"""
Provides time series types and operations
"""

import os
import sys
import types

_import_dir = os.path.abspath(".")
if not _import_dir in sys.path:
    sys.path.append(_import_dir)

import math
import warnings
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any, Callable, List, Optional, Union, cast
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import tzlocal
from pint import Unit
from pytz.exceptions import AmbiguousTimeError

import hec.hectime
import hec.parameter
import hec.unit
from hec.const import Combine, Select, SelectionState
from hec.duration import Duration
from hec.hectime import HecTime
from hec.interval import Interval
from hec.location import Location
from hec.parameter import ElevParameter, Parameter, ParameterType
from hec.quality import Quality
from hec.timespan import TimeSpan
from hec.unit import UnitQuantity

try:
    import cwms.cwms_types  # type: ignore

    cwms_imported = True
except ImportError:
    cwms_imported = False

_CWMS = "CWMS"
_DSS = "DSS"


class TimeSeriesException(Exception):
    """
    Exception specific to time series operations
    """

    pass


class TimeSeriesValue:
    """
    Holds a single time series value
    """

    def __init__(
        self,
        time: Any,
        value: Any,
        quality: Union[Quality, int] = 0,
    ):
        """
        Initializes a TimeSeriesValue object

        Args:
            time (Any): The time. Must be an HecTime object or [convertible to an HecTime object](./hectime.html#HecTime.__init__)
            value (Any): The value. Must be a UnitQuantity object or [convertible to a UnitQuantity](./unit.html#UnitQuantity.__init__) object
            quality (Union[Quality, int], optional): The quality code. Must be a Quality object or a valid quality integer. Defaults to 0.
        """
        self._time = time if isinstance(time, HecTime) else HecTime(time)
        self._value = value if isinstance(value, UnitQuantity) else UnitQuantity(value)
        self._quality = Quality(quality)

    @property
    def time(self) -> HecTime:
        """
        The time

        Operations:
            Read-Write
        """
        return self._time

    @time.setter
    def time(self, time: Any) -> None:
        self._time = time if isinstance(time, HecTime) else HecTime(time)

    @property
    def value(self) -> UnitQuantity:
        """
        The value

        Operations:
            Read-Write
        """
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        self._value = value if isinstance(value, UnitQuantity) else UnitQuantity(value)

    @property
    def quality(self) -> Quality:
        """
        The Quality

        Operations:
            Read-Write
        """
        return self._quality

    @quality.setter
    def quality(self, quality: Union[Quality, int]) -> None:
        self._quality = quality if isinstance(quality, Quality) else Quality(quality)

    def __repr__(self) -> str:
        return f"TimeSeriesValue({repr(self._time)}, {repr(self._value)}, {repr(self._quality)})"

    def __str__(self) -> str:
        return f"({str(self._time)}, {str(self.value)}, {str(self._quality)})"


class TimeSeries:
    """
    Holds time series and provides time series operations.

    ### Structure
    TimeSeries objects contain the following properties
    * `watershed` (Optional): A string that holds the the DSS A pathname part. Unused in CWMS contexts.
    * `location` (Required): A [Location](./location.html#Location) object. Its `name` property is used
        for the CWMS location identifier or DSS B pathname part.
    * `parameter` (Required): A [Parameter](./parameter.html#Parameter) object. May be an [ElevParameter](./parameter.html#ElevParameter)
        if the base parameter is "Elev", but only if there is vertical datum info. Its `name` property is
        used for the CWMS parameter identifier or DSS C pathname part.
    * `parameter_type` (Optional): A [ParameterType](./parameter.html#ParameterType) object. Its `name`
        property is used for the CWMS parameter type identifier or DSS data type
    * `interval` (Required): An [Interval](./interval.html#Interval) object. Its `name` property is used
        for the CWMS interval identier or DSS E pathname poart
    * `duration` (Optional): A [Duration](./duration.html#Durationg) object. Its `name` property is used
        for the CWMS duration identifier. Unused in DSS contexts.
    * `version` (Optional): A string that holds the CWMS version identifier or DSS F pathname part.
    * `data` (Optiona): A pandas.DataFrame object containing the time series data. The DataFrame has a DateTime index,
        a float column named "value" and a integer column named "quality"

    ### Other properties
    * `name`: The name used to initalize the object. Will be a valid CWMS time series identifier or DSS time series pathname.
    * `unit`: The unit of the parameter. Also available as the `unit_name` property of the `parameter` proerty.
    * `time_zone`: The time zone of the data or None if not set
    * `vertical_datum_info_xml`: The vertical datum info as an XML string
    * `vertical_datum_info_dict`: The vertical datum info as a dictionary
    * `times`: The times of the data values as a list of strings
    * `values`: The data values as a list of floats
    * `qualities`: The quality codes of the data values as a list of integers
    * `slice_stop_exclusive`: Controls slicing behavior

    ### Indexing and slicing
    In addition to operations available on the `data` DataFrame, TimeSeries objects may also be indexed by
    individual indexes or slices.

    The result of an index or slice operation is a copy TimeSeries object with the data as indicated in
    the index or slice.

    Indexes (single, as well as start and stop values for slices) may be one of:
    * HecTime object
    * datetime object
    * String - must be in the format yyyy&#8209;mm&#8209;dd&nbsp;hh:mm:ss([+|&#8209;]hh:mm). The time zone portion is required
        if the data times have the time zone specified
    * Integer (index into the list of data times using normal python indexing)

    Slice steps are supported and must be a positive integer value (times must always increase)

    By default, slicing follows python behavior where the stop value is exclusive (not included in the returned data).
    To use DataFrame behavior where the stop value is inclusive (returned in the data):
    * call `TimeSeries.setSliceStopInclusive()` before creating any TimeSeries objects
    * set the `slice_stop_exclusive` property to False on existing TimeSeries objects.

    Note that slicing of the `data` object will always use DataFrame behavior.
    """

    @staticmethod
    def _validIndices(df: pd.DataFrame) -> list[np.datetime64]:
        return cast(
            list[np.datetime64],
            df.index[
                ~(
                    (df["value"].isna())
                    | (np.isinf(df["value"]))
                    | (df["quality"] == 5)
                    | ((df["quality"].astype(int) & 0b1_0000) != 0)
                )
            ],
        )

    @staticmethod
    def _invalidIndices(df: pd.DataFrame) -> list[np.datetime64]:
        return cast(
            list[np.datetime64],
            df.index[
                (df["value"].isna())
                | (np.isinf(df["value"]))
                | (df["quality"] == 5)
                | ((df["quality"].astype(int) & 0b1_0000) != 0)
            ],
        )

    @staticmethod
    def _protectedIndicies(df: pd.DataFrame) -> list[np.datetime64]:
        return cast(
            list[np.datetime64],
            df[
                (
                    df["quality"].astype("int64")
                    & 0b1000_0000_0000_0000_0000_0000_0000_0000
                )
                != 0
            ].index,
        )

    @staticmethod
    def _unProtectedIndicies(df: pd.DataFrame) -> list[np.datetime64]:
        return cast(
            list[np.datetime64],
            df[
                (
                    df["quality"].astype("int64")
                    & 0b1000_0000_0000_0000_0000_0000_0000_0000
                )
                == 0
            ].index,
        )

    @staticmethod
    def aggregate_ts(
        func: Union[list[Union[Callable[[Any], Any], str]], Callable[[Any], Any], str],
        timeseries: list["TimeSeries"],
    ) -> "TimeSeries":
        """
        Generate a time series that is an aggregation of multiple time series.

        Note that some usages (marked with <sup>1</sup>, <sup>2</sup>, <sup>3</sup>, or <sup>4</sup>) generate non-standard TimeSeries results.
        In these cases the `.data` property of the TimeSeries should be used directly instead of using the `.values` property or using the
        TimeSeries in further operations.

        Args:
            func (Union[list[Union[Callable[[Any], Any], str]], Callable[[Any], Any], str]): The aggregation function(s).
            May be one of:
                <ul>
                <li><b>list[Union[Callable[[Any], Any], str]]</b><sup>1</sup>: A list comprised of items from the following two options
                (note that there is overlap between the python builtin functions and the pandas functions)
                <li><b>Callable[[Any], Any]</b>: Must take an iterable of floats and return a single value<br>
                    May be a function defined in the code (including lambda funtions) or a standard python aggregation function:
                    <ul>
                    <li><code>all</code><sup>2</sup></li>
                    <li><code>any</code><sup>2</sup></li>
                    <li><code>len</code></li>
                    <li><code>max</code></li>
                    <li><code>min</code></li>
                    <li><code>sum</code></li>
                    <li><code>math.prod</code></li>
                    <li><code>statistics.fmean</code></li>
                    <li><code>statistics.geometric_mean</code></li>
                    <li><code>statistics.harmonic_mean</code></li>
                    <li><code>statistics.mean</code></li>
                    <li><code>statistics.median</code></li>
                    <li><code>statistics.median_grouped</code></li>
                    <li><code>statistics.median_high</code></li>
                    <li><code>statistics.median_low</code></li>
                    <li><code>statistics.mode</code></li>
                    <li><code>statistics.multimode</code><sup>3</sup></li>
                    <li><code>statistics.pstdev</code></li>
                    <li><code>statistics.pvariance</code></li>
                    <li><code>statistics.quantiles</code><sup>3</sup></li>
                    <li><code>statistics.stdev</code></li>
                    <li><code>statistics.variance</code></li>
                    </ul>
                </li>
                <li><b>str</b>: Must be the name of a pandas aggregation function:
                    <ul>
                    <li><code>"all"</code><sup>2</sup></li>
                    <li><code>"any"</code><sup>2</sup></li>
                    <li><code>"count"</code></li>
                    <li><code>"describe"</code><sup>1</sup></li>
                    <li><code>"first"</code></li>
                    <li><code>"last"</code></li>
                    <li><code>"max"</code></li>
                    <li><code>"mean"</code></li>
                    <li><code>"median"</code></li>
                    <li><code>"min"</code></li>
                    <li><code>"nunique"</code></li>
                    <li><code>"prod"</code></li>
                    <li><code>"sem"</code></li>
                    <li><code>"size"</code><sup>4</sup></li>
                    <li><code>"skew"</code></li>
                    <li><code>"std"</code></li>
                    <li><code>"sum"</code></li>
                    <li><code>"var"</code></li>
                    </ul>
                </li>
                </ul>
            timeseries (list[TimeSeries]): The time series for the function to aggregate over

        <sup>1</sup>The `.data` property is a DataFrame with named columns.<br>
        <sup>2</sup>The "Values" column of the `.data` property contains bool values float values<br>
        <sup>3</sup>The "Values" column of the `.data` property contains lists of values instead of float values.<br>
        <sup>4</sup>The `.data` property is a DataFrame with one unnamed column.<br>

        Raises:
            TimeSeriesException: If less than two of the time series have data, or if the time series have
                no common times.

        Returns:
            TimeSeries: The time series that is the result of the aggregation function. The times series name will be
            modified from the first time series specified in the following way:
            * The parameter will be "Code"
            * the version will be "Aggregate"
        """
        try:
            # ----------------------------------- #
            # filter out time series without data #
            # ----------------------------------- #
            with_data = [ts for ts in timeseries if ts.data is not None]
            if len(with_data) < 2:
                raise TimeSeriesException(
                    "More that one time series with data is required"
                )
            # ------------------------------------------------------------------------------------------------- #
            # generate an index common to all time series and create a list of DataFrames with only those times #
            # ------------------------------------------------------------------------------------------------- #
            common_index = cast(pd.DataFrame, with_data[0].data).index
            for ts in with_data[1:]:
                common_index = common_index.intersection(
                    cast(pd.DataFrame, ts.data).index
                )
                if len(common_index) == 0:
                    raise TimeSeriesException("Time series do not include common times")
            common_index.name = "time"
            dfs = [cast(pd.DataFrame, ts.data).loc[common_index] for ts in with_data]
            # ---------------------------------------- #
            # generate and return a result time series #
            # ---------------------------------------- #
            ts = timeseries[0].copy(include_data=False)
            ts.ito("Code").version = "Aggregate"
            ts._data = pd.concat(dfs)[["value"]].groupby(level=0).agg(func)
            ts._data.set_index(common_index)
            ts._data["quality"] = 0
            return ts
        finally:
            for i in range(len(timeseries)):
                if timeseries[i].selection_state == SelectionState.TRANSIENT:
                    timeseries[i].select(Select.ALL)

    @staticmethod
    def percentile_ts(pct: float, timeseries: list["TimeSeries"]) -> "TimeSeries":
        """
        Computes the specified percentile of the values in the time series

        Args:
            pct (Union[tuple[float, ...], list[float], float]): The desired percentile in the range of 1..100
                or a list or tuple of such percentiles.

        Raises:
            TimeSeriesException: If the time series has no data or fewer than 2 items selected.

        Returns:
            TimeSeries: The time series of percentiles for each time. The times series name will be
            modified from the first time series specified in the following way:
            * The parameter will be "Code-Percentile"
            * the version will be "<pct>-percentile" with <pct> replaced by the pct parameter with any decimal
                point replaced with an underscore (_) character
        """
        try:
            # ----------------------------------- #
            # filter out time series without data #
            # ----------------------------------- #
            with_data = [ts for ts in timeseries if ts.data is not None]
            if len(with_data) < 2:
                raise TimeSeriesException(
                    "More that one time series with data is required"
                )
            # ------------------------------------------------------------------------------------------------- #
            # generate an index common to all time series and create a list of DataFrames with only those times #
            # ------------------------------------------------------------------------------------------------- #
            common_index = cast(pd.DataFrame, with_data[0].data).index
            for ts in with_data[1:]:
                common_index = common_index.intersection(
                    cast(pd.DataFrame, ts.data).index
                )
                if len(common_index) == 0:
                    raise TimeSeriesException("Time series do not include common times")
            common_index.name = "time"
            # ---------------------------------------- #
            # generate and return a result time series #
            # ---------------------------------------- #
            ts = timeseries[0].copy(include_data=False)
            ts.ito("Code-Percentile").version = (
                f"{str(pct).replace('.', '_')}-percentile"
            )
            ts._data = pd.DataFrame(
                {
                    "value": pd.concat(
                        [
                            (
                                cast(pd.DataFrame, ts._data).loc[
                                    cast(pd.DataFrame, ts._data)["selected"], ["value"]
                                ]
                                if ts.has_selection
                                else cast(pd.DataFrame, ts._data)["value"]
                            )
                            for ts in timeseries
                        ],
                        axis=1,
                    ).apply(lambda row: np.percentile(row.dropna(), pct), axis=1),
                    "quality": 0,
                },
                index=common_index,
            )
            return ts
        finally:
            for i in range(len(timeseries)):
                if timeseries[i].selection_state == SelectionState.TRANSIENT:
                    timeseries[i].select(Select.ALL)

    _default_slice_stop_exclusive: bool = True

    @classmethod
    def setSliceStopExclusive(cls, state: bool = True) -> None:
        """
        Set the default slicing behavior of new TimeSeries objects

        Args:
            state (bool, optional): Defaults to True.
                * `True`: python behavior (stop value is excluded)
                * `False`: DataFrame behavior (stop value is included)
        """
        cls._default_slice_stop_exclusive = state

    @classmethod
    def setSliceStopInclusive(cls, state: bool = True) -> None:
        """
        Set the default slicing behavior of new TimeSeries objects

        Args:
            state (bool, optional): Defaults to True.
                * `True`: DataFrame behavior (stop value is included)
                * `False`: python behavior (stop value is excluded)
        """
        cls._default_slice_stop_exclusive = not state

    def __init__(self, init_from: Any):
        """
        Initializes a new TimeSeries object

        Args:
            init_from (Any): The object to initialize from.
                * **str**: A CWMS time series identifier or HEC-DSS time series pathname.
                    * If CWMS
                        * The following components are set from the identifier:
                            * location (may be in the format &lt;*office*&gt;/&lt;*location*&gt; to set office)
                            * parameter
                            * parameter type
                            * interval
                            * duration
                            * version
                        * The following components are not set:
                            * watershed
                    * If HEC-DSS
                        * The following components are set from the pathname:
                            * A => watershed
                            * B => location
                            * C => parameter
                            * E => interval
                            * F => version
                        * The following compents are not set:
                            * parameter type
                            * duration
                    * The parameter unit is set to the default English unit
                    * No vertical datum information is set for elevation parameter
                * **cwms.cwms_types.Data**: A CWMS time series as returned from CDA using `cwms.get_timeseries()`
        """
        self._slice_stop_exclusive = TimeSeries._default_slice_stop_exclusive
        self._context: str
        self._watershed: Optional[str] = None
        self._location: Location
        self._parameter: Parameter
        self._parameter_type: Optional[ParameterType] = None
        self._interval: Interval
        self._duration: Optional[Duration] = None
        self._version: Optional[str] = None
        self._timezone: Optional[str] = None
        self._data: Optional[pd.DataFrame] = None
        self._midnight_as_2400: bool = False
        self._selection_state: SelectionState = SelectionState.TRANSIENT
        self._expanded = False

        if isinstance(init_from, str):
            self.name = init_from
        elif cwms_imported and isinstance(init_from, cwms.cwms_types.Data):
            self._context = _CWMS
            props = init_from.json
            df = init_from.df
            self.name = props["name"]
            self.location.office = props["office-id"]
            # props["time-zone"] is time zone of request time window, actual times are in epoch milliseconds
            self._timezone = "UTC"
            if self.parameter.base_parameter == "Elev":
                elevParam = ElevParameter(
                    self.parameter.name, props["vertical-datum-info"]
                )
                if elevParam.elevation:
                    self.location.elevation = elevParam.elevation.magnitude
                    self.location.elevation_unit = elevParam.elevation.specified_unit
                self.location.vertical_datum = elevParam.native_datum
                self.setParameter(elevParam)
            else:
                self.setParameter(Parameter(self.parameter.name, props["units"]))
            if df is not None and len(df):
                self._data = init_from.df.copy(deep=True)
                self._data.columns = ["time", "value", "quality"]
                self._data.set_index("time", inplace=True)
                self._validate()
            self.expand()
        else:
            raise TypeError(type(init_from))

    def __repr__(self) -> str:
        return f"<TimeSeries({self.name}) unit={self.parameter._unit_name} {len(self)} values>"

    def __str__(self) -> str:
        return f"{self.name} {len(self)} vlaues in {self.parameter.unit_name}"

    def __len__(self) -> int:
        if self._expanded:
            if self._data is None:
                return 0
            shape = self._data.shape
            if len(shape) == 1:
                return 1
            return shape[0]
        else:
            return len(self.expand())

    def __getitem__(self, key: Any) -> "TimeSeries":
        if self._data is None:
            raise TimeSeriesException(
                "Cannot index or slice into a TimeSeries object with no data"
            )
        other = self.copy(include_data=False)
        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
            if start:
                try:
                    start = self.indexOf(start, "next")
                except IndexError as ie:
                    if ie.args and ie.args[0] == "list index out of range":
                        stop = None
                    else:
                        raise
            if stop:
                try:
                    stop = self.indexOf(stop, "stop")
                    if self._slice_stop_exclusive:
                        t = HecTime(hec.hectime.SECOND_GRANULARITY)
                        t.set(stop)
                        stop = str(t - timedelta(seconds=1)).replace("T", " ")
                except IndexError as ie:
                    if ie.args and ie.args[0] == "list index out of range":
                        stop = None
                    else:
                        raise
            other._data = self._data.loc[start:stop:step]  # type:ignore
        else:
            other._data = cast(pd.DataFrame, self._data.loc[self.indexOf(key)])
        return other

    def __add__(
        self, amount: Union["TimeSeries", UnitQuantity, float, int]
    ) -> "TimeSeries":
        # ------------- #
        # ADD to a copy #
        # ------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if isinstance(amount, (float, int)):
            # ------------------------------------ #
            # add a unitless scalar to time series #
            # ------------------------------------ #
            other = self.copy()
            data = cast(pd.DataFrame, other._data)
            if other.has_selection:
                data.loc[data["selected"], ["value"]] += amount
                if self.selection_state == SelectionState.TRANSIENT:
                    self.iselect(Select.ALL)
            else:
                data["value"] += amount
            return other
        elif isinstance(amount, UnitQuantity):
            # --------------------------------------- #
            # add a scalar with a unit to time series #
            # --------------------------------------- #
            if UnitQuantity(1, amount.units).units.dimensionless:
                to_unit = "n/a"
            else:
                to_unit = self.unit
            return self.__add__(amount.to(to_unit).magnitude)
        elif isinstance(amount, TimeSeries):
            # ---------------------------------------#
            # add another time series to time series #
            # ---------------------------------------#
            if amount._data is None:
                raise TimeSeriesException(
                    "Operation is invalid with empty time series."
                )
            this = self._data
            if UnitQuantity(1, amount.unit).units.dimensionless:
                that = cast(pd.DataFrame, amount.to("n/a")._data)
            else:
                that = cast(pd.DataFrame, amount.to(self.unit)._data)
            other = self.copy(include_data=False)
            other._data = pd.merge(
                this[this["selected"]] if "selected" in this.columns else this,
                that[that["selected"]] if "selected" in that.columns else that,
                left_index=True,
                right_index=True,
                suffixes=("_1", "_2"),
            )
            other._data["value"] = other._data["value_1"] + other._data["value_2"]
            other._data["quality"] = 0
            other._data.drop(
                columns=["value_1", "value_2", "quality_1", "quality_2"], inplace=True
            )
            # ------------------------------ #
            # reset any transient selections #
            # ------------------------------ #
            for ts in self, amount:
                if ts.selection_state == SelectionState.TRANSIENT:
                    ts.iselect(Select.ALL)
            return other
        else:
            return NotImplemented

    def __iadd__(
        self, amount: Union["TimeSeries", UnitQuantity, float, int]
    ) -> "TimeSeries":
        # ------------ #
        # ADD in-place #
        # ------------ #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if isinstance(amount, (float, int)):
            # ------------------------------------ #
            # add a unitless scalar to time series #
            # ------------------------------------ #
            data = self._data
            if self.has_selection:
                data.loc[data["selected"], ["value"]] += amount
                if self.selection_state == SelectionState.TRANSIENT:
                    self.iselect(Select.ALL)
            else:
                data["value"] += amount
            return self
        elif isinstance(amount, UnitQuantity):
            # --------------------------------------- #
            # add a scalar with a unit to time series #
            # --------------------------------------- #
            if UnitQuantity(1, amount.units).units.dimensionless:
                to_unit = "n/a"
            else:
                to_unit = self.unit
            return self.__iadd__(amount.to(to_unit).magnitude)
        elif isinstance(amount, TimeSeries):
            # ---------------------------------------#
            # add another time series to time series #
            # ---------------------------------------#
            if amount._data is None:
                raise TimeSeriesException(
                    "Operation is invalid with empty time series."
                )
            this = self._data
            if UnitQuantity(1, amount.unit).units.dimensionless:
                that = cast(pd.DataFrame, amount.to("n/a")._data)
            else:
                that = cast(pd.DataFrame, amount.to(self.unit)._data)
            self._data = pd.merge(
                this[this["selected"]] if "selected" in this.columns else this,
                that[that["selected"]] if "selected" in that.columns else that,
                left_index=True,
                right_index=True,
                suffixes=("_1", "_2"),
            )
            self._data["value"] = self._data["value_1"] + self._data["value_2"]
            self._data["quality"] = 0
            self._data.drop(
                columns=["value_1", "value_2", "quality_1", "quality_2"], inplace=True
            )
            # ------------------------------ #
            # reset any transient selections #
            # ------------------------------ #
            for ts in self, amount:
                if ts.selection_state == SelectionState.TRANSIENT:
                    ts.iselect(Select.ALL)
            return self
        else:
            return NotImplemented

    def __sub__(
        self, amount: Union["TimeSeries", UnitQuantity, float, int]
    ) -> "TimeSeries":
        # -------------------- #
        # SUBTRACT from a copy #
        # -------------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if isinstance(amount, (float, int)):
            # ------------------------------------------- #
            # subtract a unitless scalar from time series #
            # ------------------------------------------- #
            other = self.copy()
            data = cast(pd.DataFrame, other._data)
            if other.has_selection:
                data.loc[data["selected"], ["value"]] -= amount
                if self.selection_state == SelectionState.TRANSIENT:
                    self.iselect(Select.ALL)
            else:
                data["value"] -= amount
            return other
        elif isinstance(amount, UnitQuantity):
            # ---------------------------------------------- #
            # subtract a scalar with a unit from time series #
            # ---------------------------------------------- #
            if UnitQuantity(1, amount.units).units.dimensionless:
                to_unit = "n/a"
            else:
                to_unit = self.unit
            return self.__sub__(amount.to(to_unit).magnitude)
        elif isinstance(amount, TimeSeries):
            # ----------------------------------------------#
            # subtract another time series from time series #
            # ----------------------------------------------#
            if amount._data is None:
                raise TimeSeriesException(
                    "Operation is invalid with empty time series."
                )
            this = self._data
            if UnitQuantity(1, amount.unit).units.dimensionless:
                that = cast(pd.DataFrame, amount.to("n/a")._data)
            else:
                that = cast(pd.DataFrame, amount.to(self.unit)._data)
            other = self.copy(include_data=False)
            other._data = pd.merge(
                this[this["selected"]] if "selected" in this.columns else this,
                that[that["selected"]] if "selected" in that.columns else that,
                left_index=True,
                right_index=True,
                suffixes=("_1", "_2"),
            )
            other._data["value"] = other._data["value_1"] - other._data["value_2"]
            other._data["quality"] = 0
            other._data.drop(
                columns=["value_1", "value_2", "quality_1", "quality_2"], inplace=True
            )
            # ------------------------------ #
            # reset any transient selections #
            # ------------------------------ #
            for ts in self, amount:
                if ts.selection_state == SelectionState.TRANSIENT:
                    ts.iselect(Select.ALL)
            return other
        else:
            return NotImplemented

    def __isub__(
        self, amount: Union["TimeSeries", UnitQuantity, float, int]
    ) -> "TimeSeries":
        # ----------------- #
        # SUBTRACT in-place #
        # ----------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if isinstance(amount, (float, int)):
            # ------------------------------------------- #
            # subtract a unitless scalar from time series #
            # ------------------------------------------- #
            data = self._data
            if self.has_selection:
                data.loc[data["selected"], ["value"]] -= amount
                if self.selection_state == SelectionState.TRANSIENT:
                    self.iselect(Select.ALL)
            else:
                data["value"] -= amount
            return self
        elif isinstance(amount, UnitQuantity):
            # ---------------------------------------------- #
            # subtract a scalar with a unit from time series #
            # ---------------------------------------------- #
            if UnitQuantity(1, amount.units).units.dimensionless:
                to_unit = "n/a"
            else:
                to_unit = self.unit
            return self.__isub__(amount.to(to_unit).magnitude)
        elif isinstance(amount, TimeSeries):
            # ----------------------------------------------#
            # subtract another time series from time series #
            # ----------------------------------------------#
            if amount._data is None:
                raise TimeSeriesException(
                    "Operation is invalid with empty time series."
                )
            this = self._data
            if UnitQuantity(1, amount.unit).units.dimensionless:
                that = cast(pd.DataFrame, amount.to("n/a")._data)
            else:
                that = cast(pd.DataFrame, amount.to(self.unit)._data)
            self._data = pd.merge(
                this[this["selected"]] if "selected" in this.columns else this,
                that[that["selected"]] if "selected" in that.columns else that,
                left_index=True,
                right_index=True,
                suffixes=("_1", "_2"),
            )
            self._data["value"] = self._data["value_1"] - self._data["value_2"]
            self._data["quality"] = 0
            self._data.drop(
                columns=["value_1", "value_2", "quality_1", "quality_2"], inplace=True
            )
            # ------------------------------ #
            # reset any transient selections #
            # ------------------------------ #
            for ts in self, amount:
                if ts.selection_state == SelectionState.TRANSIENT:
                    ts.iselect(Select.ALL)
            return self
        else:
            return NotImplemented

    def __mul__(
        self, amount: Union["TimeSeries", UnitQuantity, float, int]
    ) -> "TimeSeries":
        # --------------- #
        # MULTIPLY a copy #
        # --------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if isinstance(amount, (float, int)):
            # --------------------------------------- #
            # multiply time series by unitless scalar #
            # --------------------------------------- #
            other = self.copy()
            data = cast(pd.DataFrame, other._data)
            if other.has_selection:
                data.loc[data["selected"], ["value"]] *= amount
                if self.selection_state == SelectionState.TRANSIENT:
                    self.iselect(Select.ALL)
            else:
                data["value"] *= amount
            return other
        elif isinstance(amount, UnitQuantity):
            # ---------------------------------------- #
            # multiply time series by scalar with unit #
            # ---------------------------------------- #
            if UnitQuantity(1, amount.units).units.dimensionless:
                to_unit = "n/a"
                new_parameter = self.parameter
            else:
                try:
                    srcq = UnitQuantity(1, self.unit)
                    try:
                        end_unit = hec.unit.get_unit_name(
                            (srcq * UnitQuantity(1, amount.units)).units
                        )
                    except:
                        end_unit = hec.unit.get_unit_name(
                            hec.unit.get_compatible_units(
                                (srcq * UnitQuantity(1, amount.units)).units
                            )[0]
                        )
                    dstq = UnitQuantity(1, end_unit)
                    to_unit = hec.unit.get_unit_name((dstq / srcq).units)
                    new_param_name = hec.parameter.get_compatible_parameters(end_unit)[
                        0
                    ]
                    new_parameter = Parameter(new_param_name, end_unit)
                except:
                    raise TimeSeriesException(
                        f"\n==> Cannot automtically determine conversion to multiply '{self.unit}' by '{amount.units}'."
                        "\n==> Use the '.to()' method to convert one of the operands to a unit compatible with the other."
                    ) from None
            other = self.__mul__(amount.to(to_unit).magnitude)
            other.setParameter(new_parameter)
            return other
        elif isinstance(amount, TimeSeries):
            # ------------------------------------------- #
            # multiply time series by another time series #
            # ------------------------------------------- #
            if amount._data is None:
                raise TimeSeriesException(
                    "Operation is invalid with empty time series."
                )
            if UnitQuantity(1, amount.unit).units.dimensionless:
                to_unit = "n/a"
                new_parameter = self.parameter
            else:
                try:
                    srcq = UnitQuantity(1, self.unit)
                    try:
                        end_unit = hec.unit.get_unit_name(
                            (srcq * UnitQuantity(1, amount.unit)).units
                        )
                    except:
                        end_unit = hec.unit.get_unit_name(
                            hec.unit.get_compatible_units(
                                (srcq * UnitQuantity(1, amount.unit)).units
                            )[0]
                        )
                    dstq = UnitQuantity(1, end_unit)
                    to_unit = hec.unit.get_unit_name((dstq / srcq).units)
                    new_param_name = hec.parameter.get_compatible_parameters(end_unit)[
                        0
                    ]
                    new_parameter = Parameter(new_param_name, end_unit)
                except:
                    raise TimeSeriesException(
                        f"\n==> Cannot automtically determine conversion to multiply '{self.unit}' by '{amount.unit}'."
                        "\n==> Use the '.to()' method to convert one of the operands to a unit compatible with the other."
                    ) from None
            this = self._data
            that = cast(pd.DataFrame, amount.to(to_unit)._data)
            other = self.copy(include_data=False)
            other._data = pd.merge(
                this[this["selected"]] if "selected" in this.columns else this,
                that[that["selected"]] if "selected" in that.columns else that,
                left_index=True,
                right_index=True,
                suffixes=("_1", "_2"),
            )
            other._data["value"] = other._data["value_1"] * other._data["value_2"]
            other._data["quality"] = 0
            other._data.drop(
                columns=["value_1", "value_2", "quality_1", "quality_2"], inplace=True
            )
            other.setParameter(new_parameter)
            # ------------------------------ #
            # reset any transient selections #
            # ------------------------------ #
            for ts in self, amount:
                if ts.selection_state == SelectionState.TRANSIENT:
                    ts.iselect(Select.ALL)
            return other
        else:
            return NotImplemented

    def __imul__(
        self, amount: Union["TimeSeries", UnitQuantity, float, int]
    ) -> "TimeSeries":
        # ----------------- #
        # MULTIPLY in-place #
        # ----------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if isinstance(amount, (float, int)):
            # --------------------------------------- #
            # multiply time series by unitless scalar #
            # --------------------------------------- #
            data = self._data
            if self.has_selection:
                data.loc[data["selected"], ["value"]] *= amount
                if self.selection_state == SelectionState.TRANSIENT:
                    self.iselect(Select.ALL)
            else:
                data["value"] *= amount
            return self
        elif isinstance(amount, UnitQuantity):
            # ---------------------------------------- #
            # multiply time series by scalar with unit #
            # ---------------------------------------- #
            if UnitQuantity(1, amount.units).units.dimensionless:
                to_unit = "n/a"
                new_parameter = self.parameter
            else:
                try:
                    srcq = UnitQuantity(1, self.unit)
                    try:
                        end_unit = hec.unit.get_unit_name(
                            (srcq * UnitQuantity(1, amount.units)).units
                        )
                    except:
                        end_unit = hec.unit.get_unit_name(
                            hec.unit.get_compatible_units(
                                (srcq * UnitQuantity(1, amount.units)).units
                            )[0]
                        )
                    dstq = UnitQuantity(1, end_unit)
                    to_unit = hec.unit.get_unit_name((dstq / srcq).units)
                    new_param_name = hec.parameter.get_compatible_parameters(end_unit)[
                        0
                    ]
                    new_parameter = Parameter(new_param_name, end_unit)
                except:
                    raise TimeSeriesException(
                        f"\n==> Cannot automtically determine conversion to multiply '{self.unit}' by '{amount.units}'."
                        "\n==> Use the '.to()' method to convert one of the operands to a unit compatible with the other."
                    ) from None
            self.__imul__(amount.to(to_unit).magnitude)
            self.setParameter(new_parameter)
            return self
        elif isinstance(amount, TimeSeries):
            # ------------------------------------------- #
            # multiply time series by another time series #
            # ------------------------------------------- #
            if amount._data is None:
                raise TimeSeriesException(
                    "Operation is invalid with empty time series."
                )
            if UnitQuantity(1, amount.unit).units.dimensionless:
                to_unit = "n/a"
                new_parameter = self.parameter
            else:
                try:
                    srcq = UnitQuantity(1, self.unit)
                    try:
                        end_unit = hec.unit.get_unit_name(
                            (srcq * UnitQuantity(1, amount.unit)).units
                        )
                    except:
                        end_unit = hec.unit.get_unit_name(
                            hec.unit.get_compatible_units(
                                (srcq * UnitQuantity(1, amount.unit)).units
                            )[0]
                        )
                    dstq = UnitQuantity(1, end_unit)
                    to_unit = hec.unit.get_unit_name((dstq / srcq).units)
                    new_param_name = hec.parameter.get_compatible_parameters(end_unit)[
                        0
                    ]
                    new_parameter = Parameter(new_param_name, end_unit)
                except:
                    raise TimeSeriesException(
                        f"\n==> Cannot automtically determine conversion to multiply '{self.unit}' by '{amount.unit}'."
                        "\n==> Use the '.to()' method to convert one of the operands to a unit compatible with the other."
                    ) from None
            this = self._data
            that = cast(pd.DataFrame, amount.to(to_unit)._data)
            self._data = pd.merge(
                this[this["selected"]] if "selected" in this.columns else this,
                that[that["selected"]] if "selected" in that.columns else that,
                left_index=True,
                right_index=True,
                suffixes=("_1", "_2"),
            )
            self._data["value"] = self._data["value_1"] * self._data["value_2"]
            self._data["quality"] = 0
            self._data.drop(
                columns=["value_1", "value_2", "quality_1", "quality_2"], inplace=True
            )
            # ------------------------------ #
            # reset any transient selections #
            # ------------------------------ #
            self.setParameter(new_parameter)
            for ts in self, amount:
                if ts.selection_state == SelectionState.TRANSIENT:
                    ts.iselect(Select.ALL)
            return self
        else:
            return NotImplemented

    def __truediv__(
        self, amount: Union["TimeSeries", UnitQuantity, float, int]
    ) -> "TimeSeries":
        # ------------- #
        # DIVIDE a copy #
        # ------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if isinstance(amount, (float, int)):
            # ------------------------------------- #
            # divide time series by unitless scalar #
            # ------------------------------------- #
            other = self.copy()
            data = cast(pd.DataFrame, other._data)
            if other.has_selection:
                data.loc[data["selected"], ["value"]] /= amount
                if self.selection_state == SelectionState.TRANSIENT:
                    self.iselect(Select.ALL)
            else:
                data["value"] /= amount
            return other
        elif isinstance(amount, UnitQuantity):
            # -------------------------------------- #
            # divide time series by scalar with unit #
            # -------------------------------------- #
            if UnitQuantity(1, amount.units).units.dimensionless:
                to_unit = "n/a"
                new_parameter = self.parameter
            else:
                try:
                    srcq = UnitQuantity(1, self.unit)
                    try:
                        end_unit = hec.unit.get_unit_name(
                            (srcq / UnitQuantity(1, amount.units)).units
                        )
                    except:
                        end_unit = hec.unit.get_unit_name(
                            hec.unit.get_compatible_units(
                                (srcq / UnitQuantity(1, amount.units)).units
                            )[0]
                        )
                    dstq = UnitQuantity(1, end_unit)
                    to_unit = hec.unit.get_unit_name((srcq / dstq).units)
                    new_param_name = hec.parameter.get_compatible_parameters(end_unit)[
                        0
                    ]
                    new_parameter = Parameter(new_param_name, end_unit)
                except:
                    raise TimeSeriesException(
                        f"\n==> Cannot automtically determine conversion to divide '{self.unit}' by '{amount.units}'."
                        "\n==> Use the '.to()' method to convert one of the operands to a unit compatible with the other."
                    ) from None
            other = self.__truediv__(amount.to(to_unit).magnitude)
            other.setParameter(new_parameter)
            return other
        elif isinstance(amount, TimeSeries):
            # ----------------------------------------- #
            # divide time series by another time series #
            # ----------------------------------------- #
            if amount._data is None:
                raise TimeSeriesException(
                    "Operation is invalid with empty time series."
                )
            if UnitQuantity(1, amount.unit).units.dimensionless:
                to_unit = "n/a"
                new_parameter = self.parameter
            else:
                try:
                    srcq = UnitQuantity(1, str(UnitQuantity(1, self.unit).units))
                    try:
                        end_unit = hec.unit.get_unit_name(
                            (srcq / UnitQuantity(1, amount.unit)).units
                        )
                    except:
                        end_unit = hec.unit.get_unit_name(
                            hec.unit.get_compatible_units(
                                (srcq / UnitQuantity(1, amount.unit)).units
                            )[0]
                        )
                    dstq = UnitQuantity(1, str(UnitQuantity(1, end_unit).units))
                    to_unit = hec.unit.get_unit_name((srcq / dstq).units)
                    new_param_name = hec.parameter.get_compatible_parameters(end_unit)[
                        0
                    ]
                    new_parameter = Parameter(new_param_name, end_unit)
                except:
                    raise TimeSeriesException(
                        f"\n==> Cannot automtically determine conversion to divide '{self.unit}' by '{amount.unit}'."
                        "\n==> Use the '.to()' method to convert one of the operands to a unit compatible with the other."
                    ) from None
            this = self._data
            that = cast(pd.DataFrame, amount.to(to_unit)._data)
            other = self.copy(include_data=False)
            other._data = pd.merge(
                this[this["selected"]] if "selected" in this.columns else this,
                that[that["selected"]] if "selected" in that.columns else that,
                left_index=True,
                right_index=True,
                suffixes=("_1", "_2"),
            )
            other._data["value"] = other._data["value_1"] / other._data["value_2"]
            other._data["quality"] = 0
            other._data.drop(
                columns=["value_1", "value_2", "quality_1", "quality_2"], inplace=True
            )
            other.setParameter(new_parameter)
            # ------------------------------ #
            # reset any transient selections #
            # ------------------------------ #
            for ts in self, amount:
                if ts.selection_state == SelectionState.TRANSIENT:
                    ts.iselect(Select.ALL)
            return other
        else:
            return NotImplemented

    def __itruediv__(
        self, amount: Union["TimeSeries", UnitQuantity, float, int]
    ) -> "TimeSeries":
        # --------------- #
        # DIVIDE in-place #
        # --------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if isinstance(amount, (float, int)):
            # ------------------------------------- #
            # divide time series by unitless scalar #
            # ------------------------------------- #
            data = self._data
            if self.has_selection:
                data.loc[data["selected"], ["value"]] /= amount
                if self.selection_state == SelectionState.TRANSIENT:
                    self.iselect(Select.ALL)
            else:
                data["value"] /= amount
            return self
        elif isinstance(amount, UnitQuantity):
            # -------------------------------------- #
            # divide time series by scalar with unit #
            # -------------------------------------- #
            if UnitQuantity(1, amount.units).units.dimensionless:
                to_unit = "n/a"
                new_parameter = self.parameter
            else:
                try:
                    srcq = UnitQuantity(1, self.unit)
                    try:
                        end_unit = hec.unit.get_unit_name(
                            (srcq / UnitQuantity(1, amount.units)).units
                        )
                    except:
                        end_unit = hec.unit.get_unit_name(
                            hec.unit.get_compatible_units(
                                (srcq / UnitQuantity(1, amount.units)).units
                            )[0]
                        )
                    dstq = UnitQuantity(1, end_unit)
                    to_unit = hec.unit.get_unit_name((srcq / dstq).units)
                    new_param_name = hec.parameter.get_compatible_parameters(end_unit)[
                        0
                    ]
                    new_parameter = Parameter(new_param_name, end_unit)
                except:
                    raise TimeSeriesException(
                        f"\n==> Cannot automtically determine conversion to divide '{self.unit}' by '{amount.units}'."
                        "\n==> Use the '.to()' method to convert one of the operands to a unit compatible with the other."
                    ) from None
            self.__itruediv__(amount.to(to_unit).magnitude)
            self.setParameter(new_parameter)
            return self
        elif isinstance(amount, TimeSeries):
            # ----------------------------------------- #
            # divide time series by another time series #
            # ----------------------------------------- #
            if amount._data is None:
                raise TimeSeriesException(
                    "Operation is invalid with empty time series."
                )
            if UnitQuantity(1, amount.unit).units.dimensionless:
                to_unit = "n/a"
                new_parameter = self.parameter
            else:
                try:
                    srcq = UnitQuantity(1, self.unit)
                    try:
                        end_unit = hec.unit.get_unit_name(
                            (srcq / UnitQuantity(1, amount.unit)).units
                        )
                    except:
                        end_unit = hec.unit.get_unit_name(
                            hec.unit.get_compatible_units(
                                (srcq / UnitQuantity(1, amount.unit)).units
                            )[0]
                        )
                    dstq = UnitQuantity(1, end_unit)
                    to_unit = hec.unit.get_unit_name((srcq / dstq).units)
                    new_param_name = hec.parameter.get_compatible_parameters(end_unit)[
                        0
                    ]
                    new_parameter = Parameter(new_param_name, end_unit)
                except:
                    raise TimeSeriesException(
                        f"\n==> Cannot automtically determine conversion to divide '{self.unit}' by '{amount.unit}'."
                        "\n==> Use the '.to()' method to convert one of the operands to a unit compatible with the other."
                    ) from None
            this = self._data
            that = cast(pd.DataFrame, amount.to(to_unit)._data)
            self._data = pd.merge(
                this[this["selected"]] if "selected" in this.columns else this,
                that[that["selected"]] if "selected" in that.columns else that,
                left_index=True,
                right_index=True,
                suffixes=("_1", "_2"),
            )
            self._data["value"] = self._data["value_1"] / self._data["value_2"]
            self._data["quality"] = 0
            self._data.drop(
                columns=["value_1", "value_2", "quality_1", "quality_2"], inplace=True
            )
            self.setParameter(new_parameter)
            # ------------------------------ #
            # reset any transient selections #
            # ------------------------------ #
            for ts in self, amount:
                if ts.selection_state == SelectionState.TRANSIENT:
                    ts.iselect(Select.ALL)
            return self
        else:
            return NotImplemented

    def __floordiv__(
        self, amount: Union["TimeSeries", UnitQuantity, float, int]
    ) -> "TimeSeries":
        # --------------------- #
        # INTEGER DIVIDE a copy #
        # --------------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if isinstance(amount, (float, int)):
            # ------------------------------------- #
            # divide time series by unitless scalar #
            # ------------------------------------- #
            other = self.copy()
            data = cast(pd.DataFrame, other._data)
            if other.has_selection:
                data.loc[data["selected"], ["value"]] //= amount
                if self.selection_state == SelectionState.TRANSIENT:
                    self.iselect(Select.ALL)
            else:
                data["value"] //= amount
            return other
        elif isinstance(amount, UnitQuantity):
            # -------------------------------------- #
            # divide time series by scalar with unit #
            # -------------------------------------- #
            if UnitQuantity(1, amount.units).units.dimensionless:
                to_unit = "n/a"
                new_parameter = self.parameter
            else:
                try:
                    srcq = UnitQuantity(1, self.unit)
                    try:
                        end_unit = hec.unit.get_unit_name(
                            (srcq / UnitQuantity(1, amount.units)).units
                        )
                    except:
                        end_unit = hec.unit.get_unit_name(
                            hec.unit.get_compatible_units(
                                (srcq / UnitQuantity(1, amount.units)).units
                            )[0]
                        )
                    dstq = UnitQuantity(1, end_unit)
                    to_unit = hec.unit.get_unit_name((srcq / dstq).units)
                    new_param_name = hec.parameter.get_compatible_parameters(end_unit)[
                        0
                    ]
                    new_parameter = Parameter(new_param_name, end_unit)
                except:
                    raise TimeSeriesException(
                        f"\n==> Cannot automtically determine conversion to divide '{self.unit}' by '{amount.units}'."
                        "\n==> Use the '.to()' method to convert one of the operands to a unit compatible with the other."
                    ) from None
            other = self.__floordiv__(amount.to(to_unit).magnitude)
            other.setParameter(new_parameter)
            return other
        elif isinstance(amount, TimeSeries):
            # ----------------------------------------- #
            # divide time series by another time series #
            # ----------------------------------------- #
            if amount._data is None:
                raise TimeSeriesException(
                    "Operation is invalid with empty time series."
                )
            if UnitQuantity(1, amount.unit).units.dimensionless:
                to_unit = "n/a"
                new_parameter = self.parameter
            else:
                try:
                    srcq = UnitQuantity(1, self.unit)
                    try:
                        end_unit = hec.unit.get_unit_name(
                            (srcq / UnitQuantity(1, amount.unit)).units
                        )
                    except:
                        end_unit = hec.unit.get_unit_name(
                            hec.unit.get_compatible_units(
                                (srcq / UnitQuantity(1, amount.unit)).units
                            )[0]
                        )
                    dstq = UnitQuantity(1, end_unit)
                    to_unit = hec.unit.get_unit_name((srcq / dstq).units)
                    new_param_name = hec.parameter.get_compatible_parameters(end_unit)[
                        0
                    ]
                    new_parameter = Parameter(new_param_name, end_unit)
                except:
                    raise TimeSeriesException(
                        f"\n==> Cannot automtically determine conversion to divide '{self.unit}' by '{amount.unit}'."
                        "\n==> Use the '.to()' method to convert one of the operands to a unit compatible with the other."
                    ) from None
            this = self._data
            that = cast(pd.DataFrame, amount.to(to_unit)._data)
            other = self.copy(include_data=False)
            other._data = pd.merge(
                this[this["selected"]] if "selected" in this.columns else this,
                that[that["selected"]] if "selected" in that.columns else that,
                left_index=True,
                right_index=True,
                suffixes=("_1", "_2"),
            )
            other._data["value"] = other._data["value_1"] // other._data["value_2"]
            other._data["quality"] = 0
            other._data.drop(
                columns=["value_1", "value_2", "quality_1", "quality_2"], inplace=True
            )
            other.setParameter(new_parameter)
            # ------------------------------ #
            # reset any transient selections #
            # ------------------------------ #
            for ts in self, amount:
                if ts.selection_state == SelectionState.TRANSIENT:
                    ts.iselect(Select.ALL)
            return other
        else:
            return NotImplemented

    def __ifloordiv__(
        self, amount: Union["TimeSeries", UnitQuantity, float, int]
    ) -> "TimeSeries":
        # ----------------------- #
        # INTEGER DIVIDE in-place #
        # ----------------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if isinstance(amount, (float, int)):
            # ------------------------------------- #
            # divide time series by unitless scalar #
            # ------------------------------------- #
            data = self._data
            if self.has_selection:
                data.loc[data["selected"], ["value"]] //= amount
                if self.selection_state == SelectionState.TRANSIENT:
                    self.iselect(Select.ALL)
            else:
                data["value"] //= amount
            return self
        elif isinstance(amount, UnitQuantity):
            # -------------------------------------- #
            # divide time series by scalar with unit #
            # -------------------------------------- #
            if UnitQuantity(1, amount.units).units.dimensionless:
                to_unit = "n/a"
                new_parameter = self.parameter
            else:
                try:
                    srcq = UnitQuantity(1, self.unit)
                    try:
                        end_unit = hec.unit.get_unit_name(
                            (srcq / UnitQuantity(1, amount.units)).units
                        )
                    except:
                        end_unit = hec.unit.get_unit_name(
                            hec.unit.get_compatible_units(
                                (srcq / UnitQuantity(1, amount.units)).units
                            )[0]
                        )
                    dstq = UnitQuantity(1, end_unit)
                    to_unit = hec.unit.get_unit_name((srcq / dstq).units)
                    new_param_name = hec.parameter.get_compatible_parameters(end_unit)[
                        0
                    ]
                    new_parameter = Parameter(new_param_name, end_unit)
                except:
                    raise TimeSeriesException(
                        f"\n==> Cannot automtically determine conversion to divide '{self.unit}' by '{amount.units}'."
                        "\n==> Use the '.to()' method to convert one of the operands to a unit compatible with the other."
                    ) from None
            self.__ifloordiv__(amount.to(to_unit).magnitude)
            self.setParameter(new_parameter)
            return self
        elif isinstance(amount, TimeSeries):
            # ----------------------------------------- #
            # divide time series by another time series #
            # ----------------------------------------- #
            if amount._data is None:
                raise TimeSeriesException(
                    "Operation is invalid with empty time series."
                )
            if UnitQuantity(1, amount.unit).units.dimensionless:
                to_unit = "n/a"
                new_parameter = self.parameter
            else:
                try:
                    srcq = UnitQuantity(1, self.unit)
                    try:
                        end_unit = hec.unit.get_unit_name(
                            (srcq / UnitQuantity(1, amount.unit)).units
                        )
                    except:
                        end_unit = hec.unit.get_unit_name(
                            hec.unit.get_compatible_units(
                                (srcq / UnitQuantity(1, amount.unit)).units
                            )[0]
                        )
                    dstq = UnitQuantity(1, end_unit)
                    to_unit = hec.unit.get_unit_name((srcq / dstq).units)
                    new_param_name = hec.parameter.get_compatible_parameters(end_unit)[
                        0
                    ]
                    new_parameter = Parameter(new_param_name, end_unit)
                except:
                    raise TimeSeriesException(
                        f"\n==> Cannot automtically determine conversion to divide '{self.unit}' by '{amount.unit}'."
                        "\n==> Use the '.to()' method to convert one of the operands to a unit compatible with the other."
                    ) from None
            this = self._data
            that = cast(pd.DataFrame, amount.to(to_unit)._data)
            self._data = pd.merge(
                this[this["selected"]] if "selected" in this.columns else this,
                that[that["selected"]] if "selected" in that.columns else that,
                left_index=True,
                right_index=True,
                suffixes=("_1", "_2"),
            )
            self._data["value"] = self._data["value_1"] // self._data["value_2"]
            self._data["quality"] = 0
            self._data.drop(
                columns=["value_1", "value_2", "quality_1", "quality_2"], inplace=True
            )
            self.setParameter(new_parameter)
            # ------------------------------ #
            # reset any transient selections #
            # ------------------------------ #
            for ts in self, amount:
                if ts.selection_state == SelectionState.TRANSIENT:
                    ts.iselect(Select.ALL)
            return self
        else:
            return NotImplemented

    def __mod__(
        self, amount: Union["TimeSeries", UnitQuantity, float, int]
    ) -> "TimeSeries":
        # ---------------- #
        # MODULO of a copy #
        # ---------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if isinstance(amount, (float, int)):
            # -------------------------------------- #
            # mod time series with a unitless scalar #
            # -------------------------------------- #
            other = self.copy()
            data = cast(pd.DataFrame, other._data)
            if other.has_selection:
                data.loc[data["selected"], ["value"]] %= amount
                if self.selection_state == SelectionState.TRANSIENT:
                    self.iselect(Select.ALL)
            else:
                data["value"] %= amount
            return other
        elif isinstance(amount, UnitQuantity):
            # --------------------------------------- #
            # mod time series with a scalar with unit #
            # --------------------------------------- #
            if UnitQuantity(1, amount.units).units.dimensionless:
                to_unit = "n/a"
            else:
                to_unit = self.unit
            return self.__mod__(amount.to(to_unit).magnitude)
        elif isinstance(amount, TimeSeries):
            # ---------------------------------------- #
            # mod time series with another time series #
            # ---------------------------------------- #
            if amount._data is None:
                raise TimeSeriesException(
                    "Operation is invalid with empty time series."
                )
            this = self._data
            if UnitQuantity(1, amount.unit).units.dimensionless:
                that = cast(pd.DataFrame, amount.to("n/a")._data)
            else:
                that = cast(pd.DataFrame, amount.to(self.unit)._data)
            other = self.copy(include_data=False)
            other._data = pd.merge(
                this[this["selected"]] if "selected" in this.columns else this,
                that[that["selected"]] if "selected" in that.columns else that,
                left_index=True,
                right_index=True,
                suffixes=("_1", "_2"),
            )
            other._data["value"] = other._data["value_1"] % other._data["value_2"]
            other._data["quality"] = 0
            other._data.drop(
                columns=["value_1", "value_2", "quality_1", "quality_2"], inplace=True
            )
            # ------------------------------ #
            # reset any transient selections #
            # ------------------------------ #
            for ts in self, amount:
                if ts.selection_state == SelectionState.TRANSIENT:
                    ts.iselect(Select.ALL)
            return other
        else:
            return NotImplemented

    def __imod__(
        self, amount: Union["TimeSeries", UnitQuantity, float, int]
    ) -> "TimeSeries":
        # --------------- #
        # MODULO in-place #
        # --------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if isinstance(amount, (float, int)):
            # -------------------------------------- #
            # mod time series with a unitless scalar #
            # -------------------------------------- #
            data = self._data
            if self.has_selection:
                data.loc[data["selected"], ["value"]] %= amount
                if self.selection_state == SelectionState.TRANSIENT:
                    self.iselect(Select.ALL)
            else:
                data["value"] %= amount
            return self
        elif isinstance(amount, UnitQuantity):
            # --------------------------------------- #
            # mod time series with a scalar with unit #
            # --------------------------------------- #
            if UnitQuantity(1, amount.units).units.dimensionless:
                to_unit = "n/a"
            else:
                to_unit = self.unit
            return self.__imod__(amount.to(to_unit).magnitude)
        elif isinstance(amount, TimeSeries):
            # ---------------------------------------- #
            # mod time series with another time series #
            # ---------------------------------------- #
            if amount._data is None:
                raise TimeSeriesException(
                    "Operation is invalid with empty time series."
                )
            this = self._data
            if UnitQuantity(1, amount.unit).units.dimensionless:
                that = cast(pd.DataFrame, amount.to("n/a")._data)
            else:
                that = cast(pd.DataFrame, amount.to(self.unit)._data)
            self._data = pd.merge(
                this[this["selected"]] if "selected" in this.columns else this,
                that[that["selected"]] if "selected" in that.columns else that,
                left_index=True,
                right_index=True,
                suffixes=("_1", "_2"),
            )
            self._data["value"] = self._data["value_1"] % self._data["value_2"]
            self._data["quality"] = 0
            self._data.drop(
                columns=["value_1", "value_2", "quality_1", "quality_2"], inplace=True
            )
            # ------------------------------ #
            # reset any transient selections #
            # ------------------------------ #
            for ts in self, amount:
                if ts.selection_state == SelectionState.TRANSIENT:
                    ts.iselect(Select.ALL)
            return self
        else:
            return NotImplemented

    def __pow__(
        self, amount: Union["TimeSeries", UnitQuantity, float, int]
    ) -> "TimeSeries":
        # ----------------------- #
        # RAISE a copy to a power #
        # ----------------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if isinstance(amount, (float, int)):
            # ------------------------------------ #
            # raise time series by unitless scalar #
            # ------------------------------------ #
            other = self.copy()
            data = cast(pd.DataFrame, other._data)
            if other.has_selection:
                data.loc[data["selected"], ["value"]] **= amount
                if self.selection_state == SelectionState.TRANSIENT:
                    self.iselect(Select.ALL)
            else:
                data["value"] **= amount
            return other
        elif isinstance(amount, UnitQuantity):
            # ------------------------------------- #
            # raise time series by scalar with unit #
            # ONLY dimensionless units are allowed  #
            # ------------------------------------- #
            other = self.__pow__(amount.to("n/a").magnitude)
            return other
        elif isinstance(amount, TimeSeries):
            # ---------------------------------------- #
            # raise time series by another time series #
            # ONLY dimensionless units are allowed     #
            # ---------------------------------------- #
            if amount._data is None:
                raise TimeSeriesException(
                    "Operation is invalid with empty time series."
                )
            this = self._data
            that = cast(pd.DataFrame, amount.to("n/a")._data)
            other = self.copy(include_data=False)
            other._data = pd.merge(
                this[this["selected"]] if "selected" in this.columns else this,
                that[that["selected"]] if "selected" in that.columns else that,
                left_index=True,
                right_index=True,
                suffixes=("_1", "_2"),
            )
            other._data["value"] = other._data["value_1"] ** other._data["value_2"]
            other._data["quality"] = 0
            other._data.drop(
                columns=["value_1", "value_2", "quality_1", "quality_2"], inplace=True
            )
            # ------------------------------ #
            # reset any transient selections #
            # ------------------------------ #
            for ts in self, amount:
                if ts.selection_state == SelectionState.TRANSIENT:
                    ts.iselect(Select.ALL)
            return other
        else:
            return NotImplemented

    def __ipow__(
        self, amount: Union["TimeSeries", UnitQuantity, float, int]
    ) -> "TimeSeries":
        # ------------------------- #
        # RAISE to a power in-place #
        # ------------------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if isinstance(amount, (float, int)):
            # ------------------------------------ #
            # raise time series by unitless scalar #
            # ------------------------------------ #
            data = self._data
            if self.has_selection:
                data.loc[data["selected"], ["value"]] **= amount
                if self.selection_state == SelectionState.TRANSIENT:
                    self.iselect(Select.ALL)
            else:
                data["value"] **= amount
            return self
        elif isinstance(amount, UnitQuantity):
            # ------------------------------------- #
            # raise time series by scalar with unit #
            # ONLY dimensionless units are allowed  #
            # ------------------------------------- #
            self.__ipow__(amount.to("n/a").magnitude)
            return self
        elif isinstance(amount, TimeSeries):
            # ---------------------------------------- #
            # raise time series by another time series #
            # ONLY dimensionless units are allowed     #
            # ---------------------------------------- #
            if amount._data is None:
                raise TimeSeriesException(
                    "Operation is invalid with empty time series."
                )
            this = self._data
            that = cast(pd.DataFrame, amount.to("n/a")._data)
            self._data = pd.merge(
                this[this["selected"]] if "selected" in this.columns else this,
                that[that["selected"]] if "selected" in that.columns else that,
                left_index=True,
                right_index=True,
                suffixes=("_1", "_2"),
            )
            self._data["value"] = self._data["value_1"] ** self._data["value_2"]
            self._data["quality"] = 0
            self._data.drop(
                columns=["value_1", "value_2", "quality_1", "quality_2"], inplace=True
            )
            # ------------------------------ #
            # reset any transient selections #
            # ------------------------------ #
            for ts in self, amount:
                if ts.selection_state == SelectionState.TRANSIENT:
                    ts.iselect(Select.ALL)
            return self
        else:
            return NotImplemented

    def __neg__(self) -> "TimeSeries":
        # ------------- #
        # NEGATE a copy #
        # ------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        other = self.copy()
        data = cast(pd.DataFrame, other._data)
        if other.has_selection:
            data.loc[data["selected"], ["value"]] *= -1
            if self.selection_state == SelectionState.TRANSIENT:
                self.iselect(Select.ALL)
        else:
            data["value"] *= -1
        return other

    def __lshift__(self, amount: Union[TimeSpan, timedelta, int]) -> "TimeSeries":
        # ---------------------------- #
        # SHIFT a copy EARLIER in time #
        # ---------------------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        other: TimeSeries = self.copy()
        if isinstance(amount, (TimeSpan)):
            offset = amount
        elif isinstance(amount, timedelta):
            offset = TimeSpan(amount)
        elif isinstance(amount, int):
            if self._interval.is_irregular:
                raise TimeSeriesException(
                    "Cannot shift an irregular interval time series by an integer value"
                )
            offset = amount * self._interval
        times = list(map(HecTime, self.times))
        times2 = []
        for i in range(len(times)):
            times[i].midnight_as_2400 = False
            times[i] -= offset
            times2.append(times[i].datetime())
        cast(pd.DataFrame, other._data).index = pd.DatetimeIndex(times2)
        cast(pd.DataFrame, other._data).index.name = "time"
        return other

    def __ilshift__(self, amount: Union[TimeSpan, timedelta, int]) -> "TimeSeries":
        # ------------------------------ #
        # SHIFT EARLIER in time in-place #
        # ------------------------------ #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if isinstance(amount, (TimeSpan)):
            offset = amount
        elif isinstance(amount, timedelta):
            offset = TimeSpan(amount)
        elif isinstance(amount, int):
            if self._interval.is_irregular:
                raise TimeSeriesException(
                    "Cannot shift an irregular interval time series by an integer value"
                )
            offset = amount * self._interval
        times = list(map(HecTime, self.times))
        times2 = []
        for i in range(len(times)):
            times[i].midnight_as_2400 = False
            times[i] -= offset
            times2.append(times[i].datetime())
        self._data.index = pd.DatetimeIndex(times2)
        self._data.index.name = "time"
        return self

    def __rshift__(self, amount: Union[TimeSpan, timedelta, int]) -> "TimeSeries":
        # -------------------------- #
        # SHIFT a copy LATER in time #
        # -------------------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        other: TimeSeries = self.copy()
        if isinstance(amount, (TimeSpan)):
            offset = amount
        elif isinstance(amount, timedelta):
            offset = TimeSpan(amount)
        elif isinstance(amount, int):
            if self._interval.is_irregular:
                raise TimeSeriesException(
                    "Cannot shift an irregular interval time series by an integer value"
                )
            offset = amount * self._interval
        times = list(map(HecTime, self.times))
        times2 = []
        for i in range(len(times)):
            times[i].midnight_as_2400 = False
            times[i] += offset
            times2.append(times[i].datetime())
        cast(pd.DataFrame, other._data).index = pd.DatetimeIndex(times2)
        cast(pd.DataFrame, other._data).index.name = "time"
        return other

    def __irshift__(self, amount: Union[TimeSpan, timedelta, int]) -> "TimeSeries":
        # ---------------------------- #
        # SHIFT LATER in time in-place #
        # ---------------------------- #
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if isinstance(amount, (TimeSpan)):
            offset = amount
        elif isinstance(amount, timedelta):
            offset = TimeSpan(amount)
        elif isinstance(amount, int):
            if self._interval.is_irregular:
                raise TimeSeriesException(
                    "Cannot shift an irregular interval time series by an integer value"
                )
            offset = amount * self._interval
        times = list(map(HecTime, self.times))
        times2 = []
        for i in range(len(times)):
            times[i].midnight_as_2400 = False
            times[i] += offset
            times2.append(times[i].datetime())
        self._data.index = pd.DatetimeIndex(times2)
        self._data.index.name = "time"
        return self

    def _validate(self) -> None:
        # ------------------------------- #
        # validate times against interval #
        # ------------------------------- #
        if len(self) < 2:
            return
        if self.is_any_regular:
            timeStrings = self.times
            if self.is_local_regular:
                timeStrings = list(
                    map(lambda s: s[:19], timeStrings)
                )  # remove any time zone info
            lasttime = HecTime(timeStrings[0])
            for i in range(1, len(self)):
                thistime = HecTime(timeStrings[i])
                while thistime > lasttime:
                    lasttime += self.interval
                if lasttime > thistime:
                    raise TimeSeriesException(
                        f"Times do not match interval of {self.interval.name}"
                    )

    def _tsv(self, row: pd.DataFrame) -> Any:
        # --------------------------------------------- #
        # create a TimeSeriesValue from a DataFrame row #
        # --------------------------------------------- #
        return cast(
            Any,
            TimeSeriesValue(
                row.name,
                UnitQuantity(row.value, self.unit),
                cast(Union[Quality, int], int(row.quality)),
            ),
        )

    def to(
        self,
        unit_parameter_or_datum: Union[str, Unit, Parameter],
        in_place: bool = False,
    ) -> "TimeSeries":
        """
        Converts this object - or a copy of this object - to another unit, parameter, or vertical datum

        Args:
            unit_parameter_or_datum (Union[str, Unit, Parameter]): The unit, parameter or vertical datum to convert to
            in_place (bool, optional): Whether to convert this object (True) or a copy of this object (False).
                Defaults to False.

        Raises:
            TimeSeriesException: If setting the vertical datum on a non Elev parameter or an Elev parameter
                without vertical datum information

        Returns:
            TimeSeries: The converted object
        """
        target = self if in_place else self.copy()
        if isinstance(
            unit_parameter_or_datum, str
        ) and hec.parameter._all_datums_pattern.match(unit_parameter_or_datum):
            # ----------------- #
            # to vertical datum #
            # ----------------- #
            if isinstance(target.parameter, ElevParameter):
                offset = target.parameter.get_offset_to(unit_parameter_or_datum)
                if offset:
                    offset.ito(self.unit)
                    target.parameter.ito(unit_parameter_or_datum)
                    if target._data is not None:
                        target._data["value"] += offset.magnitude
            elif target.parameter.base_parameter == "Elev":
                raise TimeSeriesException(
                    f"Cannot set vertical datum on {self.parameter.name} time series that has no vetical datum information"
                )
            else:
                raise TimeSeriesException(
                    f"Cannot set vertical datum on {self.parameter.name} time series"
                )
            return target
        param: Optional[Parameter] = None
        from_unit = target.unit
        to_unit: Union[Unit, str]
        if isinstance(unit_parameter_or_datum, Parameter):
            param = unit_parameter_or_datum
        elif isinstance(unit_parameter_or_datum, str):
            try:
                param = Parameter(unit_parameter_or_datum)
            except:
                pass
        if param is not None:
            # ------------ #
            # to parameter #
            # ------------ #
            to_unit = param.unit_name
            target.setParameter(param)
        else:
            to_unit = cast(Union[Unit, str], unit_parameter_or_datum)
            target.setUnit(to_unit)
        # ------- #
        # to unit #
        # ------- #
        if target._data is not None:
            conv_1 = hec.unit.convert_units(1, from_unit, to_unit)
            conv_10 = hec.unit.convert_units(10, from_unit, to_unit)
            if conv_10 == 10 * conv_1:
                # --------------- #
                # constant factor #
                # --------------- #
                target._data["value"] *= conv_1
            elif (conv_10 - 10) == (conv_1 - 1):
                # --------------- #
                # constant offset #
                # --------------- #
                target._data["value"] += conv_1 - 1
            else:
                # --------------------------------- #
                # need to apply conversion per item #
                # --------------------------------- #
                target._data.loc[:, "value"] = target._data.apply(
                    lambda v: hec.unit.convert_units(v, from_unit, to_unit)
                )
        return target

    def ito(self, unit_parameter_or_datum: Union[str, Unit, Parameter]) -> "TimeSeries":
        """
        Converts this object to another unit, parameter or vertical datum.

        Identical to calling ts.to(..., True)

        Args:
            unit_parameter_or_datum (Union[str, Unit, Parameter]): The unit, parameter or vertical datum to convert to

        Raises:
            TimeSeriesException: If setting the vertical datum on a non Elev parameter or an Elev parameter
                without vertical datum information

        Returns:
            TimeSeries: The converted object
        """
        return self.to(unit_parameter_or_datum, True)

    def select(
        self,
        selection: Union[Select, int, slice, Callable[[TimeSeriesValue], bool]],
        combination: Combine = Combine.REPLACE,
        in_place: bool = False,
    ) -> "TimeSeries":
        """
        Marks individual items in this object - or a copy of this object - as selected for pariticpation the next operation,
        either directly or by combining each item's current selected state with the result of a function.
        On creation the selection is cleared (i.e., every item is selected)

        This object's selection_state property determines the selection of this object after the next operation:
        * `SelectionState.TRANSIENT`: (default) The selection will be cleared after the next operation.
        * `SelectionState.DURABLE`: The selection will remain until explicitly changed by a call to iselect()

        Args:
            selection (Union[Select, int, slice, Callable[[TimeSeriesValue], bool]]): One of the following:
                * `Select.NONE`: Marks all items as unselected. Any `combination` is ignored.
                * `Select.ALL`: Marks all items as selected. Any `combination` is ignored.
                * `Select.INVERT`: Inverts the current selected state of each item. Any `combination` is ignored.
                * integer: An integer offset from the beginning of the time series
                * `HecTime` object: single item matching specified time
                * datetime object: single item matching specified time
                * string convertible to HecTime object: : single item matching specified time
                * slice: One or more items.
                    * The start parameter (if specified) and stop parameter may be:
                        * integers - offsets from the first value in the time series
                        * `HecTime` objects
                        * datetime objects
                        * strings convertible to HecTime objects
                    * The step parameter must be an integer, if specified
                * function: A function that takes a single `TimeSeriesValue` parameter and returns a bool result.
                    An item is marked as selected if and only if the result of the function is True for the item (when combined with the current state if necessary).
            combination (Combine, optional): Specifies how to combine the function result with an item's current selected state.
                Used when `selection` is not one of eh `Select` values. Defaults to Combine.REPLACE.
                * `Combine.REPLACE`: Current selected state of each item is ignored and is replaced by the result of the function.
                * `Combine.AND`: Current selected state of each item is ANDed with the result of the function to generate new selected state.
                * `Combine.OR`: Current selected state of each items is ORed with the result of the function to generate new selected state.
                * `Combine.XOR`: Current selected state of each item is XORed with the result of the function to generate new selected state.
            in_place (bool, optional): Specifies whether to mark itmes in this object (True) or a copy of this object (False). Defaults to False.

        Raises:
            TimeSeriesException: If this object has no data
            ValueError: If an invalid selection or combination is specified.

        Returns:
            TimeSeries: The marked object
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        target = self if in_place else self.copy()
        data = cast(pd.DataFrame, target._data)
        if isinstance(selection, Select):
            # ---------------- #
            # direct selection #
            # ---------------- #
            if selection == Select.NONE:
                data.assign(selected=False)
            elif selection == Select.ALL:
                if "selected" in data.columns:
                    data.drop(columns=["selected"], inplace=True)
            elif selection == Select.INVERT:
                if "selected" in data.columns:
                    data.loc[:, "selected"] = data.loc[:, "selected"] != True
                else:
                    data.assign(selected=False)
            elif selection == Combine.NOOP:
                pass
            else:
                raise ValueError(f"Invalid selection: {selection}")
        elif isinstance(selection, int):
            # --------------------- #
            # selection via integer #
            # --------------------- #
            func = (
                lambda tsv: target.formatTimeForIndex(tsv.time)
                in target.__getitem__(slice(selection, selection + 1)).times
            )
            return target.iselect(func, combination)
        elif isinstance(selection, HecTime):
            # --------------------- #
            # selection via HecTime #
            # --------------------- #
            func = lambda tsv: target.formatTimeForIndex(
                tsv.time
            ) == target.formatTimeForIndex(selection)
            return target.iselect(func, combination)
        elif isinstance(selection, (str, datetime)):
            # -------------------------------- #
            # selection via string or datetime #
            # -------------------------------- #
            func = lambda tsv: target.formatTimeForIndex(
                tsv.time
            ) == target.formatTimeForIndex(HecTime(selection))
            return target.iselect(func, combination)
        elif isinstance(selection, slice):
            # ------------------- #
            # selection via slice #
            # ------------------- #
            func = (
                lambda tsv: target.formatTimeForIndex(tsv.time)
                in target.__getitem__(selection).times
            )
            return target.iselect(func, combination)
        elif type(selection) == types.FunctionType:
            # ---------------------- #
            # selection via function #
            # ---------------------- #
            func = selection
            if combination == Combine.REPLACE:
                data.loc[:, "selected"] = data.apply(
                    lambda row: func(self._tsv(row)),
                    axis=1,
                )
            elif combination == Combine.AND:
                if "selected" in cast(pd.DataFrame, target._data).columns:
                    data.loc[:, "selected"] = data.apply(
                        lambda row: row["selected"] and func(self._tsv(row)),
                        axis=1,
                    )
                else:
                    data.loc[:, "selected"] = data.apply(
                        lambda row: func(self._tsv(row)),
                        axis=1,
                    )
            elif combination == Combine.OR:
                if "selected" in cast(pd.DataFrame, target._data).columns:
                    data.loc[:, "selected"] = data.apply(
                        lambda row: row["selected"] or func(self._tsv(row)),
                        axis=1,
                    )
                else:
                    pass
            elif combination == Combine.XOR:
                if "selected" in cast(pd.DataFrame, target._data).columns:
                    data.loc[:, "selected"] = data.apply(
                        lambda row: (row["selected"] or func(self._tsv(row)))
                        and not (row["selected"] and func(self._tsv(row))),
                        axis=1,
                    )
                else:
                    data.loc[:, "selected"] = data.apply(
                        lambda row: not func(self._tsv(row)),
                        axis=1,
                    )
            else:
                raise ValueError(f"Invalid combination: {combination}")
        else:
            raise TypeError(
                f"Invalid type for 'selection' parameter: {type(selection)}"
            )
        return target

    def iselect(
        self,
        selection: Union[Select, int, slice, Callable[[TimeSeriesValue], bool]],
        combination: Combine = Combine.REPLACE,
    ) -> "TimeSeries":
        """
        Marks individual items in this objectas selected for pariticpation the next operation,
        either directly or by combining each item's current selected state with the result of a function.
        On creation the selection is cleared (i.e., every item is selected)

        This object's selection_state property determines the selection of this object after the next operation:
        * `SelectionState.TRANSIENT`: (default) The selection will be cleared after the next operation.
        * `SelectionState.DURABLE`: The selection will remain until explicitly changed by a call to iselect()

        Args:
            selection (Union[Select, int, slice, Callable[[TimeSeriesValue], bool]]): One of the following:
                * `Select.NONE`: Marks all items as unselected. Any `combination` is ignored.
                * `Select.ALL`: Marks all items as selected. Any `combination` is ignored.
                * `Select.INVERT`: Inverts the current selected state of each item. Any `combination` is ignored.
                * integer: An integer offset from the beginning of the time series
                * `HecTime` object: single item matching specified time
                * datetime object: single item matching specified time
                * string convertible to HecTime object: : single item matching specified time
                * slice: One or more items.
                    * The start parameter (if specified) and stop parameter may be:
                        * integers - offsets from the first value in the time series
                        * `HecTime` objects
                        * datetime objects
                        * strings convertible to HecTime objects
                    * The step parameter must be an integer, if specified
                * function: A function that takes a single `TimeSeriesValue` parameter and returns a bool result.
                    An item is marked as selected if and only if the result of the function is True for the item (when combined with the current state if necessary).
            combination (Combine, optional): Specifies how to combine the function result with an item's current selected state.
                Used when `selection` is not one of eh `Select` values. Defaults to Combine.REPLACE.
                * `Combine.REPLACE`: Current selected state of each item is ignored and is replaced by the result of the function.
                * `Combine.AND`: Current selected state of each item is ANDed with the result of the function to generate new selected state.
                * `Combine.OR`: Current selected state of each items is ORed with the result of the function to generate new selected state.
                * `Combine.XOR`: Current selected state of each item is XORed with the result of the function to generate new selected state.

        Raises:
            TimeSeriesException: If this object has no data
            ValueError: If an invalid selection or combination is specified.

        Returns:
            TimeSeries: The marked object
        """
        return self.select(selection, combination, in_place=True)

    def isValid(self, index: Union[int, str, datetime, HecTime]) -> bool:
        """
        Returns whether the index is in the time series and the value at the index is valid

        Args:
            index (Union[int, str, datetime, HecTime]): The index to test.

        Returns:
            bool: False if any of the following are true, otherwise True:
            * The time series does not contain the index
            * The quality is MISSING
            * The quality is REJECTED
            * The value is NaN
            * The value is Infinite
        """
        if not isinstance(index, (int, str, datetime, HecTime)):
            raise TypeError(
                f"Expected int, str, datetime, or HecTime, got {type(index)}"
            )
        try:
            df = self[index].data
            if df is None:
                return False
            if math.isnan(df.value) or math.isinf(df.value):
                return False
            if df.quality & 0b0_0101 or df.quality & 0b1_0001:
                return False
            return True
        except:
            return False

    def selectValid(self, in_place: bool = False) -> "TimeSeries":
        """
        Marks individual items in this object - or a copy of this object - as selected for pariticpation the next operation based on whether
        the items are valid. Items are valid unless any of the following are true:
        * The quality is MISSING
        * The quality is REJECTED
        * The value is NaN
        * The value is Infinite

        This selection replaces any other selection - if it is to be combined with other selection criteria
        it must be performed before the other criteria


        This object's selection_state property indicates/determines whether the selection is cleared af the next operation (via
        an automatic ts.select(Select.NONE)) or maintained until explicitly modified.

        Args:
            in_place (bool, optional): Specifies whether to mark itmes in this object (True) or a copy of this object (False). Defaults to False.

        Raises:
            TimeSeriesException: If this object has no data

        Returns:
            TimeSeries: The marked object
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        target = self if in_place else self.copy()
        data = cast(pd.DataFrame, target._data)
        data.loc[:, "selected"] = data.index.isin(TimeSeries._validIndices(data))
        return target

    def iselectValid(self) -> "TimeSeries":
        """
        Marks individual items in this object as selected for pariticpation the next operation based on whether
        the items are valid. Items are valid unless any of the following are true:
        * The quality is MISSING
        * The quality is REJECTED
        * The value is NaN
        * The value is Infinite

        This object's selection_state property indicates/determines whether the selection is cleared af the next operation (via
        an automatic ts.select(Select.ALL)) or maintained until explicitly modified.

        Identical to calling ts.selectAll(in_place=True)

        Raises:
            TimeSeriesException: If this object has no data

        Returns:
            TimeSeries: The marked object
        """
        self.selectValid(in_place=True)
        return self

    def map(
        self, func: Callable[[float], float], in_place: bool = False
    ) -> "TimeSeries":
        """
        Applies a function of one variable to the values of this object and returns the modified object

        Args:
            func (Callable): The function of one variable to apply to the values
            in_place (bool, optional): Specifies whether to operate on this object (True)
                or a copy of this object (False). Defaults to False.

        Returns:
            TimeSeries: Either this object (modified) or a modified copy of this object.
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        target = self if in_place else self.copy()
        cast(pd.DataFrame, target._data)["value"] = cast(pd.DataFrame, target._data)[
            "value"
        ].map(func)
        return target

    def imap(self, func: Callable[[float], float]) -> "TimeSeries":
        """
        Modifies this object by applying a function of one variable to the values, and returns the modified object.

        Identical to calling [.apply(func, True)](#Timeseries.apply)

        Args:
            func (Callable): The function of one variable to apply to the values

        Returns:
            TimeSeries: This object (modified)
        """
        return self.map(func, in_place=True)

    def indexOf(
        self,
        item_to_index: Union[HecTime, datetime, int, str],
        not_found: Optional[str] = None,
    ) -> str:
        """
        Retrieves the data index of a specified object

        Args:
            item_to_index (Union[HecTime, datetime, int, str]): The object to retrieve the index of.
                * **HecTime**: an HecTime object
                * **datetime**:  a datetime object
                * **int**: a normal python index
                * **str**: a date-time string
            not_found (Optional[str]): Specifies the behavior if `item_to_index` is not in the index:
                * 'next': return the higher of the bounding indices of the item
                * 'previous': return the lower of the bounding indices of the item
                * 'stop': used for the stop index of slices - return the lower of the bounding indices plus one (unless beyond end)
                * None (default): raise an IndexError

        Raises:
            TimeSeriesException: If the time series has no values, or if `not_found` is specifed and is not "next" "previous", or "stop"
            TypeError: If `item_to_index` is not one of the expected types
            IndexError:
                * **int**: If the integer is out of range of the number of times
                * **Others**: If no index item matches the input object

        Returns:
            str: The actual index item that for the specified object
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if not_found and not_found not in ("next", "previous", "stop"):
            raise TimeSeriesException(
                'Parameter not_found must be None, "next", "previous", or "stop"'
            )
        times = self.times
        idx = None
        try:
            if isinstance(item_to_index, (HecTime, datetime, str)):
                ht = HecTime(item_to_index)
                ht.midnight_as_2400 = False
                key = str(ht).replace("T", " ")
                if not_found is None:
                    idx = times.index(key)
                else:
                    try:
                        idx = times.index(key)
                    except:
                        if not_found == "next":
                            for i in range(len(times)):
                                if times[i] > key:
                                    idx = i
                                    break
                            else:
                                raise
                        elif not_found == "previous":
                            for i in range(len(times))[::-1]:
                                if times[i] < key:
                                    idx = i
                                    break
                            else:
                                raise
                        elif not_found == "stop":
                            for i in range(len(times))[::-1]:
                                if times[i] < key:
                                    idx = i
                                    if idx < len(times) - 1:
                                        idx += 1
                                    break
                            else:
                                raise
            elif isinstance(item_to_index, int):
                idx = item_to_index
                if idx < 0 and not_found == "next":
                    idx = 0
                if idx >= len(times) and not_found == "previous":
                    idx = len(times) - 1
            else:
                raise TypeError(
                    f"Expected HecTime, datetime, str, or int. Got {type(item_to_index)}"
                )
        except TypeError:
            raise
        except:
            if not_found == "next":
                raise IndexError(
                    f"{item_to_index} is not in times and no next time was found"
                )
            if not_found == "previous":
                raise IndexError(
                    f"{item_to_index} is not in times and no previous time was found"
                )
            raise IndexError(f"{item_to_index} is not in times")
        assert idx is not None
        return times[idx]

    @property
    def slice_stop_exclusive(self) -> bool:
        """
        Whether the `stop` portion of `[start:stop]` slicing is exclusive for this object.
        * If `True`, the slicing TimeSeries objects follows Python rules, where `stop`
            specifies the lowest index not included.
        * If `False`, the slicing of TimeSeries objects follows pandas.DataFrame rules,
            where `stop` specifies the highest index included.

        The default value is determined by the class state, which defaults to `True`, but
        can be set by calling [setSliceStartExclusive()](#TimeSeries.setSliceStartExclusive) or
        [setSliceStartInclusive()](#TimeSeries.setSliceStartInclusive) before creating a
        TimeSeries object

        Operations:
            Read/Write
        """
        return self._slice_stop_exclusive

    @slice_stop_exclusive.setter
    def slice_stop_exclusive(self, state: bool) -> None:
        self._slice_stop_exclusive = state

    @property
    def name(self) -> str:
        """
        The CWMS time series identifier or HEC-DSS pathname

        Operations:
            Read/Write
        """
        parts = []
        if self._context == _CWMS:
            parts.append(str(self._location))
            parts.append(self._parameter.name)
            parts.append(cast(ParameterType, self._parameter_type).getCwmsName())
            parts.append(self._interval.name)
            parts.append(cast(Duration, self._duration).name)
            parts.append(cast(str, self._version))
            return ".".join(parts)
        elif self._context == _DSS:
            parts.append("")
            parts.append("")
            parts.append(self._location.name)
            parts.append(self._parameter.name)
            parts.append("")
            parts.append(self._interval.name)
            parts.append(self._version if self._version else "")
            parts.append("")
            return "/".join(parts)
        else:
            raise TimeSeriesException(f"Invalid context: {self._context}")

    @name.setter
    def name(self, value: str) -> None:
        try:
            parts = value.split(".")
            if len(parts) == 6:
                self._context = _CWMS
                self.setLocation(parts[0])
                self.setParameter(parts[1])
                self.setParameterType(parts[2])
                self.setInterval(parts[3])
                self.setDuration(parts[4])
                self.version = parts[5]
            else:
                parts = value.split("/")
                if len(parts) == 8:
                    A, B, C, E, F = 1, 2, 3, 5, 6
                    self._context = _DSS
                    self.watershed = parts[A]
                    self.setLocation(parts[B])
                    self.setParameter(parts[C])
                    self.setInterval(parts[E])
                    self.version = parts[F]
                else:
                    raise TimeSeriesException(
                        "Expected valid CWMS time series identifier or HEC-DSS time series pathname"
                    )
            if not self._location:
                raise TimeSeriesException("Location must be specified")
            if not self._parameter:
                raise TimeSeriesException("Parameter must be specified")
            if not self._parameter_type and self._context == _CWMS:
                raise TimeSeriesException("Parameter type must be specified")
            if not self._interval:
                raise TimeSeriesException("Interval must be specified")
            if not self._duration and self._context == _CWMS:
                raise TimeSeriesException("Duration must be specified")
            if not self._version and self._context == _CWMS:
                raise TimeSeriesException("Version must be specified")

        except Exception as e:
            raise TimeSeriesException(
                f"Invalid time series name: '{value}':\n{type(e)}: {' '.join(e.args)}"
            )

    @property
    def watershed(self) -> Optional[str]:
        """
        The watershed (DSS A pathname part)

        Operations:
            Read Only
        """
        return self._watershed

    @watershed.setter
    def watershed(self, value: str) -> None:
        self._watershed = value

    @property
    def location(self) -> Location:
        """
        The location object (used in HEC-DSS B pathname part)

        Operations:
            Read Only
        """
        return self._location

    @property
    def parameter(self) -> Parameter:
        """
        The parameter object (used in HEC-DSS C pathname part)

        Operations:
            Read Only
        """
        return self._parameter

    @property
    def parameter_type(self) -> Optional[ParameterType]:
        """
        The parameter type object

        Operations:
            Read Only
        """
        return self._parameter_type

    @property
    def interval(self) -> Interval:
        """
        The interval object (used in HEC-DSS E pathname part)

        Operations:
            Read Only
        """
        return self._interval

    @property
    def duration(self) -> Optional[Duration]:
        """
        The duration object

        Operations:
            Read Only
        """
        return self._duration

    @property
    def version(self) -> Optional[str]:
        """
        The version (HEC-DSS F pathname part)

        Operations:
            Read/Write
        """
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        self._version = value

    @property
    def time_zone(self) -> Optional[str]:
        """
        The time zone of the data

        Operations:
            Read Only
        """
        return self._timezone

    @property
    def unit(self) -> str:
        """
        The parameter unit object

        Operations:
            Read Only
        """
        return self._parameter.unit_name

    @property
    def is_regular(self) -> bool:
        """
        Specifies whether the time series is a normal regular time series

        Operations:
            Read Only
        """
        return self.interval.is_regular

    @property
    def is_local_regular(self) -> bool:
        """
        Specifies whether the time series is a local regular time series

        Operations:
            Read Only
        """
        return self.interval.is_local_regular

    @property
    def is_any_regular(self) -> bool:
        """
        Specifies whether the time series is a normal regular or local regular time series

        Operations:
            Read Only
        """
        return self.interval.is_any_regular

    @property
    def is_irregular(self) -> bool:
        """
        Specifies whether the time series is a normal irregular time series

        Operations:
            Read Only
        """
        return self.interval.is_irregular

    @property
    def is_pseudo_regular(self) -> bool:
        """
        Specifies whether the time series is a normal irregular or pseudo-regular time series

        Operations:
            Read Only
        """
        return self.interval.is_pseudo_regular

    @property
    def is_any_irregular(self) -> bool:
        """
        Specifies whether the time series is a normal irregular or pseudo-regular time series

        Operations:
            Read Only
        """
        return self.interval.is_any_irregular

    @property
    def vertical_datum_info(self) -> Optional[ElevParameter._VerticalDatumInfo]:
        """
        The vertical datum info object or None if not set

        Operations:
            Read Only
        """
        if isinstance(self._parameter, ElevParameter):
            return self._parameter.vertical_datum_info
        else:
            return None

    @property
    def vertical_datum_info_xml(self) -> Optional[str]:
        """
        The vertical datum info as an XML string or None if not set

        Operations:
            Read Only
        """
        if (
            isinstance(self._parameter, ElevParameter)
            and self._parameter.vertical_datum_info
        ):
            return self._parameter.vertical_datum_info_xml
        else:
            return None

    @property
    def vertical_datum_info_dict(self) -> Optional[dict[str, Any]]:
        """
        The vertical datum info as a dictionary or None if not set

        Operations:
            Read Only
        """
        if (
            isinstance(self._parameter, ElevParameter)
            and self._parameter.vertical_datum_info
        ):
            return self._parameter.vertical_datum_info_dict
        else:
            return None

    @property
    def data(self) -> Optional[pd.DataFrame]:
        """
        The data as a DataFrame or None if not set. Note this exposes the interal DataFrame object to
        allow direct modification. For uses that should not modify this TimeSeries object, the DataFrame
        should be copied using its `copy()` method prior to modification (e.g., `df = ts.data.copy()`)

        Operations:
            Read Only
        """
        return self._data

    @property
    def times(self) -> list[str]:
        """
        The times as a list of strings (empty if there is no data). Items are formatted as yyyy&#8209;mm&#8209;dd&nbsp;hh:mm:ss([+|&#8209;]hh:mm)

        Operations:
            Read Only
        """
        if self._data is None:
            return []
        if len(self._data.shape) == 1:
            timestr = self._data.name.strftime("%Y-%m-%d %H:%M:%S%z")
            if timestr[-5] in "-+":
                timestr = f"{timestr[:-2]}:{timestr[-2:]}"
            return timestr
        return list(map(self.formatTimeForIndex, self._data.index.tolist()))

    @property
    def values(self) -> list[float]:
        """
        The values as a list of floats (empty if there is no data)

        Operations:
            Read Only
        """
        return [] if self._data is None else self._data["value"].tolist()

    @property
    def qualities(self) -> list[int]:
        """
        The qualities as a list of integers (empty if there is no data)

        Operations:
            Read Only
        """
        return [] if self._data is None else self._data["quality"].tolist()

    @property
    def tsv(self) -> list[TimeSeriesValue]:
        """
        The times, values, and qualities as a list of TimeSeriesValue objects (empty if there is no data)

        Operations:
            Read Only
        """
        if self._data is None:
            return []
        if len(self._data.shape) == 1:
            return [
                TimeSeriesValue(
                    self._data.name,
                    UnitQuantity(self._data.value, self.unit),
                    self._data.quality,
                )
            ]

        def func(tsv: TimeSeriesValue) -> Any:
            return tsv

        return cast(
            list[TimeSeriesValue],
            (
                pd.DataFrame(self._data)
                .apply(
                    lambda row: func(self._tsv(row)),
                    axis=1,
                )
                .tolist()
            ),
        )

    @property
    def midnight_as_2400(self) -> bool:
        """
        The object's current setting of whether to show midnight as hour 24 (default) or not.

        Operations:
            Read/Write
        """
        return self._midnight_as_2400

    @midnight_as_2400.setter
    def midnight_as_2400(self, state: bool) -> None:
        self._midnight_as_2400 = state

    @property
    def has_selection(self) -> bool:
        """
        Whether the object has a current selection specified

        Operations:
            Read Only
        """
        return self._data is not None and "selected" in self._data.columns

    @property
    def selected(self) -> list[bool]:
        """
        The current selection (empty if all items are selected)

        Operations:
            Read Only
        """
        return (
            []
            if self._data is None or "selected" not in self._data.columns
            else self._data["selected"].tolist()
        )

    @property
    def selection_state(self) -> SelectionState:
        """
        The persistence state of selections in this object.

        The default selection_state of [SelectionState.TRANSIENT](./const.html#SelectionState)

        Operations:
            Read/Write
        """
        return self._selection_state

    @selection_state.setter
    def selection_state(self, period: SelectionState) -> None:
        self._selection_state = period

    def setLocation(self, value: Union[Location, str]) -> "TimeSeries":
        """
        Sets the location for the time series

        Args:
            value (Union[Location, str]):
                * Location: The Location object to use
                * str: The location name (may be in the format &lt;*office*&gt;/&lt;*location*&gt; to set office)

        Returns:
            TimeSeries: The modified object
        """
        if isinstance(value, Location):
            self._location = value
        else:
            if self._context == _CWMS:
                try:
                    office, location = value.split("/")
                    self._location = Location(location, office)
                except:
                    self._location = Location(value)
            elif self._context == _DSS:
                self._location = Location(value)
            else:
                raise TimeSeriesException(f"Invalid context: {self._context}")
        return self

    def formatTimeForIndex(self, item: Union[HecTime, datetime, str]) -> str:
        """
        Formats a time item for indexing into the times of this object. The formatting depends on
        the setting of this object's [`mindnight_as_2400`](#TimeSeries.midnight_as_2400) property

        Args:
            item (Union[HecTime, datetime, str]): The time item to format.

        Returns:
            str: The formatted string with the midnight setting of this object
        """
        ht = HecTime()
        ht.set(item)
        ht.midnight_as_2400 = self.midnight_as_2400
        return str(ht).replace("T", " ")

    def setParameter(self, value: Union[Parameter, str]) -> "TimeSeries":
        """
        Sets the parameter for the time series

        Args:
            value (Union[Parameter, str]):
                * Parameter: The Parameter object to use
                * str: The parameter name - the unit will be set to the default English unit

        Returns:
            TimeSeries: The modified object
        """
        if isinstance(value, Parameter):
            self._parameter = value
        else:
            self._parameter = Parameter(value, "EN")
        return self

    def setParameterType(self, value: Union[ParameterType, str]) -> "TimeSeries":
        """
        Sets the parameter type for the time series

        Args:
            value (Union[ParameterType, str]):
                * ParameterType: The ParameterType object to use
                * str: The parameter type name

        Returns:
            TimeSeries: The modified object
        """
        if isinstance(value, ParameterType):
            self._parameter_type = value
        else:
            self._parameter_type = ParameterType(value)
        return self

    def setInterval(self, value: Union[Interval, str, int]) -> "TimeSeries":
        """
        Sets the interval for the time series

        Args:
            value (Union[Interval, str]):
                * Interval: The Interval object to use
                * str: The interval name
                * int: The (actual or characteristic) number of minutes for the interval

        Returns:
            TimeSeries: The modified object
        """
        if isinstance(value, Interval):
            self._interval = value
        else:
            if self._context == _CWMS:
                self._interval = Interval.getCwms(value)
            else:
                self._interval = Interval.getDss(value)
        return self

    def setDuration(self, value: Union[Duration, str, int]) -> "TimeSeries":
        """
        Sets the Duration for the time series

        Args:
            value (Union[Duration, str]):
                * Interval: The Duration object to use
                * str: The duration name
                * int: The (actual or characteristic) number of minutes for the duration

        Returns:
            TimeSeries: The modified object
        """
        if isinstance(value, Duration):
            self._duration = value
        else:
            self._duration = Duration.forInterval(value)
        return self

    def setUnit(self, value: Union[Unit, str]) -> "TimeSeries":
        """
        Sets the parameter unit for the time series.

        **NOTE**: This does *not* modify any data values. Use the [ito()](#TimeSeries.ito) method
        to modify data, which also sets the unit.

        Args:
            value (Union[Unit, str]):
                <ul>
                <li>Unit: The Unit object or name to use</li>
                <li>str: The unit name</li>
                </ul>

        Returns:
            TimeSeries: The modified object
        """
        if isinstance(value, Unit):
            if self._parameter.unit.dimensionality != Unit.dimensionality:
                raise TimeSeriesException(
                    f"Cannont set unit of {self._parameter.name} time series to {value}"
                )
            self._parameter._unit = value
            self._parameter._unit_name = eval(
                f"f'{{{value}:{UnitQuantity._default_output_format}}}'"
            )
        else:
            self._parameter.to(value, in_place=True)
        return self

    def setVerticalDatumInfo(self, value: Union[str, dict[str, Any]]) -> "TimeSeries":
        """
        Sets the vertical datum info for the time series

        Args:
            value (Union[str, dict[str, Any]]):
                <ul>
                <li>str: the vertical datum info as an XML string
                <li>dict: the vertical datum info as a dictionary</li>
                </ul>

        Raises:
            TimeSeriesException: If the base parameter is not "Elev"

        Returns:
            TimeSeries: The modified object
        """
        if self._parameter.base_parameter == "Elev":
            self._parameter = ElevParameter(self._parameter.name, value)
        else:
            raise TimeSeriesException(
                f"Cannot set vertical datum on {self._parameter.name} time series"
            )
        return self

    def copy(self, include_data: bool = True) -> "TimeSeries":
        """
        Creates a copy of this object, with or without data

        Args:
            include_data (bool, optional): Specifies whether to include the data in the copy. Defaults to True.

        Returns:
            TimeSeries: The copy of this object
        """
        other = TimeSeries(self.name)
        other._location = deepcopy(self._location)
        other._parameter = deepcopy(self._parameter)
        other._parameter_type = deepcopy(self._parameter_type)
        other._interval = deepcopy(self._interval)
        other._duration = deepcopy(self._duration)
        other._version = self._version
        other._timezone = self._timezone
        if include_data and self._data is not None:
            other._data = self._data.copy()
            other._expanded = self._expanded
        return other

    def setValue(self, value: float, in_place: bool = False) -> "TimeSeries":
        """
        Sets the value of selected items of this object or a copy of this object

        Args:
            value (float): The value to set for selected items
            in_place (bool): Specifies whether to set the values in this object
                (True) or a copy of this object (False)

        Returns:
            TimeSeries: The modified object
        """
        target = self if in_place else self.copy()
        data = cast(pd.DataFrame, target._data)
        if target.has_selection:
            data.loc[data["selected"], ["value"]] = value
            if self.selection_state == SelectionState.TRANSIENT:
                self.iselect(Select.ALL)
        else:
            data["value"] = value
        return target

    def isetValue(self, value: float) -> "TimeSeries":
        """
        Sets the value of selected items of this object.

        Identical to calling .setValue(..., True)

        Args:
            value (float): The value to set for selected items

        Returns:
            TimeSeries: The modified object
        """
        return self.setValue(value, True)

    def setQuality(
        self, quality: Union[Quality, int], in_place: bool = False
    ) -> "TimeSeries":
        """
        Sets the quality of selected items of this object or a copy of this object

        Args:
            quality: Union[Quality, int]: The quality to set for selected items
            in_place (bool): Specifies whether to set the values in this object
                (True) or a copy of this object (False)

        Returns:
            TimeSeries: The modified object
        """
        target = self if in_place else self.copy()
        data = cast(pd.DataFrame, target._data)
        if target.has_selection:
            data.loc[data["selected"], ["quality"]] = Quality(quality).code
            if self.selection_state == SelectionState.TRANSIENT:
                self.iselect(Select.ALL)
        else:
            data["quality"] = Quality(quality).code
        return target

    def isetQuality(self, quality: Union[Quality, int]) -> "TimeSeries":
        """
        Sets the quality of selected items of this object.

        Identical to calling .setQuality(..., True)

        Args:
            quality: Union[Quality, int]: The quality to set for selected items

        Returns:
            TimeSeries: The modified object
        """
        return self.setQuality(quality, True)

    def setValueQuality(
        self, value: float, quality: Union[Quality, int], in_place: bool = False
    ) -> "TimeSeries":
        """
        Sets the value and quality of selected items of this object or a copy of this object

        Args:
            value (float): The value to set for selected items
            quality: Union[Quality, int]: The quality to set for selected items
            in_place (bool): Specifies whether to set the values in this object
                (True) or a copy of this object (False)

        Returns:
            TimeSeries: The modified object
        """
        target = self if in_place else self.copy()
        data = cast(pd.DataFrame, target._data)
        if target.has_selection:
            data.loc[data["selected"], ["value"]] = value
            data.loc[data["selected"], ["quality"]] = Quality(quality).code
            if self.selection_state == SelectionState.TRANSIENT:
                self.iselect(Select.ALL)
        else:
            data["value"] = value
            data["quality"] = Quality(quality).code
        return target

    def isetValueQuality(
        self, value: float, quality: Union[Quality, int]
    ) -> "TimeSeries":
        """
        Sets the value and quality of selected items of this object

        Identical to calling .setValueQuality(..., True)

        Args:
            value (float): The value to set for selected items
            quality: Union[Quality, int]: The quality to set for selected items

        Returns:
            TimeSeries: The modified object
        """
        return self.setValueQuality(value, quality, True)

    def atTimeZone(
        self,
        timeZone: Optional[Union["HecTime", datetime, ZoneInfo, str]],
        onAlreadytSet: int = 1,
    ) -> "TimeSeries":
        """
        Attaches the specified time zone to this object. Does not change the actual times

        Args:
            timeZone (Optional[Union["HecTime", datetime, ZoneInfo, str]]): The time zone to attach or
                object containing that time zone.
                * Use `"local"` to specify the system time zone.
                * Use `None` to remove time zone information
            onAlreadytSet (int): Specifies action to take if a different time zone is already
                attached. Defaults to 1.
                - `0`: Quietly attach the new time zone
                - `1`: (default) Issue a warning about attaching a different time zone
                - `2`: Raises an exception
        Raises:
            TimeSeriesException: if a different time zone is already attached and `onAlreadySet` == 2

        Returns:
            TimeSeries: The modified object
        """
        if isinstance(timeZone, HecTime):
            tz = timeZone._tz
        elif isinstance(timeZone, datetime):
            tz = timeZone.tzinfo
        elif isinstance(timeZone, (ZoneInfo, type(None))):
            tz = timeZone
        else:
            tz = (
                tzlocal.get_localzone()
                if timeZone.lower() == "local"
                else ZoneInfo(timeZone)
            )
        if self._timezone:
            if tz == ZoneInfo(self._timezone):
                return self
            if tz is None:
                if self._data is not None:
                    self._data = self._data.tz_localize(None)
                self._timezone = None
            else:
                if onAlreadytSet > 0:
                    message = f"{repr(self)} already has a time zone set to {self._timezone} when setting to {tz}"
                    if onAlreadytSet > 1:
                        raise TimeSeriesException(message)
                    else:
                        warnings.warn(
                            message + ". Use onAlreadySet=0 to prevent this message.",
                            UserWarning,
                        )
                if self._data is not None:
                    self._data = self._data.tz_localize(None)
                    self._data = self._data.tz_localize(str(tz))
                self._timezone = str(timeZone)
        else:
            if tz:
                if self._data is not None:
                    self._data = self._data.tz_localize(str(tz))
                self._timezone = str(tz)
        return self

    def asTimeZone(
        self, timeZone: Union["HecTime", datetime, ZoneInfo, str], onTzNotSet: int = 1
    ) -> "TimeSeries":
        """
        Returns a copy of this object at the spcified time zone

        Args:
            timeZone (Union[HecTime, datetime, ZoneInfo, str]): The target time zone or object containg the target time zone.
                Use `"local"` to specify the system time zone.
            onTzNotSet (int, optional): Specifies behavior if this object has no time zone attached. Defaults to 1.
                - `0`: Quietly behave as if this object had the local time zone attached.
                - `1`: (default) Same as `0`, but issue a warning.
                - `2`: Raise an exception preventing objectes with out time zones attached from using this method.

        Returns:
            TimeSeries: A copy of this object at the specified time zone
        """
        if isinstance(timeZone, HecTime):
            tz = timeZone._tz
        elif isinstance(timeZone, datetime):
            tz = timeZone.tzinfo
        elif isinstance(timeZone, ZoneInfo):
            tz = timeZone
        else:
            tz = (
                tzlocal.get_localzone()
                if timeZone.lower() == "local"
                else ZoneInfo(timeZone)
            )
        if self._data is not None:
            if self._timezone:
                self._data = self._data.tz_convert(str(tz))
            else:
                try:
                    self._data = self._data.tz_localize(
                        str(tz), ambiguous="infer", nonexistent="NaT"
                    )
                except AmbiguousTimeError:
                    dst = np.ndarray(len(self.times), dtype=bool)  # type: ignore
                    dst.fill(True)
                    self._data = self._data.tz_localize(
                        str(tz), ambiguous=dst, nonexistent="NaT"
                    )
        self._timezone = str(tz)
        return self

    def aggregate(
        self,
        func: Union[list[Union[Callable[[Any], Any], str]], Callable[[Any], Any], str],
    ) -> Any:
        """
        Perform an aggregation of the values in a time series time series.

        Args:
            func (Union[list[Union[Callable[[Any], Any], str]],Callable[[Any], Any], str]): The aggregation function(s).
            May be one of:
                <ul>
                <li><b>list[Union[Callable[[Any], Any], str]]</b>: A list comprised of items from the following two options
                (note that there is overlap between the python builtin functions and the pandas functions)
                <li><b>Callable[[Any], Any]</b>: Must take an iterable of floats and return a float timeseries<br>
                    May be a function defined in the code (including lambda funtions) or a standard python aggregation function:
                    <ul>
                    <li><code>all</code></li>
                    <li><code>any</code></li>
                    <li><code>len</code></li>
                    <li><code>max</code></li>
                    <li><code>min</code></li>
                    <li><code>sum</code></li>
                    <li><code>math.prod</code></li>
                    <li><code>statistics.fmean</code></li>
                    <li><code>statistics.geometric_mean</code></li>
                    <li><code>statistics.harmonic_mean</code></li>
                    <li><code>statistics.mean</code></li>
                    <li><code>statistics.median</code></li>
                    <li><code>statistics.median_grouped</code></li>
                    <li><code>statistics.median_high</code></li>
                    <li><code>statistics.median_low</code></li>
                    <li><code>statistics.mode</code></li>
                    <li><code>statistics.multimode</code></li>
                    <li><code>statistics.pstdev</code></li>
                    <li><code>statistics.pvariance</code></li>
                    <li><code>statistics.quantiles</code></li>
                    <li><code>statistics.stdev</code></li>
                    <li><code>statistics.variance</code></li>
                    </ul>
                </li>
                <li><b>str</b>: Must be the name of a pandas aggregation function:
                    <ul>
                    <li><code>"all"</code></li>
                    <li><code>"any"</code></li>
                    <li><code>"count"</code></li>
                    <li><code>"describe"</code></li>
                    <li><code>"first"</code></li>
                    <li><code>"last"</code></li>
                    <li><code>"max"</code></li>
                    <li><code>"mean"</code></li>
                    <li><code>"median"</code></li>
                    <li><code>"min"</code></li>
                    <li><code>"nunique"</code></li>
                    <li><code>"prod"</code></li>
                    <li><code>"sem"</code></li>
                    <li><code>"size"</code></li>
                    <li><code>"skew"</code></li>
                    <li><code>"std"</code></li>
                    <li><code>"sum"</code></li>
                    <li><code>"var"</code></li>
                    </ul>
                </li>
                </ul>

        Raises:
            TimeSeriesException: If the time series has no data, or if there are less than two items
            to aggregate over.

        Returns:
            The result of the aggregation function(s)
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if self.has_selection:
            selected = self._data[self._data["selected"]]
            if len(selected) < 2:
                raise TimeSeriesException(
                    "Cannot perform aggregation with fewer than 2 items selected"
                )
            return selected["value"].agg(func)
        else:
            if len(self._data) < 2:
                raise TimeSeriesException(
                    "Cannot perform aggregation with fewer than 2 items"
                )
            return self._data["value"].agg(func)

    def percentile(self, pct: float) -> float:
        """
        Computes the specified percentile of the values in the time series

        Args:
            pct (float): The desired percentile in the range of 1..100

        Raises:
            TimeSeriesException: If the time series has no data or fewer than 2 items selected.

        Returns:
            float: The value for the specified percentile
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if self.has_selection:
            selected = self._data[self._data["selected"]]
            if len(selected) < 2:
                raise TimeSeriesException(
                    "Cannot perform operation with fewer than 2 items selected"
                )
            if self.selection_state == SelectionState.TRANSIENT:
                self.iselect(Select.ALL)
            return selected["value"].quantile(pct / 100.0)
        else:
            if len(self._data) < 2:
                raise TimeSeriesException(
                    "Cannot perform operation with fewer than 2 items"
                )
            return self._data["value"].quantile(pct / 100.0)

    def kurtosis(self) -> float:
        """
        Computes the kurtosis coefficient of the values in the time series

        Raises:
            TimeSeriesException: If the time series has no data or fewer than 2 items selected.

        Returns:
            float: The kurtosis coefficient
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if self.has_selection:
            selected = self._data[self._data["selected"]]
            if len(selected) < 2:
                raise TimeSeriesException(
                    "Cannot perform aggregation with fewer than 2 items selected"
                )
            return cast(float, selected["value"].kurtosis())
        else:
            if len(self._data) < 2:
                raise TimeSeriesException(
                    "Cannot perform aggregation with fewer than 2 items"
                )
            return cast(float, self._data["value"].kurtosis())

    def minValue(self) -> float:
        """
        Returns the minimum value in the time series.

        Raises:
            TimeSeriesException: If the time series has no data

        Returns:
            float: The minimum value in the time series
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if self.has_selection:
            selected = self._data[self._data["selected"]]
            if self.selection_state == SelectionState.TRANSIENT:
                self.iselect(Select.ALL)
            if len(selected) == 0:
                raise TimeSeriesException("Operation is invalid with empty selection.")
            return float(selected["value"].min())
        else:
            return float(self._data["value"].min())

    def maxValue(self) -> float:
        """
        Returns the maximum value in the time series.

        Raises:
            TimeSeriesException: If the time series has no data

        Returns:
            float: The maximum value in the time series
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if self.has_selection:
            selected = self._data[self._data["selected"]]
            if self.selection_state == SelectionState.TRANSIENT:
                self.iselect(Select.ALL)
            if len(selected) == 0:
                raise TimeSeriesException("Operation is invalid with empty selection.")
            return float(selected["value"].max())
        else:
            return float(self._data["value"].max())

    def minValueTime(self) -> HecTime:
        """
        Returns the time of minimum value in the time series.

        Raises:
            TimeSeriesException: If the time series has no data

        Returns:
            float: The time of minimum value in the time series. If the minimum value
                occurs more than once, the earliest time is returned.
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if self.has_selection:
            selected = self._data[self._data["selected"]]
            if self.selection_state == SelectionState.TRANSIENT:
                self.iselect(Select.ALL)
            if len(selected) == 0:
                raise TimeSeriesException("Operation is invalid with empty selection.")
            return HecTime(selected["value"].idxmin())
        else:
            return HecTime(self._data["value"].idxmin())

    def maxValueTime(self) -> HecTime:
        """
        Returns the time of maximum value in the time series.

        Raises:
            TimeSeriesException: If the time series has no data

        Returns:
            float: The time of maximum value in the time series. If the maximum value
                occurs more than once, the earliest time is returned.
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if self.has_selection:
            selected = self._data[self._data["selected"]]
            if self.selection_state == SelectionState.TRANSIENT:
                self.iselect(Select.ALL)
            if len(selected) == 0:
                raise TimeSeriesException("Operation is invalid with empty selection.")
            return HecTime(selected["value"].idxmax())
        else:
            return HecTime(self._data["value"].idxmax())

    def accum(self, in_place: bool = False) -> "TimeSeries":
        """
        Returns a time series whose values are the accumulation of values in this time series.

        Missing values are ignored; the accumulation at those times is the same as for the
        previous time.

        If a selection is present, all non-selected items are set to missing before the
        accumulation is computed. They remain missing in the retuned time series.

        Args:
            in_place (bool, optional): If True, this object is modified and retured, otherwise
                a copy of this object is modified and returned.. Defaults to False.

        Raises:
            TimeSeriesException: If the time series has no data.

        Returns:
            TimeSeries: The accumulation time series
        """
        target = self if in_place else self.copy()
        if target._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if target.has_selection:
            target._data.loc[~target._data["selected"], "value"] = np.nan
            if target.selection_state == SelectionState.TRANSIENT:
                target.iselect(Select.ALL)
        target._data["accum"] = target._data["value"].cumsum().ffill()
        target._data["value"] = target._data["accum"]
        target._data.drop(columns=["accum"])
        return target

    def iaccum(self) -> "TimeSeries":
        """
        Modifies this time series to be the accumulation of values originally in this time series.

        Identical to calling ts.accum(True)

        Missing values are ignored; the accumulation at those times is the same as for the
        previous time.

        If a selection is present, all non-selected items are set to missing before the
        accumulation is computed. They remain missing in the retuned time series.

        Raises:
            TimeSeriesException: If the time series has no data.

        Returns:
            TimeSeries: The modified time series
        """
        return self.accum(True)

    def _diff(self, time_based: bool, in_place: bool = False) -> "TimeSeries":
        target = self if in_place else self.copy()
        if target._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        if target.has_selection:
            target._data.loc[~target._data["selected"], "value"] = np.nan
            if target.selection_state == SelectionState.TRANSIENT:
                target.iselect(Select.ALL)
        if time_based:
            target._data["time-diffs"] = (
                target._data.index.to_series().diff().dt.total_seconds() / 60
            )
            target._data["diffs"] = (
                target._data["value"].diff() / target._data["time-diffs"]
            )
            target._data.drop(columns=["time-diffs"])
        else:
            target._data["diffs"] = target._data["value"].diff()
        target._data["value"] = target._data["diffs"]
        target._data.drop(columns=["diffs"])
        target._data = target._data.drop(target._data.index[0])
        return target

    def diff(self, in_place: bool = False) -> "TimeSeries":
        """
        Returns a time series whose values are the differences of successive values in this time series.

        A missing value at a specific time in the source time series will cause the value at that
        and the next time in the result time sereies to be missing.

        If a selection is present, all non-selected items are set to missing before the
        accumulation is computed. They remain missing in the retuned time series.

        Args:
            in_place (bool, optional): If True, this object is modified and retured, otherwise
                a copy of this object is modified and returned.. Defaults to False.

        Raises:
            TimeSeriesException: If the time series has no data.

        Returns:
            TimeSeries: The time series of differences
        """
        return self._diff(time_based=False, in_place=in_place)

    def idiff(self, in_place: bool = False) -> "TimeSeries":
        """
        Modifies time series to be the differences of successive values originally in this time series.

        Identical to calling ts.diff(True)

        A missing value at a specific time in the source time series will cause the value at that
        and the next time in the result time sereies to be missing.

        If a selection is present, all non-selected items are set to missing before the
        accumulation is computed. They remain missing in the retuned time series.

        Raises:
            TimeSeriesException: If the time series has no data.

        Returns:
            TimeSeries: The modified time series
        """
        return self.diff(True)

    def time_derivative(self, in_place: bool = False) -> "TimeSeries":
        """
        Returns a time series whose values are the differences of successive values in this time series divided
        by the number of minutes between the times of the values.

        A missing value at a specific time in the source time series will cause the value at that
        and the next time in the result time sereies to be missing.

        If a selection is present, all non-selected items are set to missing before the
        accumulation is computed. They remain missing in the retuned time series.

        Args:
            in_place (bool, optional): If True, this object is modified and retured, otherwise
                a copy of this object is modified and returned.. Defaults to False.

        Raises:
            TimeSeriesException: If the time series has no data.

        Returns:
            TimeSeries: The time series of time-based differences
        """
        return self._diff(time_based=True, in_place=in_place)

    def itime_derivative(self, in_place: bool = False) -> "TimeSeries":
        """
        Modifies time series to be the differences of successive values originally in this time series divided by the
        number of minutes between the times of the values.

        Identical to calling ts.time_derivative(True)

        A missing value at a specific time in the source time series will cause the value at that
        and the next time in the result time sereies to be missing.

        If a selection is present, all non-selected items are set to missing before the
        accumulation is computed. They remain missing in the retuned time series.

        Raises:
            TimeSeriesException: If the time series has no data.

        Returns:
            TimeSeries: The modified time series
        """
        return self.time_derivative(True)

    @property
    def number_values(self) -> int:
        """
        The number of values in the time series. Same as len(ts).

        Operations:
            Read Only
        """
        if len(self) == 0:
            return 0
        data = cast(pd.DataFrame, self._data)
        df = data[data["selected"]] if self.has_selection else data
        return df.shape[0]

    @property
    def number_valid_values(self) -> int:
        """
        The number of valid values in the time series. Values are valid unless any of the following are true:
        * The quality is MISSING
        * The quality is REJECTED
        * The value is NaN
        * The value is Infinite

        Operations:
            Read Only
        """
        if len(self) == 0:
            return 0
        data = cast(pd.DataFrame, self._data)
        df = data[data["selected"]] if self.has_selection else data
        if self.selection_state == SelectionState.TRANSIENT:
            self.iselect(Select.ALL)
        return int(
            df[
                ~(
                    (df["value"].isna())
                    | (np.isinf(df["value"]))
                    | (df["quality"] == 5)
                    | ((df["quality"].astype(int) & 0b1_0000) != 0)
                )
            ].shape[0]
        )

    @property
    def number_invalid_values(self) -> int:
        """
        The number of invalid values in the time series. Values are invalid if any of the following are true:
        * The quality is MISSING
        * The quality is REJECTED
        * The value is NaN
        * The value is Infinite

        Operations:
            Read Only
        """
        if len(self) == 0:
            return 0
        data = cast(pd.DataFrame, self._data)
        df = data[data["selected"]] if self.has_selection else data
        if self.selection_state == SelectionState.TRANSIENT:
            self.iselect(Select.ALL)
        return int(
            df[
                (df["value"].isna())
                | (np.isinf(df["value"]))
                | (df["quality"] == 5)
                | ((df["quality"].astype(int) & 0b1_0000) != 0)
            ].shape[0]
        )

    @property
    def number_missing_values(self) -> int:
        """
        The number of invalid values in the time series. Values are missing if either of the following are true:
        * The quality is MISSING
        * The value is NaN

        Operations:
            Read Only
        """
        if len(self) == 0:
            return 0
        data = cast(pd.DataFrame, self._data)
        df = data[data["selected"]] if self.has_selection else data
        if self.selection_state == SelectionState.TRANSIENT:
            self.iselect(Select.ALL)
        return df[(df["value"].isna()) | (df["quality"] == 5)].shape[0]

    @property
    def number_questioned_values(self) -> int:
        """
        The number of values in the time series that have quality of QUESTIONABLE:

        Operations:
            Read Only
        """
        if len(self) == 0:
            return 0
        data = cast(pd.DataFrame, self._data)
        df = data[data["selected"]] if self.has_selection else data
        if self.selection_state == SelectionState.TRANSIENT:
            self.iselect(Select.ALL)
        return df[((df["quality"].astype(int) & 0b1000) != 0)].shape[0]

    @property
    def number_rejected_values(self) -> int:
        """
        The number of values in the time series that have quality of REJECTED:

        Operations:
            Read Only
        """
        if len(self) == 0:
            return 0
        data = cast(pd.DataFrame, self._data)
        df = data[data["selected"]] if self.has_selection else data
        if self.selection_state == SelectionState.TRANSIENT:
            self.iselect(Select.ALL)
        return df[((df["quality"].astype(int) & 0b1_0000) != 0)].shape[0]

    @property
    def first_valid_value(self) -> Optional[float]:
        """
        The first valid value in the time series. Values are valid unless any of the following are true:
        * The quality is MISSING
        * The quality is REJECTED
        * The value is NaN
        * The value is Infinite

        Operations:
            Read Only
        """
        if len(self) == 0:
            return None
        data = cast(pd.DataFrame, self._data)
        df = data[data["selected"]] if self.has_selection else data
        if self.selection_state == SelectionState.TRANSIENT:
            self.iselect(Select.ALL)
        validIndices = TimeSeries._validIndices(df)
        return (
            None if len(validIndices) == 0 else float(df.loc[validIndices[0]]["value"])
        )

    @property
    def first_valid_time(self) -> Optional[np.datetime64]:
        """
        The time of the first valid value in the time series. Values are valid unless any of the following are true:
        * The quality is MISSING
        * The quality is REJECTED
        * The value is NaN
        * The value is Infinite

        Operations:
            Read Only
        """
        if len(self) == 0:
            return None
        data = cast(pd.DataFrame, self._data)
        df = data[data["selected"]] if self.has_selection else data
        if self.selection_state == SelectionState.TRANSIENT:
            self.iselect(Select.ALL)
        validIndices = TimeSeries._validIndices(df)
        return (
            None
            if len(validIndices) == 0
            else cast(np.datetime64, df.loc[validIndices[0]].name)
        )

    @property
    def last_valid_value(self) -> Optional[float]:
        """
        The last valid value in the time series. Values are valid unless any of the following are true:
        * The quality is MISSING
        * The quality is REJECTED
        * The value is NaN
        * The value is Infinite

        Operations:
            Read Only
        """
        if len(self) == 0:
            return None
        data = cast(pd.DataFrame, self._data)
        df = data[data["selected"]] if self.has_selection else data
        if self.selection_state == SelectionState.TRANSIENT:
            self.iselect(Select.ALL)
        validIndices = TimeSeries._validIndices(df)
        return (
            None if len(validIndices) == 0 else float(df.loc[validIndices[-1]]["value"])
        )

    @property
    def last_valid_time(self) -> Optional[np.datetime64]:
        """
        The time of the last valid value in the time series. Values are valid unless any of the following are true:
        * The quality is MISSING
        * The quality is REJECTED
        * The value is NaN
        * The value is Infinite

        Operations:
            Read Only
        """
        if len(self) == 0:
            return None
        data = cast(pd.DataFrame, self._data)
        df = data[data["selected"]] if self.has_selection else data
        if self.selection_state == SelectionState.TRANSIENT:
            self.iselect(Select.ALL)
        validIndices = TimeSeries._validIndices(df)
        return (
            None
            if len(validIndices) == 0
            else cast(np.datetime64, df.loc[validIndices[-1]].name)
        )

    @property
    def is_english(self) -> bool:
        """
        Returns whether the unit of this time series is recognized as an English unit

        Operations:
            Read Only
        """
        return self.unit in hec.unit.unit_names_by_unit_system["EN"]

    @property
    def is_metric(self) -> bool:
        """
        Returns whether the unit of this time series is recognized as an Metric unit

        Operations:
            Read Only
        """
        return self.unit in hec.unit.unit_names_by_unit_system["SI"]

    @property
    def can_determine_unit_system(self) -> bool:
        """
        Returns whether the unit of this time series is recognized as an English unit, or a Metric unit, but not both

        Operations:
            Read Only
        """
        return self.is_english != self.is_metric

    def setProtected(self, in_place: bool = False) -> "TimeSeries":
        """
        Sets the quality protection bit of selected items of this time series - or a copy of it - and
        returns the modified time series.

        Args:
            in_place (bool, optional): Specifies whether to modify and return this time series (True)
                or a copy of this time series (False). Defaults to False.

        Raises:
            TimeSeriesException: If the time series has no data.

        Returns:
            TimeSeries: The modidified time series
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        # ------------------------------ #
        # get the DataFrame to work with #
        # ------------------------------ #
        target = self if in_place else self.copy()
        data = cast(pd.DataFrame, target._data)
        df = data.loc[data["selected"]] if target.has_selection else data
        # -------------------------------------------- #
        # set the protection bit of selected qualities #
        # -------------------------------------------- #
        df.loc[:, "quality"] |= 0b1000_0000_0000_0000_0000_0000_0000_0001
        cast(pd.DataFrame, target._data).update(df)
        if target.selection_state == SelectionState.TRANSIENT:
            target.iselect(Select.ALL)
        return target

    def isetProtected(self) -> "TimeSeries":
        """
        Sets the quality protection bit of selected items of this time series and
        returns the modified time series.

        Identical to calling `setProtected(in_place=True)`

        Raises:
            TimeSeriesException: If the time series has no data.

        Returns:
            TimeSeries: The modidified time series
        """
        return self.setProtected(in_place=True)

    def setUnprotected(self, in_place: bool = False) -> "TimeSeries":
        """
        Un-sets the quality protection bit of selected items of this time series - or a copy of it - and
        returns the modified time series.

        Args:
            in_place (bool, optional): Specifies whether to modify and return this time series (True)
                or a copy of this time series (False). Defaults to False.

        Raises:
            TimeSeriesException: If the time series has no data.

        Returns:
            TimeSeries: The modidified time series
        """
        # ------------------------------ #
        # get the DataFrame to work with #
        # ------------------------------ #
        target = self if in_place else self.copy()
        data = cast(pd.DataFrame, target._data)
        df = data.loc[data["selected"]] if self.has_selection else data
        df.loc[:, "quality"] = df["quality"] & 0b0111_1111_1111_1111_1111_1111_1111_1111
        cast(pd.DataFrame, target._data).update(df)
        if target.selection_state == SelectionState.TRANSIENT:
            target.iselect(Select.ALL)
        return target

    def isetUnprotected(self) -> "TimeSeries":
        """
        Un-sets the quality protection bit of selected items of this time series and
        returns the modified time series.

        Identical to calling `setUnprotected(in_place=True)`

        Args:
            in_place (bool, optional): Specifies whether to modify and return this time series (True)
                or a copy of this time series (False). Defaults to False.

        Raises:
            TimeSeriesException: If the time series has no data.

        Returns:
            TimeSeries: The modidified time series
        """
        return self.setUnprotected(in_place=True)

    @staticmethod
    def _roundOff(v: float, precision: int, tens_place: int) -> float:
        if np.isnan(v) or np.isinf(v):
            return v
        exponent = 0
        factor = 1.0
        v2 = abs(v)
        while v2 > 10.0:
            exponent += 1
            factor /= 10.0
            v2 /= 10.0
        while v2 < 1.0:
            exponent -= 1
            factor *= 10.0
            v2 *= 10.0
        precision = min(exponent + 1 - tens_place, precision)
        if precision >= 0:
            factor_precision = 10 ** (precision - 1)
            v3 = np.rint(factor_precision * v2) / factor_precision / factor
            if v < 0.0:
                v3 = -v3
        else:
            v3 = 0.0
        return round(float(v3), 10)

    def roundOff(
        self, precision: int, tens_place: int, in_place: bool = False
    ) -> "TimeSeries":
        """
        Return a time series whose values are rounded according to the parameters.

        <table>
        <tr><th>value</th><th>precision</th><th>tens_place></th><th>result</th></tr>
        <tr><td>123456.789</td><td>5</td><td>0</td><td>123460.0</td></tr>
        <tr><td>123456.789</td><td>7</td><td>-1</td><td>123456.8</td></tr>
        <tr><td>123456.789</td><td>7</td><td>0</td><td>123457.0</td></tr>
        <tr><td>123456.789</td><td>7</td><td>1</td><td>123460.0</td></tr>
        </table>

        Args:
            precision (int): The maximum number of significant digits to use.
            tens_place (int): The lowest power of 10 to have a non-zero value.
            in_place (bool, optional): Modify and return this object if True, otherwise modify
                and return a copy of this object. Defaults to False.

        Returns:
            TimeSeries: The modified object
        """
        return self.map(
            lambda v: TimeSeries._roundOff(v, precision, tens_place), in_place
        )

    def iroundOff(self, precision: int, tens_place: int) -> "TimeSeries":
        """
        Modify this time series by rounding values according to the parameters, and return it.

        Identical to calling ts.rounOff(..., in_place=True)

        <table>
        <tr><th>value</th><th>precision</th><th>tens_place></th><th>result</th></tr>
        <tr><td>123456.789</td><td>5</td><td>0</td><td>123460.0</td></tr>
        <tr><td>123456.789</td><td>7</td><td>-1</td><td>123456.8</td></tr>
        <tr><td>123456.789</td><td>7</td><td>0</td><td>123457.0</td></tr>
        <tr><td>123456.789</td><td>7</td><td>1</td><td>123460.0</td></tr>
        </table>

        Args:
            precision (int): The maximum number of significant digits to use.
            tens_place (int): The lowest power of 10 to have a non-zero value.

        Returns:
            TimeSeries: The modified object
        """
        return self.map(lambda v: TimeSeries._roundOff(v, precision, tens_place), True)

    def _movingAverage(
        self,
        operation: str,
        window: int,
        onlyValid: bool,
        useReduced: bool,
        in_place: bool = False,
    ) -> "TimeSeries":
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        op = operation.upper()
        centered = op in ["CENTERED", "OLYMPIC"]
        olympic = op == "OLYMPIC"
        if window < 2:
            raise TimeSeriesException("Window size for averaging must be > 1")
        if centered and window % 2 == 0:
            raise TimeSeriesException(
                f"Window must be an odd number for {'Olympic' if olympic else 'Centered'} moving average"
            )
        # ------------------------------ #
        # get the DataFrame to work with #
        # ------------------------------ #
        target = self if in_place else self.copy()
        df = cast(pd.DataFrame, target._data)
        # --------------------------- #
        # first perform the averaging #
        # --------------------------- #
        if olympic:
            # -------------------------------------------- #
            # we have to roll our own function for Olympic #
            # -------------------------------------------- #
            def olympic_average(vals: np.ndarray) -> Any:  # type: ignore
                vals = vals[~np.isnan(vals)]
                if len(vals) <= 2:
                    return np.nan
                return np.mean(np.sort(vals)[1:-1])

            df["averaged"] = (
                df["value"]
                .rolling(window=window, min_periods=1, center=True)
                .apply(olympic_average, raw=True)
            )
        else:
            # --------------------------------------------------- #
            # for Forward and Centered we can use built-in mean() #
            # --------------------------------------------------- #
            df["averaged"] = (
                df["value"]
                .rolling(window=window, min_periods=1, center=centered)
                .mean()
            )
        # -------------------------------------------------------------------------------- #
        # next change any values that don't match onlyValid and useReduced criteria to NaN #
        # -------------------------------------------------------------------------------- #
        if onlyValid:
            invalidIndices = TimeSeries._invalidIndices(df)
            bad: set[np.datetime64] = set()
            if centered:
                for idx in invalidIndices:
                    pos = cast(int, df.index.get_loc(idx))
                    bad.update(df.index[pos - window // 2 : pos - window // 2 + window])
            else:
                for idx in invalidIndices:
                    pos = cast(int, df.index.get_loc(idx))
                    bad.update(df.index[pos : pos + window])
            badIndices = sorted(bad)
            df.loc[badIndices, "averaged"] = np.nan
        if centered:
            if not useReduced:
                df.loc[df.index[: window // 2], "averaged"] = np.nan
                df.loc[df.index[-(window // 2) :], "averaged"] = np.nan
        else:
            if useReduced:
                df.loc[df.index[0], "averaged"] = np.nan
            else:
                df.loc[df.index[: window - 1], "averaged"] = np.nan
        # -------------------------------- #
        # finally clean up and set quality #
        # -------------------------------- #
        df["value"] = df["averaged"]
        df.drop(columns=["averaged"], inplace=True)
        df.loc[TimeSeries._validIndices(df), "quality"] = 0
        df.loc[TimeSeries._invalidIndices(df), "quality"] = 5
        return target

    def forwardMovingAverage(
        self, window: int, onlyValid: bool, useReduced: bool, in_place: bool = False
    ) -> "TimeSeries":
        """
        Computes and returns a time series that is the forward moving average of this time series.

        A forward moving average sets the value at each time to be the average of the values at that
        time and a number of previous consecutive times.

        Args:
            window (int): The number of values to average over. The result at each time will be
                the average of the values at (window-1) previous times and the value at the current
                time. The span between times is not accounted for so discretion should be used if
                the time series is irregular.
            onlyValid (bool): Specifies whether to only average over windows where every value is
                valid. If False, the average at any given time may be computed using fewer values
                that specified in the window parameter.
            useReduced (bool): Specifies whether to allow averages using less than window number
                of values will be computed at the beginning of the times series. If False, the
                values at the first (window-1) times will be set to missing.
            in_place (bool, optional): If True, this time series is modified and returned.
                Otherwise this time series is not modified. Defaults to False.

        Raises:
            TimeSeriesException: If the time series has no data or if the window is invalid.

        Returns:
            TimeSeries: The averaged time series
        """
        return self._movingAverage("FORWARD", window, onlyValid, useReduced, in_place)

    def iforwardMovingAverage(
        self, window: int, onlyValid: bool, useReduced: bool, in_place: bool = False
    ) -> "TimeSeries":
        """
        Modifies this time series to be the forward moving average of the original values, and returns it.

        A forward moving average sets the value at each time to be the average of the values at that
        time and a number of previous consecutive times.

        Args:
            window (int): The number of values to average over. The result at each time will be
                the average of the values at (window-1) previous times and the value at the current
                time. The span between times is not accounted for so discretion should be used if
                the time series is irregular.
            onlyValid (bool): Specifies whether to only average over windows where every value is
                valid. If False, the average at any given time may be computed using fewer values
                that specified in the window parameter.
            useReduced (bool): Specifies whether to allow averages using less than window number
                of values will be computed at the beginning of the times series. If False, the
                values at the first (window-1) times will be set to missing.

        Raises:
            TimeSeriesException: If the time series has no data or if the window is invalid.

        Returns:
            TimeSeries: The averaged time series
        """
        return self.forwardMovingAverage(window, onlyValid, useReduced, in_place=True)

    def centeredMovingAverage(
        self, window: int, onlyValid: bool, useReduced: bool, in_place: bool = False
    ) -> "TimeSeries":
        """
        Computes and returns a time series that is the centered moving average of this time series.

        A centered moving average sets the value at each time to be the average of the values at that
        time and a number of previous and following consecutive times.

        Args:
            window (int): The number of values to average over. The result at each time will be
                the average of the values at ((window-1)/2) previous times, the value at the current
                time, and the values at ((window-1)/2) following times. The span between times is not
                accounted for so discretion should be used if the time series is irregular. Must be an odd number.
            onlyValid (bool): Specifies whether to only average over windows where every value is
                valid. If False, the average at any given time may be computed using fewer values
                that specified in the window parameter.
            useReduced (bool): Specifies whether to allow averages using less than window number
                of values will be computed at the beginning and end of the times series. If False, the
                values at the first and last ((window-1)/2) times will be set to missing.
            in_place (bool, optional): If True, this time series is modified and returned.
                Otherwise this time series is not modified. Defaults to False.

        Raises:
            TimeSeriesException: If the time series has no data or if the window is invalid.

        Returns:
            TimeSeries: The averaged time series
        """
        return self._movingAverage("CENTERED", window, onlyValid, useReduced, in_place)

    def icenteredMovingAverage(
        self, window: int, onlyValid: bool, useReduced: bool, in_place: bool = False
    ) -> "TimeSeries":
        """
        Modifies this time series to be the centered moving average of the original values, and returns it.

        A centered moving average sets the value at each time to be the average of the values at that
        time and a number of previous and following consecutive times.

        Args:
            window (int): The number of values to average over. The result at each time will be
                the average of the values at ((window-1)/2) previous times, the value at the current
                time, and the values at ((window-1)/2) following times. The span between times is not
                accounted for so discretion should be used if the time series is irregular. Must be an odd number.
            onlyValid (bool): Specifies whether to only average over windows where every value is
                valid. If False, the average at any given time may be computed using fewer values
                that specified in the window parameter.
            useReduced (bool): Specifies whether to allow averages using less than window number
                of values will be computed at the beginning and end of the times series. If False, the
                values at the first and last ((window-1)/2) times will be set to missing.
            in_place (bool, optional): If True, this time series is modified and returned.
                Otherwise this time series is not modified. Defaults to False.

        Raises:
            TimeSeriesException: If the time series has no data or if the window is invalid.

        Returns:
            TimeSeries: The averaged time series
        """
        return self.centeredMovingAverage(window, onlyValid, useReduced, in_place=True)

    def olympicMovingAverage(
        self, window: int, onlyValid: bool, useReduced: bool, in_place: bool = False
    ) -> "TimeSeries":
        """
        Computes and returns a time series that is the olympic moving average of this time series.

        An olympic moving average sets the value at each time to be the average of the values at that
        time and a number of previous and following consecutive times, disregarding the minimum
        and maximum values in the range to average over.

        Args:
            window (int): The number of values to average over. The result at each time will be
                the average of the values at ((window-1)/2) previous times, the value at the current
                time, and the values at ((window-1)/2) following times, not using the minimum and
                maximum values in the window. The span between times is not accounted for so discretion
                should be used if the time series is irregular. Must be an odd number.
            onlyValid (bool): Specifies whether to only average over windows where every value is
                valid. If False, the average at any given time may be computed using fewer values
                that specified in the window parameter.
            useReduced (bool): Specifies whether to allow averages using less than window number
                of values will be computed at the beginning and end of the times series. If False, the
                values at the first and last ((window-1)/2) times will be set to missing.
            in_place (bool, optional): If True, this time series is modified and returned.
                Otherwise this time series is not modified. Defaults to False.

        Raises:
            TimeSeriesException: If the time series has no data or if the window is invalid.

        Returns:
            TimeSeries: The averaged time series
        """
        return self._movingAverage("OLYMPIC", window, onlyValid, useReduced, in_place)

    def iolympicMovingAverage(
        self, window: int, onlyValid: bool, useReduced: bool, in_place: bool = False
    ) -> "TimeSeries":
        """
        Modifies this time series to be the olympic moving average of the original values, and returns it.

        An olympic moving average sets the value at each time to be the average of the values at that
        time and a number of previous and following consecutive times, disregarding the minimum
        and maximum values in the range to average over.

        Args:
            window (int): The number of values to average over. The result at each time will be
                the average of the values at ((window-1)/2) previous times, the value at the current
                time, and the values at ((window-1)/2) following times, not using the minimum and
                maximum values in the window. The span between times is not accounted for so discretion
                should be used if the time series is irregular. Must be an odd number.
            onlyValid (bool): Specifies whether to only average over windows where every value is
                valid. If False, the average at any given time may be computed using fewer values
                that specified in the window parameter.
            useReduced (bool): Specifies whether to allow averages using less than window number
                of values will be computed at the beginning and end of the times series. If False, the
                values at the first and last ((window-1)/2) times will be set to missing.
            in_place (bool, optional): If True, this time series is modified and returned.
                Otherwise this time series is not modified. Defaults to False.

        Raises:
            TimeSeriesException: If the time series has no data or if the window is invalid.

        Returns:
            TimeSeries: The averaged time series
        """
        return self.olympicMovingAverage(window, onlyValid, useReduced, in_place=True)

    def screenWithValueRange(
        self,
        minRejectLimit: float = math.nan,
        minQuestionLimit: float = math.nan,
        maxQuestionLimit: float = math.nan,
        maxRejectLimit: float = math.nan,
        in_place: bool = False,
    ) -> "TimeSeries":
        """
        Screens a time series - either this one or a copy of this one - settting the quality codes to
        "Okay", "Missing", "Questionable" or "Rejected" based on specified criteria about the value magnitudes.

        Args:
            minRejectLimit (float, optional): The minimum value that is not flagged as rejected. Defaults to `-math.nan` (test disabled).
            minQuestionLimit (float, optional): The minium non-rejected value that is flagged as questionable. Defaults to `-math.nan` (test disabled).
            maxQuestionLimit (float, optional): The maxium non-rejected value that is flagged as questionable. Defaults to `-math.nan` (test disabled).
            maxRejectLimit (float, optional): The minimum value that is not flagged as rejected. Defaults to `-math.nan` (test disabled).
            in_place (bool, optional): Specifies whether to modify and return this time series (True) or a copy of this
                time series (False). Defaults to False.

        Raises:
            TimeSeriesException: If this time series has no data, or if:
                * `minRejectLimit` (if not `math.nan`) is not less than `minQuestionLimit` (if not `math.nan`) or `maxRejectLimit` (if not `math.nan`)
                * `minQuestionLimit` (if not `math.nan`) is not less than `maxQuestionLimit` (if not `math.nan`) or `maxRejectLimit` (if not `math.nan`)
                * `maxQuestionLimit` (if not `math.nan`) is not less thatn `maxRejectLimit` (if not `math.nan`)

        Returns:
            TimeSeries: The screened time series
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        # ---------------- #
        # set up variables #
        # ---------------- #
        testMinReject = not math.isnan(minRejectLimit)
        testMinQuestion = not math.isnan(minQuestionLimit)
        testMaxQuestion = not math.isnan(maxQuestionLimit)
        testMaxReject = not math.isnan(maxRejectLimit)
        if testMinReject:
            if testMinQuestion and minRejectLimit >= minQuestionLimit:
                raise TimeSeriesException(
                    "minRejectLimit must be less than minQuestionLimit"
                )
            if testMaxReject and maxRejectLimit <= minRejectLimit:
                raise TimeSeriesException(
                    "minRejectLimit must be less than maxRejectLimit"
                )
        elif testMinQuestion:
            if testMaxQuestion and minQuestionLimit >= maxQuestionLimit:
                raise TimeSeriesException(
                    "minQuestionLimit must be less than maxQuestionLimit"
                )
            if testMaxReject and minQuestionLimit >= maxRejectLimit:
                raise TimeSeriesException(
                    "minQuestionLimit must be less than maxRejectLimit"
                )
        elif testMaxQuestion and testMaxReject:
            if maxQuestionLimit >= maxRejectLimit:
                raise TimeSeriesException(
                    "maxQuestionLimit must be less than maxRejectLimit"
                )
        qualityText = {
            "okay": "Screened Okay No_Range Original None None None Unprotected",
            "missing": "Screened Missing No_Range Original None None None Unprotected",
            "question": "Screened Questionable No_Range Original None None Absolute_Value Unprotected",
            "reject": "Screened Rejected No_Range Original None None Absolute_Value Unprotected",
        }
        okayCode = Quality(qualityText["okay"].split()).code
        missingCode = Quality(qualityText["missing"].split()).code
        questionCode = Quality(qualityText["question"].split()).code
        rejectCode = Quality(qualityText["reject"].split()).code
        # ------------------------------ #
        # get the DataFrame to work with #
        # ------------------------------ #
        target = self if in_place else self.copy()
        data = cast(pd.DataFrame, target._data)
        df = data.loc[data["selected"]] if self.has_selection else data
        # ---------------- #
        # do the screening #
        # ---------------- #
        protectedIndices = set(TimeSeries._protectedIndicies(df))
        missingIndices = set(df[df["value"].isna()].index)
        questionIndices = set()
        rejectIndices = set()
        if testMinReject:
            rejectIndices |= set(
                df[
                    (df["value"] < minRejectLimit) & (~df.index.isin(protectedIndices))
                ].index
            )
        if testMaxReject:
            rejectIndices |= set(
                df[
                    (df["value"] > maxRejectLimit) & (~df.index.isin(protectedIndices))
                ].index
            )
        if testMinQuestion:
            questionIndices |= set(
                df[
                    (df["value"] < minQuestionLimit)
                    & (~df.index.isin(protectedIndices))
                    & (~df.index.isin(rejectIndices))
                ].index
            )
        if testMaxQuestion:
            questionIndices |= set(
                df[
                    (df["value"] > maxQuestionLimit)
                    & (~df.index.isin(protectedIndices))
                    & (~df.index.isin(rejectIndices))
                ].index
            )
        okayIndices = df.index.difference(
            list(protectedIndices | rejectIndices | questionIndices | missingIndices)
        )
        df.loc[
            df.index.isin(okayIndices) & ~df.index.isin(protectedIndices), "quality"
        ] = okayCode
        df.loc[
            df.index.isin(missingIndices) & ~df.index.isin(protectedIndices), "quality"
        ] |= missingCode
        df.loc[
            df.index.isin(questionIndices) & ~df.index.isin(protectedIndices), "quality"
        ] |= questionCode
        df.loc[
            df.index.isin(rejectIndices) & ~df.index.isin(protectedIndices), "quality"
        ] |= rejectCode
        data.update(df)
        return target

    def iscreenWithValueRange(
        self,
        minRejectLimit: float = math.nan,
        minQuestionLimit: float = math.nan,
        maxQuestionLimit: float = math.nan,
        maxRejectLimit: float = math.nan,
    ) -> "TimeSeries":
        """
        Screens a this time series, settting the quality codes to "Okay", "Missing", "Questionable" or "Rejected" based on specified criteria about the value magnitudes.

        Identical to calling `screenValueRange(..., in_place=True)`

        Args:
            minRejectLimit (float, optional): The minimum value that is not flagged as rejected. Defaults to `-math.nan` (test disabled).
            minQuestionLimit (float, optional): The minium non-rejected value that is flagged as questionable. Defaults to `-math.nan` (test disabled).
            maxQuestionLimit (float, optional): The maxium non-rejected value that is flagged as questionable. Defaults to `-math.nan` (test disabled).
            maxRejectLimit (float, optional): The minimum value that is not flagged as rejected. Defaults to `-math.nan` (test disabled).

        Raises:
            TimeSeriesException: If this time series has no data, or if:
                * `minRejectLimit` (if not `math.nan`) is not less than `minQuestionLimit` (if not `math.nan`) or `maxRejectLimit` (if not `math.nan`)
                * `minQuestionLimit` (if not `math.nan`) is not less than `maxQuestionLimit` (if not `math.nan`) or `maxRejectLimit` (if not `math.nan`)
                * `maxQuestionLimit` (if not `math.nan`) is not less thatn `maxRejectLimit` (if not `math.nan`)

        Returns:
            TimeSeries: The screened time series
        """
        return self.screenWithValueRange(
            minRejectLimit, minQuestionLimit, maxQuestionLimit, maxRejectLimit
        )

    def screenWithValueChangeRate(
        self,
        minRejectLimit: float = math.nan,
        minQuestionLimit: float = math.nan,
        maxQuestionLimit: float = math.nan,
        maxRejectLimit: float = math.nan,
        in_place: bool = False,
    ) -> "TimeSeries":
        """
        Screens a time series - either this one or a copy of this one - settting the quality codes to
        "Okay", "Missing", "Questionable" or "Rejected" based on specified criteria about the rate of change.

        Args:
            minRejectLimit (float, optional): The minimum change per minute from one value to the next (increasing or decreasing) that is not flagged as rejected. Defaults to `math.nan` (test disabled).
            minRejectLimit (float, optional): The minimum non-rejected change per minute  from one value to the next (increasing or decreasing) that is not flagged as questioned. Defaults to `math.nan` (test disabled).
            maxRejectLimit (float, optional): The maximum non-rejected change per minute  from one value to the next (increasing or decreasing) that is not flagged as questioned. Defaults to `math.nan` (test disabled).
            maxRejectLimit (float, optional): The maximum change per minute  from one value to the next (increasing or decreasing) that is not flagged as rejected. Defaults to `-ath.nan` (test disabled).
            in_place (bool, optional): Specifies whether to modify and return this time series (True) or a copy of this
                time series (False). Defaults to False.

        Raises:
            TimeSeriesException: If this time series has no data, or if:
                * `minRejectLimit` (if not `math.nan`) is not less than `minQuestionLimit` (if not `math.nan`) or `maxRejectLimit` (if not `math.nan`)
                * `minQuestionLimit` (if not `math.nan`) is not less than `maxQuestionLimit` (if not `math.nan`) or `maxRejectLimit` (if not `math.nan`)
                * `maxQuestionLimit` (if not `math.nan`) is not less thatn `maxRejectLimit` (if not `math.nan`)

        Returns:
            TimeSeries: The screened time series
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        # ---------------- #
        # set up variables #
        # ---------------- #
        testMinReject = not math.isnan(minRejectLimit)
        testMinQuestion = not math.isnan(minQuestionLimit)
        testMaxQuestion = not math.isnan(maxQuestionLimit)
        testMaxReject = not math.isnan(maxRejectLimit)
        if testMinReject:
            if testMinQuestion and minRejectLimit >= minQuestionLimit:
                raise TimeSeriesException(
                    "minRejectLimit must be less than minQuestionLimit"
                )
            if testMaxReject and maxRejectLimit <= minRejectLimit:
                raise TimeSeriesException(
                    "minRejectLimit must be less than maxRejectLimit"
                )
        elif testMinQuestion:
            if testMaxQuestion and minQuestionLimit >= maxQuestionLimit:
                raise TimeSeriesException(
                    "minQuestionLimit must be less than maxQuestionLimit"
                )
            if testMaxReject and minQuestionLimit >= maxRejectLimit:
                raise TimeSeriesException(
                    "minQuestionLimit must be less than maxRejectLimit"
                )
        elif testMaxQuestion and testMaxReject:
            if maxQuestionLimit >= maxRejectLimit:
                raise TimeSeriesException(
                    "maxQuestionLimit must be less than maxRejectLimit"
                )
        qualityText = {
            "okay": "Screened Okay No_Range Original None None None Unprotected",
            "missing": "Screened Missing No_Range Original None None None Unprotected",
            "question": "Screened Questionable No_Range Original None None Rate_of_Change Unprotected",
            "reject": "Screened Rejected No_Range Original None None Rate_of_Change Unprotected",
        }
        okayCode = Quality(qualityText["okay"].split()).code
        missingCode = Quality(qualityText["missing"].split()).code
        questionCode = Quality(qualityText["question"].split()).code
        rejectCode = Quality(qualityText["reject"].split()).code
        # ------------------------------ #
        # get the DataFrame to work with #
        # ------------------------------ #
        target = self if in_place else self.copy()
        data = cast(pd.DataFrame, target._data)
        data["value_diff"] = data["value"].diff()
        data["minutes_diff"] = data.index.to_series().diff().dt.total_seconds() / 60
        data["rate_of_change"] = data["value_diff"] / data["minutes_diff"]
        df = data.loc[data["selected"]] if self.has_selection else data
        # ---------------- #
        # do the screening #
        # ---------------- #
        protectedIndices = set(TimeSeries._protectedIndicies(df))
        unscreenedIndices = set([df.index[0]])
        missingIndices = set(df[df["rate_of_change"].isna()].index) - unscreenedIndices
        questionIndices = set()
        rejectIndices = set()
        if testMinReject:
            rejectIndices |= set(
                df[
                    (df["rate_of_change"] < minRejectLimit)
                    & (~df.index.isin(protectedIndices))
                ].index
            )
        if testMaxReject:
            rejectIndices |= set(
                df[
                    (df["rate_of_change"] > maxRejectLimit)
                    & (~df.index.isin(protectedIndices))
                ].index
            )
        if testMinQuestion:
            questionIndices |= set(
                df[
                    (df["rate_of_change"] < minQuestionLimit)
                    & (~df.index.isin(protectedIndices))
                    & (~df.index.isin(rejectIndices))
                ].index
            )
        if testMaxQuestion:
            questionIndices |= set(
                df[
                    (df["rate_of_change"] > maxQuestionLimit)
                    & (~df.index.isin(protectedIndices))
                    & (~df.index.isin(rejectIndices))
                ].index
            )
        okayIndices = df.index.difference(
            list(
                protectedIndices
                | missingIndices
                | unscreenedIndices
                | questionIndices
                | rejectIndices
            )
        )
        df.loc[
            df["rate_of_change"].isna()
            & ~df.index.isin(protectedIndices)
            & ~df.index.isin(unscreenedIndices),
            "quality",
        ] = (df["quality"] & ~missingCode) | missingCode
        df.loc[
            df.index.isin(okayIndices) & ~df.index.isin(protectedIndices), "quality"
        ] = okayCode
        df.loc[
            df.index.isin(missingIndices) & ~df.index.isin(protectedIndices), "quality"
        ] |= missingCode
        df.loc[
            df.index.isin(questionIndices) & ~df.index.isin(protectedIndices), "quality"
        ] |= questionCode
        df.loc[
            df.index.isin(rejectIndices) & ~df.index.isin(protectedIndices), "quality"
        ] |= rejectCode
        data.update(df)
        data.drop(
            columns=["value_diff", "minutes_diff", "rate_of_change"], inplace=True
        )
        return target

    def iscreenWithValueChangeRate(
        self,
        minRejectLimit: float = math.nan,
        minQuestionLimit: float = math.nan,
        maxQuestionLimit: float = math.nan,
        maxRejectLimit: float = math.nan,
    ) -> "TimeSeries":
        """
        Screens this a time series, settting the quality codes to "Okay", "Missing", "Questionable" or "Rejected" based on specified criteria about the rate of change.

        Args:
            minRejectLimit (float, optional): The minimum change per minute from one value to the next (increasing or decreasing) that is not flagged as rejected. Defaults to `math.nan` (test disabled).
            minRejectLimit (float, optional): The minimum non-rejected change per minute  from one value to the next (increasing or decreasing) that is not flagged as questioned. Defaults to `math.nan` (test disabled).
            maxRejectLimit (float, optional): The maximum non-rejected change per minute  from one value to the next (increasing or decreasing) that is not flagged as questioned. Defaults to `math.nan` (test disabled).
            maxRejectLimit (float, optional): The maximum change per minute  from one value to the next (increasing or decreasing) that is not flagged as rejected. Defaults to `-ath.nan` (test disabled).

        Raises:
            TimeSeriesException: If this time series has no data, or if:
                * `minRejectLimit` (if not `math.nan`) is not less than `minQuestionLimit` (if not `math.nan`) or `maxRejectLimit` (if not `math.nan`)
                * `minQuestionLimit` (if not `math.nan`) is not less than `maxQuestionLimit` (if not `math.nan`) or `maxRejectLimit` (if not `math.nan`)
                * `maxQuestionLimit` (if not `math.nan`) is not less thatn `maxRejectLimit` (if not `math.nan`)

        Returns:
            TimeSeries: The screened time series
        """
        return self.screenWithValueChangeRate(
            minRejectLimit, minQuestionLimit, maxRejectLimit, maxQuestionLimit
        )

    def screenWithValueRangeOrChange(
        self,
        minLimit: float = math.nan,
        maxLimit: float = math.nan,
        changeLimit: float = math.nan,
        replaceInvalidValue: bool = True,
        invalidValueReplacement: float = math.nan,
        invalidValidity: str = "M",
        in_place: bool = False,
    ) -> "TimeSeries":
        """
        Screens a time series - either this one or a copy of this one - setting values and/or quality codes
        where the values are outside the specified range or differ more than the specified change.

        Args:
            minLimit (float): The minimum valid value. Values below this value will have their values and/or quality codes changed.
                Defaults to `math.nan` (test disabled).
            maxLimit (float): The maximum valid value. Values above this value will have their values and/or quality codes changed.
                Defaults to `math.nan` (test disabled).
            changeLimit (float): The maxium valid change from one value to the next. Values whose change (either increasing or decreasing)
                is greater that is will have their values and/or quality codes changed. Defaults to `math.nan` (test disabled).
            replaceInvalidValue (bool, optional): Replace screened-out values with the specified value. Defaults to True.
            invalidValueReplacement (float, optional): The value to replace screen-out values with if `replaceInvalidValue=True`.
                 Defaults to `math.nan` (missing value).
            invalidValidity (str, optional): Specifies the validity component of the quality code for screened-out values.
                May be "M" (Missing), "Q" (Questionable), or "R" (Rejected). Values flagged as missing also have the value modified to math.nan.
                Defaults to "M".
            in_place (bool, optional): Specifies whether to modify and return this time series (True) or a copy of this
                time series (False). Defaults to False.

        Raises:
            TimeSeriesException: If the time series has no data or f `invalidValidity` (if specified) is not 'M', 'Q', or 'R'.

        Returns:
            TimeSeries: The screened time series
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        # ---------------- #
        # set up variables #
        # ---------------- #
        testMin = not math.isnan(minLimit)
        testMax = not math.isnan(maxLimit)
        testChange = not math.isnan(changeLimit)
        replValidity = invalidValidity.upper()
        if replValidity not in "MQR":
            raise TimeSeriesException("Invalid validity must be 'M', 'Q', or 'R'")
        validityComponent = {"M": "Missing", "Q": "Questionable", "R": "Rejected"}[
            replValidity
        ]
        qualityText = {
            "okay": "Screened Okay No_Range Original None None None Unprotected",
            "abs_val": f"Screened {validityComponent} No_Range Modified Automatic Missing Absolute_Value Unprotected",
            "rate_of_change": f"Screened {validityComponent} No_Range Modified Automatic Missing Rate_of_Change Unprotected",
        }
        okayCode = Quality(qualityText["okay"].split()).code
        missingCode = Quality("Missing").code
        absValueCode = Quality(qualityText["abs_val"].split()).code
        rateOfChangeCode = Quality(qualityText["rate_of_change"].split()).code
        # ------------------------------ #
        # get the DataFrame to work with #
        # ------------------------------ #
        target = self if in_place else self.copy()
        data = cast(pd.DataFrame, target._data)
        df = data.loc[data["selected"]] if self.has_selection else data
        # ---------------- #
        # do the screening #
        # ---------------- #
        protectedIndices = set(TimeSeries._protectedIndicies(df))
        missingIndices = set(df[df["value"].isna()].index)
        minIndices = set()
        maxIndices = set()
        changeIndices = set()
        if testMin:
            minIndices |= set(
                df[(df["value"] < minLimit) & (~df.index.isin(protectedIndices))].index
            )
        if testMax:
            maxIndices = set(
                df[(df["value"] > maxLimit) & (~df.index.isin(protectedIndices))].index
            )
        if testChange:
            changeIndices = set(
                df[
                    (abs(df["value"] - df["value"].shift(1)) > changeLimit)
                    & (~df.index.isin(protectedIndices))
                ].index
            )
        okayIndices = df.index.difference(
            list(
                protectedIndices
                | minIndices
                | maxIndices
                | changeIndices
                | missingIndices
            )
        )
        df.loc[df["value"].isna(), "quality"] = (
            df["quality"] & ~missingCode
        ) | missingCode
        df.loc[
            df.index.isin(okayIndices) & ~df.index.isin(protectedIndices), "quality"
        ] = okayCode
        df.loc[
            df.index.isin(minIndices) & ~df.index.isin(protectedIndices), "quality"
        ] |= absValueCode
        df.loc[
            df.index.isin(maxIndices) & ~df.index.isin(protectedIndices), "quality"
        ] |= absValueCode
        df.loc[
            df.index.isin(changeIndices) & ~df.index.isin(protectedIndices), "quality"
        ] |= rateOfChangeCode
        if replaceInvalidValue:
            df.loc[
                df.index.isin(minIndices) & ~df.index.isin(protectedIndices), "value"
            ] = invalidValueReplacement
            df.loc[
                df.index.isin(maxIndices) & ~df.index.isin(protectedIndices), "value"
            ] = invalidValueReplacement
            df.loc[
                df.index.isin(changeIndices) & ~df.index.isin(protectedIndices), "value"
            ] = invalidValueReplacement
            if math.isnan(invalidValueReplacement):
                # -------------------------------------------------- #
                # make sure quality indicates missing for NaN values #
                # -------------------------------------------------- #
                df.loc[
                    df.index.isin(minIndices) & ~df.index.isin(protectedIndices),
                    "quality",
                ] = (df["quality"] & ~missingCode) | missingCode
                df.loc[
                    df.index.isin(maxIndices) & ~df.index.isin(protectedIndices),
                    "quality",
                ] = (df["quality"] & ~missingCode) | missingCode
                df.loc[
                    df.index.isin(changeIndices) & ~df.index.isin(protectedIndices),
                    "quality",
                ] = (df["quality"] & ~missingCode) | missingCode
        # -------------------------------------------------- #
        # can't use .update(df) because it doesn't copy NaNs #
        # -------------------------------------------------- #
        for idx in df.index:
            data.loc[idx, "value"] = df.loc[idx, "value"]
            data.loc[idx, "quality"] = df.loc[idx, "quality"]

        if target.selection_state == SelectionState.TRANSIENT:
            target.iselect(Select.ALL)
        return target

    def iscreenWithValueRangeOrChange(
        self,
        minLimit: float = math.nan,
        maxLimit: float = math.nan,
        changeLimit: float = math.nan,
        replaceInvalidValue: bool = True,
        invalidValueReplacement: float = math.nan,
        invalidValidity: str = "M",
    ) -> "TimeSeries":
        """
        Screens this time series, setting values and/or quality codes where the values are outside the specified range
        or differ more than the specified change.

        Identical to calling `screenWithMaxMin2(..., in_place=True)`

        Args:
            minLimit (float): The minimum valid value. Values below this value will have their values and/or quality codes changed.
                Defaults to `math.nan` (test disabled).
            maxLimit (float): The maximum valid value. Values above this value will have their values and/or quality codes changed.
                Defaults to `math.nan` (test disabled).
            changeLimit (float): The maxium valid change from one value to the next. Values whose change (either increasing or decreasing)
                is greater that is will have their values and/or quality codes changed. Defaults to `math.nan` (test disabled).
            replaceInvalidValue (bool, optional): Replace screened-out values with the specified value. Defaults to True.
            invalidValueReplacement (float, optional): The value to replace screen-out values with if `replaceInvalidValue=True`.
                 Defaults to `math.nan` (missing value).
            invalidValidity (str, optional): Specifies the validity component of the quality code for screened-out values.
                May be "M" (Missing), "Q" (Questionable), or "R" (Rejected). Values flagged as missing also have the value modified to math.nan.
                Defaults to "M".

        Raises:
            TimeSeriesException: If the time series has no data or if the window is invalid.

        Returns:
            TimeSeries: The screened time series
        """
        return self.screenWithValueRangeOrChange(
            minLimit,
            maxLimit,
            changeLimit,
            replaceInvalidValue,
            invalidValueReplacement,
            invalidValidity,
        )

    @staticmethod
    def _screenWithDurationMagnitude(
        times: list[HecTime],
        values: list[float],
        qualities: Optional[list[int]],
        duration: Duration,
        minMissingLimit: float,
        minRejectLimit: float,
        minQuestionLimit: float,
        maxQuestionLimit: float,
        maxRejectLimit: float,
        maxMissingLimit: float,
        percentValidRequired: float,
    ) -> list[int]:
        totalCount = len(times)
        if totalCount < 2:
            raise TimeSeriesException("Operation requires a time series of length > 1")
        if qualities is None:
            qualitiesIn = totalCount * [0]
        else:
            qualitiesIn = qualities
        if len(values) != totalCount:
            raise TimeSeriesException(
                f"Lists of times and values must be of same length, got {totalCount} and {len(values)}"
            )
        if len(qualitiesIn) != totalCount:
            raise TimeSeriesException(
                f"Lists of times and qualities must be of same length, got {totalCount} and {len(qualitiesIn)}"
            )
        if (
            not math.isnan(percentValidRequired)
            and not 0 <= percentValidRequired <= 100
        ):
            raise TimeSeriesException(
                f"percentValidRequired must be in range 0..100, got {percentValidRequired}"
            )
        if duration.isBop:
            raise TimeSeriesException(
                "Method is currently suitable for End-of-Period durations only"
            )
        # ----------------- #
        # set the variables #
        # ----------------- #
        qualitiesOut = totalCount * [0]
        testMinMissing = not math.isnan(minMissingLimit)
        testMinReject = not math.isnan(minRejectLimit)
        testMinQuestion = not math.isnan(minQuestionLimit)
        testMaxQuestion = not math.isnan(maxQuestionLimit)
        testMaxReject = not math.isnan(maxRejectLimit)
        testMaxMissing = not math.isnan(maxMissingLimit)
        qualityText = {
            "okay": "Screened Okay No_Range Original None None None Unprotected",
            "missing": "Screened Missing No_Range Modified Automatic Missing Duration_Value Unprotected",
            "question": "Screened Questionable No_Range Original None None Duration_Value Unprotected",
            "reject": "Screened Rejected No_Range Original None None Duration_Value Unprotected",
        }
        okayCode = Quality(qualityText["okay"].split()).code
        missingCode = Quality(qualityText["missing"].split()).code
        questionCode = Quality(qualityText["question"].split()).code
        rejectCode = Quality(qualityText["reject"].split()).code
        baseTime = times[0] - (
            times[1] - times[0]
        )  # assume the first interval is equal to the second

        # ---------------- #
        # do the screening #
        # ---------------- #
        for last in range(totalCount):
            # --------------------------- #
            # don't screen invalid values #
            # --------------------------- #
            if (
                math.isnan(values[last])
                or math.isinf(values[last])
                or Quality(qualitiesIn[last]).score == 0
            ):
                continue
            # ---------------------------------------------------------------------------------------------- #
            # get the times that contribute to the accumulation at this time step for the specified duration #
            # ---------------------------------------------------------------------------------------------- #
            if last == 0:
                # ------------------------------------------------ #
                # assume the first interval is equal to the second #
                # ------------------------------------------------ #
                first = 0
                minutes = cast(TimeSpan, (times[last] - baseTime)).total_seconds() / 60
            else:
                for first in range(last + 1)[::-1]:
                    firstTime = baseTime if first == 0 else times[first - 1]
                    minutes = (
                        cast(TimeSpan, (times[last] - firstTime)).total_seconds() / 60
                    )
                    if minutes >= duration.minutes:
                        break
            if minutes < duration.minutes:
                continue
            span = range(first, last + 1)
            if first == last:
                # ------------------ #
                # single valid value #
                # ------------------ #
                total = values[last]
            else:
                # ----------------------------------------------- #
                # verify we have enough valid contributing values #
                # ----------------------------------------------- #
                valid = [
                    i
                    for i in span
                    if not math.isnan(values[i])
                    and not math.isinf(values[i])
                    and Quality(qualitiesIn[i]).score > 0
                ]
                if (
                    100.0 * len(valid) / len(span) < percentValidRequired
                ):  # will always be False with math.nan
                    continue
                # -------------------------------------------------- #
                # enumerate the contributions so we can adjust later #
                # -------------------------------------------------- #
                contrib = [
                    (values[i], 0)[
                        bool(
                            math.isnan(values[i])
                            or math.isinf(values[i])
                            or Quality(qualitiesIn[i]).score == 0
                        )
                    ]
                    for i in span
                ]
                total = sum(contrib)
            extraMinutes = minutes % duration.minutes
            # ----------------------------------------------------------- #
            # adjust for accumulations that exceed the specified duration #
            # ----------------------------------------------------------- #
            if extraMinutes:
                # ----------------------------------------------------------- #
                # take all of the extra out of the first value's contribution #
                # ----------------------------------------------------------- #
                firstTime = baseTime if first == 0 else times[first - 1]
                firstInterval = (
                    cast(TimeSpan, (times[first] - firstTime)).total_seconds() / 60
                )
                total -= contrib[0] * float(extraMinutes) / firstInterval
            # ------------------------- #
            # set the retuned qualities #
            # ------------------------- #
            if (testMinMissing and total < minMissingLimit) or (
                testMaxMissing and total > maxMissingLimit
            ):
                qualitiesOut[last] = missingCode
            elif (testMinReject and total < minRejectLimit) or (
                testMaxReject and total > maxRejectLimit
            ):
                qualitiesOut[last] = rejectCode
            elif (testMinQuestion and total < minQuestionLimit) or (
                testMaxQuestion and total > maxQuestionLimit
            ):
                qualitiesOut[last] = questionCode
            elif (
                testMinMissing
                or testMaxMissing
                or testMinReject
                or testMaxReject
                or testMinQuestion
                or testMaxQuestion
            ):
                qualitiesOut[last] = okayCode

        return qualitiesOut

    def screenWithDurationMagnitude(
        self,
        duration: Union[Duration, str],
        minMissingLimit: float = math.nan,
        minRejectLimit: float = math.nan,
        minQuestionLimit: float = math.nan,
        maxQuestionLimit: float = math.nan,
        maxRejectLimit: float = math.nan,
        maxMissingLimit: float = math.nan,
        percentValidRequired: float = 0.0,
        in_place: bool = False,
    ) -> "TimeSeries":
        """
        Screens a time series - either this one or a copy of this one - setting values and/or quality codes
        where the accumulated values over a specified duration are outside the specified range.

        Args:
            duration (Union[Duration, str]): The duration over which to screen the accumulated values. May be a
                [`Duration`](duration.html#Duration) object or the name of a valid duration (e.g., '6Hours', '1Day', ...). Accumulations for durations that are not even multiples
                of regular time series intervals may be used. Irregular time series may also be screened. The end of the duration is always positioned at the time (assumed to be EOP) of
                the accumulation to be screened. If the beginning of the duration does not align with a data time in the time series, a fraction of the first interval's accumulation is used.
                Only EOP durations may be used.
            minMissingLimit (float, optional): The minimum accumulation over the duration that is not flagged as missing. Values flagged as missing also have the value modified to math.nan. Defaults to `math.nan` (test disabled).
            minRejectLimit (float, optional): The minimum non-missing accumulation over the duration that is not flagged as rejected. Defaults to `math.nan` (test disabled).
            minQuestionLimit (float, optional): The minimum non-rejected, non-missing accumulation over the duration that is not flagged as questioned. Defaults to `math.nan` (test disabled).
            maxQuestionLimit (float, optional): The maximum non-rejected, non-missing accumulation over the duration that is not flagged as questioned. Defaults to `math.nan` (test disabled).
            maxRejectLimit (float, optional): The maximum non-missing accumulation over the duration that is not flagged as rejected. Defaults to `math.nan` (test disabled).
            maxMissingLimit (float, optional): The maximum accumulation over the duration that is not flagged as missing. Values flagged as missing also have the value modified to math.nan. Defaults to `math.nan` (test disabled).
            percentValidRequired (float, optional): The minimum percent (0..100) of valid values in the accumulation that will allow the value to be screened. Defaults to 0.
                Values are invalid if any of the following are true:
                * The quality is MISSING
                * The quality is REJECTED
                * The value is NaN
                * The value is Infinite
            in_place (bool, optional): Specifies whether to modify this time series (True) or a copy of it. Defaults to False.

        Raises:
            TimeSeriesException: If any of the following are true:
                * The time series has fewer than two values to be screened.
                * If `percentValidRequired` is not in the range 0..100
                * If the non-NaN limits are not in the following increasing-value order:
                    * `minMissingLimit`
                    * `minRejectLimit`
                    * `minQuestionLimit`
                    * `maxQuestionLimit`
                    * `maxRejectLimit`
                    * `maxMissingLimit`

        Returns:
            TimeSeries: The screened time series
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        # ---------------- #
        # set up variables #
        # ---------------- #
        if isinstance(duration, str):
            dur = Duration(duration)
        else:
            dur = duration
        # ------------------------------ #
        # get the DataFrame to work with #
        # ------------------------------ #
        target = self if in_place else self.copy()
        data = cast(pd.DataFrame, target._data)
        df = data.loc[data["selected"]] if self.has_selection else data
        dfProtected = df.loc[
            (df["quality"] & 0b1000_0000_0000_0000_0000_0000_0000_0000) != 0
        ].copy()
        # ---------------- #
        # do the screening #
        # ---------------- #
        quality_codes = TimeSeries._screenWithDurationMagnitude(
            list(map(HecTime, map(self.formatTimeForIndex, df.index.tolist()))),
            df["value"].tolist(),
            df["quality"].tolist(),
            dur,
            minMissingLimit,
            minRejectLimit,
            minQuestionLimit,
            maxQuestionLimit,
            maxRejectLimit,
            maxMissingLimit,
            percentValidRequired,
        )
        df.loc[:, "quality"] = df["quality"] & 0b0_0001 | np.array(quality_codes)
        df.loc[(df["quality"] & 0b0_0101 == 0b0_0101), "value"] = np.nan
        df.update(dfProtected)
        # -------------------------------------------------- #
        # can't use .update(df) because it doesn't copy NaNs #
        # -------------------------------------------------- #
        for idx in dfProtected.index:
            df.loc[idx, "value"] = dfProtected.loc[idx, "value"]
            df.loc[idx, "quality"] = dfProtected.loc[idx, "quality"]
        for idx in df.index:
            data.loc[idx, "value"] = df.loc[idx, "value"]
            data.loc[idx, "quality"] = df.loc[idx, "quality"]
        if target.selection_state == SelectionState.TRANSIENT:
            target.iselect(Select.ALL)
        return target

    def iscreenWithDurationMagnitude(
        self,
        duration: Union[Duration, str],
        minMissingLimit: float,
        minRejectLimit: float,
        minQuestionLimit: float,
        maxQuestionLimit: float,
        maxRejectLimit: float,
        maxMissingLimit: float,
        percentValidRequired: float = 0.0,
    ) -> "TimeSeries":
        """
        Screens this time series, setting values and/or quality codes where the accumulated values over a specified duration are outside the specified range.

        Identical to calling ts.screenDurationMagnitude(..., in_place=True)

        Args:
            duration (Union[Duration, str]): The duration over which to screen the accumulated values. May be a
                [`Duration`](duration.html#Duration) object or the name of a valid duration (e.g., '6Hours', '1Day', ...). Accumulations for durations that are not even multiples
                of regular time series intervals may be used. Irregular time series may also be screened. The end of the duration is always positioned at the time (assumed to be EOP) of
                the accumulation to be screened. If the beginning of the duration does not align with a data time in the time series, a fraction of the first interval's accumulation is used.
                Only EOP durations may be used.
            minMissingLimit (float, optional): The minimum accumulation over the duration that is not flagged as missing. Values flagged as missing also have the value modified to math.nan. Defaults to `math.nan` (test disabled).
            minRejectLimit (float, optional): The minimum non-missing accumulation over the duration that is not flagged as rejected. Defaults to `math.nan` (test disabled).
            minQuestionLimit (float, optional): The minimum non-rejected, non-missing accumulation over the duration that is not flagged as questioned. Defaults to `math.nan` (test disabled).
            maxQuestionLimit (float, optional): The maximum non-rejected, non-missing accumulation over the duration that is not flagged as questioned. Defaults to `math.nan` (test disabled).
            maxRejectLimit (float, optional): The maximum non-missing accumulation over the duration that is not flagged as rejected. Defaults to `math.nan` (test disabled).
            maxMissingLimit (float, optional): The maximum accumulation over the duration that is not flagged as missing. Values flagged as missing also have the value modified to math.nan. Defaults to `math.nan` (test disabled).
            percentValidRequired (float, optional): The minimum percent (0..100) of valid values in the accumulation that will allow the value to be screened. Defaults to 0
                Defaults to math.nan. Values are invalid if any of the following are true:
                * The quality is MISSING
                * The quality is REJECTED
                * The value is NaN
                * The value is Infinite

        Raises:
            TimeSeriesException: If any of the following are true:
                * The time series has fewer than two values to be screened.
                * If `percentValidRequired` is not in the range 0..100
                * If the non-NaN limits are not in the following increasing-value order:
                    * `minMissingLimit`
                    * `minRejectLimit`
                    * `minQuestionLimit`
                    * `maxQuestionLimit`
                    * `maxRejectLimit`
                    * `maxMissingLimit`

        Returns:
            TimeSeries: The screened time series
        """
        return self.screenWithDurationMagnitude(
            duration,
            minMissingLimit,
            minRejectLimit,
            minQuestionLimit,
            maxQuestionLimit,
            maxRejectLimit,
            maxMissingLimit,
            percentValidRequired,
            False,
        )

    @staticmethod
    def _screenWithConstantValue(
        times: list[HecTime],
        values: list[float],
        qualities: Optional[list[int]],
        duration: Duration,
        missingLimit: float,
        rejectLimit: float,
        questionLimit: float,
        minThreshold: float,
        percentValidRequired: float,
    ) -> list[int]:
        totalCount = len(times)
        if totalCount < 2:
            raise TimeSeriesException("Operation requires a time series of length > 1")
        if qualities is None:
            qualitiesIn = totalCount * [0]
        else:
            qualitiesIn = qualities
        if len(values) != totalCount:
            raise TimeSeriesException(
                f"Lists of times and values must be of same length, got {totalCount} and {len(values)}"
            )
        if len(qualitiesIn) != totalCount:
            raise TimeSeriesException(
                f"Lists of times and qualities must be of same length, got {totalCount} and {len(qualitiesIn)}"
            )
        if (
            not math.isnan(percentValidRequired)
            and not 0 <= percentValidRequired <= 100
        ):
            raise TimeSeriesException(
                f"percentValidRequired must be in range 0..100, got {percentValidRequired}"
            )
        # ----------------- #
        # set the variables #
        # ----------------- #
        qualitiesOut = totalCount * [0]
        testMissing = not math.isnan(missingLimit)
        testReject = not math.isnan(rejectLimit)
        testQuestion = not math.isnan(questionLimit)
        if testMissing:
            if testReject and missingLimit >= rejectLimit:
                raise TimeSeriesException(
                    "Missing limit must be less than Reject limit"
                )
            if testQuestion and missingLimit >= questionLimit:
                raise TimeSeriesException(
                    "Missing limit must be less than Question limit"
                )
        if testReject:
            if testQuestion and rejectLimit >= questionLimit:
                raise TimeSeriesException(
                    "Reject limit must be less than Question limit"
                )
        qualityText = {
            "okay": "Screened Okay No_Range Original None None None Unprotected",
            "missing": "Screened Missing No_Range Modified Automatic Missing Duration_Value Unprotected",
            "question": "Screened Questionable No_Range Original None None Duration_Value Unprotected",
            "reject": "Screened Rejected No_Range Original None None Duration_Value Unprotected",
        }
        okayCode = Quality(qualityText["okay"].split()).code
        missingCode = Quality(qualityText["missing"].split()).code
        questionCode = Quality(qualityText["question"].split()).code
        rejectCode = Quality(qualityText["reject"].split()).code
        # ---------------- #
        # do the screening #
        # ---------------- #
        for last in range(1, totalCount):
            # --------------------------- #
            # don't screen invalid values #
            # --------------------------- #
            if (
                math.isnan(values[last])
                or math.isinf(values[last])
                or Quality(qualitiesIn[last]).score == 0
            ):
                continue
            if values[last] < minThreshold:  # always False if minThreshold is math.nan:
                continue
            # ---------------------------------------------------------------------------------------------- #
            # get the times that contribute to the accumulation at this time step for the specified duration #
            # ---------------------------------------------------------------------------------------------- #
            for first in range(last + 1)[::-1]:
                minutes = (
                    cast(TimeSpan, (times[last] - times[first])).total_seconds() / 60
                )
                if minutes >= duration.minutes:
                    break
            if minutes < duration.minutes:
                continue
            span = range(first, last + 1)
            # ---------------------------------- #
            # verify we have enough valid values #
            # ---------------------------------- #
            valid = [
                values[i]
                for i in span
                if not math.isnan(values[i])
                and not math.isinf(values[i])
                and Quality(qualitiesIn[i]).score > 0
            ]
            if (
                100.0 * len(valid) / len(span) < percentValidRequired
            ):  # will always be False with math.nan
                continue
            # ---------------------------------- #
            # get the max change in the duration #
            # ---------------------------------- #
            maxChange = max(valid) - min(valid)
            # ------------------------- #
            # set the retuned qualities #
            # ------------------------- #
            if testMissing and maxChange < missingLimit:
                qualitiesOut[last] = missingCode
            elif testReject and maxChange < rejectLimit:
                qualitiesOut[last] = rejectCode
            elif testQuestion and maxChange < questionLimit:
                qualitiesOut[last] = questionCode
            elif testMissing or testReject or testQuestion:
                qualitiesOut[last] = okayCode

        return qualitiesOut

    def screenWithConstantValue(
        self,
        duration: Union[Duration, str],
        missingLimit: float = math.nan,
        rejectLimit: float = math.nan,
        questionLimit: float = math.nan,
        minThreshold: float = math.nan,
        percentValidRequired: float = math.nan,
        in_place: bool = False,
    ) -> "TimeSeries":
        """
        Screens a time series - either this one or a copy of this one - setting values and/or quality codes
        where the value changes over a specified duration are below specified limits.

        Args:
            duration (Union[Duration, str]): The duration over which to screen the value changes. May be a
                [`Duration`](duration.html#Duration) object or the name of a valid duration (e.g., '6Hours', '1Day', ...).
            missingLimit (float, optional): The mininum value change over the duration that is not flagged as missing. Values flagged as missing also have the value modified to math.nan. Defaults to math.nan (test not performed).
            rejectLimit (float, optional): The mininum non-missing value change over the duration that is not flagged as rejected. Defaults to math.nan (test not performed).
            questionLimit (float, optional): The mininum non-rejected, non-missing value change over the duration that is not flagged as questionable. Defaults to math.nan (test not performed).
            minThreshold (float, optional): Values less than this will not be screened. Defaults to math.nan (test not performed)
            percentValidRequired (float, optional): The minimum percent (0..100) of valid values in the duration that will allow the value to be screened. Defaults to math.nan (test not performed).
                Defaults to math.nan. Values are invalid if any of the following are true:
                * The quality is MISSING
                * The quality is REJECTED
                * The value is NaN
                * The value is Infinite
            in_place (bool, optional): Specifies whether to modify this time series (True) or a copy of it. Defaults to False.

        Raises:
            TimeSeriesException: If any of the following are true:
                * The time series has fewer than two values to be screened.
                * If `percentValidRequired` is not in the range 0..100
                * If the non-NaN limits are not in the following increasing-value order:
                    * `missingLimit`
                    * `rejectLimit`
                    * `questionLimit`

        Returns:
            TimeSeries: The screened time series
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        # ---------------- #
        # set up variables #
        # ---------------- #
        if isinstance(duration, str):
            dur = Duration(duration)
        else:
            dur = duration
        # ------------------------------ #
        # get the DataFrame to work with #
        # ------------------------------ #
        target = self if in_place else self.copy()
        data = cast(pd.DataFrame, target._data)
        df = data.loc[data["selected"]] if self.has_selection else data
        dfProtected = df.loc[
            (df["quality"] & 0b1000_0000_0000_0000_0000_0000_0000_0000) != 0
        ].copy()
        # ---------------- #
        # do the screening #
        # ---------------- #
        quality_codes = TimeSeries._screenWithConstantValue(
            list(map(HecTime, map(self.formatTimeForIndex, df.index.tolist()))),
            df["value"].tolist(),
            df["quality"].tolist(),
            dur,
            missingLimit,
            rejectLimit,
            questionLimit,
            minThreshold,
            percentValidRequired,
        )
        df.loc[:, "quality"] = df["quality"] & 0b0_0001 | np.array(quality_codes)
        df.loc[(df["quality"] & 0b0_0101 == 0b0_0101), "value"] = np.nan
        df.update(dfProtected)
        # -------------------------------------------------- #
        # can't use .update(df) because it doesn't copy NaNs #
        # -------------------------------------------------- #
        for idx in dfProtected.index:
            df.loc[idx, "value"] = dfProtected.loc[idx, "value"]
            df.loc[idx, "quality"] = dfProtected.loc[idx, "quality"]
        for idx in df.index:
            data.loc[idx, "value"] = df.loc[idx, "value"]
            data.loc[idx, "quality"] = df.loc[idx, "quality"]
        if target.selection_state == SelectionState.TRANSIENT:
            target.iselect(Select.ALL)
        return target

    def iscreenWithConstantValue(
        self,
        duration: Union[Duration, str],
        missingLimit: float = math.nan,
        rejectLimit: float = math.nan,
        questionLimit: float = math.nan,
        minThreshold: float = math.nan,
        percentValidRequired: float = math.nan,
    ) -> "TimeSeries":
        """
        Screens a this time series, setting values and/or quality codes where the value changes over a specified duration are below specified limits.

        Args:
            duration (Union[Duration, str]): The duration over which to screen the value changes. May be a
                [`Duration`](duration.html#Duration) object or the name of a valid duration (e.g., '6Hours', '1Day', ...).
            missingLimit (float, optional): The mininum value change over the duration that is not flagged as missing. Values flagged as missing also have the value modified to math.nan. Defaults to math.nan (test not performed).
            rejectLimit (float, optional): The mininum non-missing value change over the duration that is not flagged as rejected. Defaults to math.nan (test not performed).
            questionLimit (float, optional): The mininum non-rejected, non-missing value change over the duration that is not flagged as questionable. Defaults to math.nan (test not performed).
            minThreshold (float, optional): Values less than this will not be screened. Defaults to math.nan (test not performed)
            percentValidRequired (float, optional): The minimum percent (0..100) of valid values in the duration that will allow the value to be screened. Defaults to math.nan (test not performed).
                Defaults to math.nan. Values are invalid if any of the following are true:
                * The quality is MISSING
                * The quality is REJECTED
                * The value is NaN
                * The value is Infinite

        Raises:
            TimeSeriesException: If any of the following are true:
                * The time series has fewer than two values to be screened.
                * If `percentValidRequired` is not in the range 0..100
                * If the non-NaN limits are not in the following increasing-value order:
                    * `missingLimit`
                    * `rejectLimit`
                    * `questionLimit`

        Returns:
            TimeSeries: The screened time series
        """
        return self.screenWithConstantValue(
            duration,
            missingLimit,
            rejectLimit,
            questionLimit,
            minThreshold,
            percentValidRequired,
            False,
        )

    def screenWithForwardMovingAverage(
        self,
        window: int,
        onlyValid: bool,
        useReduced: bool,
        diffLimit: float,
        failedValidity: str = "M",
        in_place: bool = False,
    ) -> "TimeSeries":
        """
        Screens a time series - either this one or a copy of this one - setting values and/or quality codes where the value differ from
        those of a forward moving averge of the time series by a specified amount.

        Args:
            window (int): The number of values to average over. See [`forwardMovingAverage()`](#TimeSeries.forwardMovingAverage) for more info.
            onlyValid (bool): Specifies whether to only average over windows where every value is
                valid. See [`forwardMovingAverage()`](#TimeSeries.forwardMovingAverage) for more info.
            useReduced (bool): Specifies whether to allow averages using less than window number
                of values will be computed at the beginning of the times series. See [`forwardMovingAverage()`](#TimeSeries.forwardMovingAverage) for more info.
            diffLimit (float): The maximum difference between a value and the value at the same time in the forward moving average
                that will not be flagged as questionable, rejected, or missing. See [`forwardMovingAverage()`](#TimeSeries.forwardMovingAverage) for more info.
            failedValidity (str, optional): Specifies the validity portion of the quality code for failed values
                Must be one of "M" (Missing), "R" (Rejected) or "Q" (Questionable). Values flagged as missing also have the value modified to math.nan.
                Defaults to "M".
            in_place (bool, optional): Specifies whether to modify this time series (True) or a copy of it. Defaults to False.

        Raises:
            TimeSeriesException: If any of the following are true:
                * The time series has no data
                * The window is invalid
                * `failedValidity` is not one of "M", "R", or "Q"

        Returns:
            TimeSeries: The screened time series
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        # ---------------- #
        # set up variables #
        # ---------------- #
        if failedValidity.upper() not in "MQR":
            raise TimeSeriesException("Failed validity must be 'M', 'Q', or 'R'")
        validityComponent = {"M": "Missing", "Q": "Questionable", "R": "Rejected"}[
            failedValidity.upper()
        ]
        qualityText = {
            "invalid-missing": "Screened Missing No_Range Original None None None Unprotected",
            "screened-okay": "Screened Okay No_Range Original None None None Unprotected",
            "screened-missing": f"Screened {validityComponent} No_Range Modified Automatic Missing Relative_Value Unprotected",
            "screened-other": f"Screened {validityComponent} No_Range Original None None Relative_Value Unprotected",
        }
        invalidMissingCode = Quality(qualityText["invalid-missing"].split()).code
        screenedOkayCode = Quality(qualityText["screened-okay"].split()).code
        screenedMissingCode = Quality(qualityText["screened-missing"].split()).code
        screenedOtherCode = Quality(qualityText["screened-other"].split()).code
        # ------------------------------ #
        # get the DataFrame to work with #
        # ------------------------------ #
        target = self if in_place else self.copy()
        data = cast(pd.DataFrame, target._data)
        df = data.loc[data["selected"]] if self.has_selection else data
        dfProtected = df.loc[
            (df["quality"] & 0b1000_0000_0000_0000_0000_0000_0000_0000) != 0
        ].copy()
        # ---------------- #
        # do the screening #
        # ---------------- #
        missingIndices = df.index[pd.isna(df["value"]) | np.isinf(df["value"])].tolist()
        df.loc[missingIndices, "value"] = np.nan
        df.loc[missingIndices, "quality"] = invalidMissingCode
        for idx in df.index:
            data.loc[idx, "value"] = df.loc[idx, "value"]
            data.loc[idx, "quality"] = df.loc[idx, "quality"]
        dfAverage = cast(
            pd.DataFrame,
            target.forwardMovingAverage(window, onlyValid, useReduced).data,
        )
        for idx in set(df.index) - set(missingIndices):
            currentQualityCode = df.loc[idx, "quality"]
            if np.isnan(dfAverage.loc[idx, "value"]):
                continue
            if abs(dfAverage.loc[idx, "value"] - df.loc[idx, "value"]) > diffLimit:
                if failedValidity.upper() == "M":
                    df.loc[idx, "quality"] = (
                        currentQualityCode & 0b0_0001 | screenedMissingCode
                    )
                    df.loc[idx, "value"] = np.nan
                else:
                    df.loc[idx, "quality"] = (
                        currentQualityCode & 0b0_0001 | screenedOtherCode
                    )
            elif currentQualityCode & 1 == 0:
                df.loc[idx, "quality"] = screenedOkayCode
        # --------------- #
        # set the results #
        # --------------- #
        for idx in dfProtected.index:
            df.loc[idx, "value"] = dfProtected.loc[idx, "value"]
            df.loc[idx, "quality"] = dfProtected.loc[idx, "quality"]
        for idx in df.index:
            data.loc[idx, "value"] = df.loc[idx, "value"]
            data.loc[idx, "quality"] = df.loc[idx, "quality"]
        if target.selection_state == SelectionState.TRANSIENT:
            target.iselect(Select.ALL)
        return target

    def iscreenWithForwardMovingAverage(
        self,
        window: int,
        onlyValid: bool,
        useReduced: bool,
        diffLimit: float,
        invalidValidity: str = "M",
    ) -> "TimeSeries":
        """
        Screens this time series, setting values and/or quality codes where the value differ from
        those of a forward moving averge of the time series by a specified amount.

        Identical to calling [`screenWithForwardMovingAverage()`](#TimeSeries.screenWithForwardMovingAverage) with `in_place=True`.

        Args:
            window (int): The number of values to average over. See [`forwardMovingAverage()`](#TimeSeries.forwardMovingAverage) for more info.
            onlyValid (bool): Specifies whether to only average over windows where every value is
                valid. See [`forwardMovingAverage()`](#TimeSeries.forwardMovingAverage) for more info.
            useReduced (bool): Specifies whether to allow averages using less than window number
                of values will be computed at the beginning of the times series. See [`forwardMovingAverage()`](#TimeSeries.forwardMovingAverage) for more info.
            diffLimit (float): The maximum difference between a value and the value at the same time in the forward moving average
                that will not be flagged as questionable, rejected, or missing. See [`forwardMovingAverage()`](#TimeSeries.forwardMovingAverage) for more info.
            failedValidity (str, optional): Specifies the validity portion of the quality code for failed values
                Must be one of "M" (Missing), "R" (Rejected) or "Q" (Questionable). Values flagged as missing also have the value modified to math.nan.
                Defaults to "M".
            in_place (bool, optional): Specifies whether to modify this time series (True) or a copy of it. Defaults to False.

        Raises:
            TimeSeriesException: If any of the following are true:
                * The time series has no data
                * The window is invalid
                * `failedValidity` is not one of "M", "R", or "Q"

        Returns:
            TimeSeries: The screened time series
        """
        return self.screenWithForwardMovingAverage(
            window,
            onlyValid,
            useReduced,
            diffLimit,
            invalidValidity,
            False,
        )

    def estimateMissingValues(
        self,
        maxMissingCount: int,
        accumulation: bool = False,
        estimateRejected: bool = True,
        setQuestionable: bool = True,
        in_place: bool = False,
    ) -> "TimeSeries":
        """
        Estimates missing values in a time series using specified criteria, and returns the estimated time series (either this time series or a copy of it).
        Values are estimated using linear interpolation between the bounding valid values

        Args:
            maxMissingCount (int): The maximum number of consecutive missing values that will be replaced with estimates.
                Groups of consecutive missing values larger than this number remain missing (except see `accumulation`).
            accumulation (bool, optional): Specifies whether the time series is an accumulation (e.g., cumulative precipitaion).
                The estimation behavior for accumulation time series differs in that
                * If the bounding valid values for a group of consecutive missing values decrease with increasing time, no estimations are performed
                * If the bounding valid values for a group of consecutive missing values are equal, the all missing values in the group are replaced
                    with the same value, without regard to `maxMissingCount`
                Defaults to False.
            estimateRejected (bool, optional): Specifies whether to treat values in the time series with Rejected quality as missing. Defaults to True.
            setQuestionable (bool, optional): Specifies whether to set the quality for estimated values to Questionable. If False, quality is set to Okay. Defaults to True.
            in_place (bool, optional): Specfies whether to modify and return this time seires (True) or a copy of this time series (False). Defaults to False.

        Raises:
            TimeSeriesException: If there are no values in the time series

        Returns:
            TimeSeries: The estimated time series
        """
        if self._data is None:
            raise TimeSeriesException("Operation is invalid with empty time series.")
        # ---------------- #
        # set up variables #
        # ---------------- #
        qualityCode = [
            Quality(
                "Screened Okay No_Range Modified Automatic Lin_Interp None Unprotected".split()
            ).code,
            Quality(
                "Screened Questionable No_Range Modified Automatic Lin_Interp None Unprotected".split()
            ).code,
        ][int(setQuestionable)]
        # ------------------------------ #
        # get the DataFrame to work with #
        # ------------------------------ #
        target = self if in_place else self.copy()
        data = cast(pd.DataFrame, target._data)
        df = data.loc[data["selected"]] if self.has_selection else data
        dfProtected = df.loc[
            (df["quality"] & 0b1000_0000_0000_0000_0000_0000_0000_0000) != 0
        ].copy()
        # ----------------- #
        # do the estimation #
        # ----------------- #
        if estimateRejected:
            mask = (df["quality"] & 0b1_1111) == 0b1_0001
            df.loc[mask, "value"] = np.nan
        original = df["value"].copy()
        if accumulation:

            def conditional_interpolation(
                df: pd.DataFrame, max_nan: int
            ) -> pd.DataFrame:
                values = df["value"]
                is_nan = values.isna()
                groups = (
                    is_nan != is_nan.shift()
                ).cumsum()  # Identify groups of consecutive NaN/Non-NaN
                # Iterate through groups
                for group_id, group in df.groupby(groups):
                    if not group["value"].isna().any():
                        continue  # Skip non-NaN groups
                    # Find indices for the current NaN group
                    nan_indices = group.index
                    prev_pos = cast(int, df.index.get_loc(nan_indices[0])) - 1
                    next_pos = cast(int, df.index.get_loc(nan_indices[-1])) + 1
                    # Check bounds
                    if prev_pos < 0 or next_pos >= len(values):
                        continue  # Skip interpolation if out of bounds
                    # Get values before and after the NaNs
                    prev_index = df.index[prev_pos]
                    next_index = df.index[next_pos]
                    prev_value = values[prev_index]
                    next_value = values[next_index]
                    # Apply conditions
                    if next_value < prev_value:
                        continue  # Skip interpolation if the next value is less than the previous
                    if prev_value == next_value:
                        df.loc[nan_indices, "value"] = (
                            prev_value  # Fill with the same value
                        )
                        continue
                    # Check if NaN count exceeds the limit
                    if len(nan_indices) > max_nan:
                        continue
                    # Perform interpolation
                    df.loc[nan_indices, "value"] = values.interpolate().loc[nan_indices]
                return df

            df = conditional_interpolation(df, maxMissingCount)
        else:

            def interp(series: pd.Series, max_nan: int) -> pd.Series:  # type: ignore
                # get a mask of NaN locations
                is_nan = series.isna()
                # identify groups of consecutive values
                groups = (is_nan != is_nan.shift()).cumsum()
                # count the number of NaNs in each group
                nan_counts = is_nan.groupby(groups).transform("sum")
                # replace NaNs we don't want interpolated
                mask = ~((nan_counts > max_nan) & is_nan)
                nan_indicies = mask.where(~mask).dropna().index
                series[nan_indicies] = 0
                # interpolate the remaining NaNs and restore the un-interpolated NaNs
                series = series.interpolate()
                series[nan_indicies] = np.nan
                return series

            df.loc[:, "value"] = interp(df["value"].copy(), maxMissingCount)
        modified = (original.isna()) & (df["value"].notna())
        df.loc[modified, "quality"] = qualityCode
        # --------------- #
        # set the results #
        # --------------- #
        for idx in dfProtected.index:
            df.loc[idx, "value"] = dfProtected.loc[idx, "value"]
            df.loc[idx, "quality"] = dfProtected.loc[idx, "quality"]
        for idx in df.index:
            data.loc[idx, "value"] = df.loc[idx, "value"]
            data.loc[idx, "quality"] = df.loc[idx, "quality"]
        if target.selection_state == SelectionState.TRANSIENT:
            target.iselect(Select.ALL)
        return target

    def iestimateMissingValues(
        self,
        maxMissingCount: int,
        accumulation: bool = False,
        estimateRejected: bool = True,
        setQuestionable: bool = True,
    ) -> "TimeSeries":
        """
        Estimates missing values in this time series using specified criteria, and returns the estimated time series.
        Values are estimated using linear interpolation between the bounding valid values.
        Identical to calling estimtateMissingValues(..., in_place=True)

        Args:
            maxMissingCount (int): The maximum number of consecutive missing values that will be replaced with estimates.
                Groups of consecutive missing values larger than this number remain missing (except see `accumulation`).
            accumulation (bool, optional): Specifies whether the time series is an accumulation (e.g., cumulative precipitaion).
                The estimation behavior for accumulation time series differs in that
                * If the bounding valid values for a group of consecutive missing values decrease with increasing time, no estimations are performed
                * If the bounding valid values for a group of consecutive missing values are equal, the all missing values in the group are replaced
                    with the same value, without regard to `maxMissingCount`
                Defaults to False.
            estimateRejected (bool, optional): Specifies whether to treat values in the time series with Rejected quality as missing. Defaults to True.
            setQuestionable (bool, optional): Specifies whether to set the quality for estimated values to Questionable. If False, quality is set to Okay. Defaults to True.

        Raises:
            TimeSeriesException: If there are no values in the time series

        Returns:
            TimeSeries: The estimated time series
        """
        return self.estimateMissingValues(
            maxMissingCount,
            accumulation,
            estimateRejected,
            setQuestionable,
            in_place=True,
        )

    def hasSameTimes(self, other: "TimeSeries") -> bool:
        """
        Returns whether another time series has the same times as this time series.

        Args:
            other (TimeSeries): The other time series

        Returns:
            bool: Whether another time series has the same times as this time series.
        """
        return other.times == self.times

    def expand(
        self,
        startTime: Optional[Union[str, datetime, HecTime]] = None,
        endTime: Optional[Union[str, datetime, HecTime]] = None,
        in_place: bool = False,
    ) -> "TimeSeries":
        """
        Expands a regular time seires (either this one or a copy of this one) so that there are no gaps in time
        (fills gaps with missing values) and returns the expanded time series. If `startTime` and/or `endTime`
        are specified, the times between the startTime and the first time and between the last time and the endTime
        are considered as gaps to be filled.

        Irregular time series (including pseudo-regular time series) are not affected.

        Does not alter any selection, even if selection state is `SelectionState.TRANSIENT`. Selected items remain
        selected after expansion even though their location in the data may change.

        Args:
            startTime (Optional[Union[str, datetime, HecTime]], optional): The beginning of the timespan before the first time
                to fill with missing values. Does not need to fall on the time series interval. If not at least one full
                interval prior to the first time, no missing values will be inserted before the first time. Defaults to None.
            endTime (Optional[Union[str, datetime, HecTime]], optional): The end of the timespan after the last time to fill
                with missing values. Does not need to fall on the time series interval. If not at least one full interval after
                the last time, no missing values will be inserted after the last time. Defaults to None.
            in_place (bool, optional): Specifies whether to expand this time series (True) or a copy of this time series (False).
            Defaults to False.

        Returns:
            TimeSeries: The expanded time series
        """
        # --------------------------------------- #
        # short circuit for irregular time series #
        # --------------------------------------- #
        if self.is_any_irregular:
            return self if in_place else self.copy()
        # ---------------- #
        # set up variables #
        # ---------------- #
        if startTime and not isinstance(startTime, HecTime):
            startTime = HecTime(startTime)
        if endTime and not isinstance(endTime, HecTime):
            endTime = HecTime(endTime)
        tsvs = self.tsv
        expandedTsvs = []
        missingQuantity = UnitQuantity(math.nan, self.unit)
        missingQuality = Quality("Missing")
        selected = self.selected
        selectedIndices = [i for i in range(len(selected)) if selected[i]]
        # ------------------------------ #
        # get the DataFrame to work with #
        # ------------------------------ #
        target = self if in_place else self.copy()
        if (
            not target._expanded
            or startTime
            and startTime < tsvs[0].time
            or endTime
            and endTime > tsvs[-1].time
        ):
            # ---------------- #
            # do the expansion #
            # ---------------- #
            offset = 0
            if startTime and startTime < tsvs[0].time:
                lastTime = cast(HecTime, tsvs[0].time.clone())
                while lastTime > cast(HecTime, startTime):
                    lastTime -= self.interval
                while lastTime < tsvs[0].time:
                    tsv = TimeSeriesValue(
                        lastTime.clone(), missingQuantity, missingQuality
                    )
                    expandedTsvs.append(tsv)
                    lastTime += self.interval
                    offset += 1
                selectedIndices = [i + offset for i in selectedIndices]
            offsets = {}
            for i in range(1, len(tsvs)):
                offsets[i] = 0
                expandedTsvs.append(tsvs[i - 1])
                lastTime = tsvs[i - 1].time + self.interval
                if lastTime < tsvs[i].time:
                    while lastTime < tsvs[i].time:
                        tsv = TimeSeriesValue(
                            lastTime.clone(), missingQuantity, missingQuality
                        )
                        expandedTsvs.append(tsv)
                        lastTime += self.interval
                        offsets[i] += 1
            for idx in sorted(offsets):
                offset = offsets[idx]
                selectedIndices = [
                    i if i < idx else i + offset for i in selectedIndices
                ]
            expandedTsvs.append(tsvs[-1])
            if endTime and endTime > tsvs[-1].time:
                lastTime = tsvs[-1].time + self.interval
                while lastTime <= endTime:
                    tsv = TimeSeriesValue(
                        lastTime.clone(), missingQuantity, missingQuality
                    )
                    expandedTsvs.append(tsv)
                    lastTime += self.interval
            # --------------- #
            # set the results #
            # --------------- #
            if any(selected):
                target._data = pd.DataFrame(
                    {
                        "value": [tsv.value.magnitude for tsv in expandedTsvs],
                        "quality": [tsv.quality.code for tsv in expandedTsvs],
                        "selected": [
                            True if i in selectedIndices else False
                            for i in range(len(expandedTsvs))
                        ],
                    },
                    index=pd.DatetimeIndex(
                        [tsv.time.datetime() for tsv in expandedTsvs], name="time"
                    ),
                )
            else:
                target._data = pd.DataFrame(
                    {
                        "value": [tsv.value.magnitude for tsv in expandedTsvs],
                        "quality": [tsv.quality.code for tsv in expandedTsvs],
                    },
                    index=pd.DatetimeIndex(
                        [tsv.time.datetime() for tsv in expandedTsvs], name="time"
                    ),
                )
            target._expanded = True
        return target

    def iexpand(
        self,
        startTime: Optional[Union[str, datetime, HecTime]] = None,
        endTime: Optional[Union[str, datetime, HecTime]] = None,
    ) -> "TimeSeries":
        """
        Expands a regular time seires in place so that there are no gaps in time (fills gaps with missing values) and returns
        the expanded time series. If `startTime` and/or `endTime` are specified, the times between the startTime and the first
        time and between the last time and the endTime are considered as gaps to be filled.

        Irregular time series (including pseudo-regular time series) are not affected.

        Does not alter any selection, even if selection state is `SelectionState.TRANSIENT`. Selected items remain
        selected after expansion even though their location in the data may change.

        Identical to calling expand(... in_place=True)

        Args:
            startTime (Optional[Union[str, datetime, HecTime]], optional): The beginning of the timespan before the first time
                to fill with missing values. Does not need to fall on the time series interval. If not at least one full
                interval prior to the first time, no missing values will be inserted before the first time. Defaults to None.
            endTime (Optional[Union[str, datetime, HecTime]], optional): The end of the timespan after the last time to fill
                with missing values. Does not need to fall on the time series interval. If not at least one full interval after
                the last time, no missing values will be inserted after the last time. Defaults to None.

        Returns:
            TimeSeries: The expanded time series
        """
        return self.expand(startTime, endTime, in_place=True)

    def collapse(self, in_place: bool = False) -> "TimeSeries":
        """
        Collapses a regular time series (either this one or a copy of this one), removing all missing values unless they are
        either protected or marked as part of the current selection.

        Irregular time series (including pseudo-regular time series) are not affected.

        Does not alter any selection, even if selection state is `SelectionState.TRANSIENT`. Selected items remain
        selected after collapse even though their location in the data may change.

        Args:
            in_place (bool, optional): Specifies whether to collapse this time series (True) or a copy of this time series (False).
            Defaults to False.

        Returns:
            TimeSeries: The collapsed time series
        """
        # --------------------------------------- #
        # short circuit for irregular time series #
        # --------------------------------------- #
        if self.is_any_irregular:
            return self if in_place else self.copy()
        # ------------------------------ #
        # get the DataFrame to work with #
        # ------------------------------ #
        target = self if in_place else self.copy()
        df = cast(pd.DataFrame, target._data)  # does not recognize selection
        # --------------- #
        # set the results #
        # --------------- #
        if self.has_selection:
            condition = (
                ~df["value"].isna()
                | ((df["quality"] & (1 << 31)) != 0)
                | df["selected"]
            )
        else:
            condition = ~df["value"].isna() | ((df["quality"] & (1 << 31)) != 0)
        target._data = df[condition]
        target._expanded = False
        return target

    def icollapse(self) -> "TimeSeries":
        """
        Collapses a regular time series in place, removing all missing values unless they are either protected or marked
        as part of the current selection.

        Irregular time series (including pseudo-regular time series) are not affected.

        Does not alter any selection, even if selection state is `SelectionState.TRANSIENT`. Selected items remain
        selected after collapse even though their location in the data may change.

        Identical to calling collapse(in_place=True)

        Returns:
            TimeSeries: The collapsed time series
        """
        return self.collapse(in_place=True)

    def trim(self, in_place: bool = False) -> "TimeSeries":
        """
        Trims a regular time series (either this one or a copy of this one), removing all missing values from the beginning and
        end of the time series unless they are either protected or marked as part of the current selection.

        Irregular time series (including pseudo-regular time series) are not affected.

        Does not alter any selection, even if selection state is `SelectionState.TRANSIENT`. Selected items remain
        selected after trim even though their location in the data may change.

        Args:
            in_place (bool, optional): Specifies whether to trim this time series (True) or a copy of this time series (False).
            Defaults to False.

        Returns:
            TimeSeries: The trimmed time series
        """
        # --------------------------------------- #
        # short circuit for irregular time series #
        # --------------------------------------- #
        if self.is_any_irregular:
            return self if in_place else self.copy()
        # ------------------------------ #
        # get the DataFrame to work with #
        # ------------------------------ #
        target = self if in_place else self.copy()
        df = cast(pd.DataFrame, target._data)  # does not recognize selection
        # --------------- #
        # set the results #
        # --------------- #
        if self.has_selection:
            condition = (
                ~df["value"].isna()
                | ((df["quality"] & (1 << 31)) != 0)
                | df["selected"]
            )
        else:
            condition = ~df["value"].isna() | ((df["quality"] & (1 << 31)) != 0)
        first_valid = condition.idxmax()  # First index where condition is True
        last_valid = condition[::-1].idxmax()  # Last index where condition is True
        target._data = df.loc[first_valid:last_valid]  # type: ignore
        return target

    def itrim(self) -> "TimeSeries":
        """
        Trims a regular time series in place, removing all missing values from the beginning and end of the time series
        unless they are either protected or marked as part of the current selection.

        Irregular time series (including pseudo-regular time series) are not affected.

        Does not alter any selection, even if selection state is `SelectionState.TRANSIENT`. Selected items remain
        selected after trim even though their location in the data may change.

        Identical to calling trim(in_place=True)

        Returns:
            TimeSeries: The trimmed time series
        """
        return self.trim(in_place=True)

    def merge(
        self, other: Union["TimeSeries", List["TimeSeries"]], in_place: bool = False
    ) -> "TimeSeries":
        """
        Merges one or more time series into either this time series or a copy of it, and returns the merged time series.

        When the same time exists while merging, the following precedence is followed:
        * other protected value (incoming protected trumps existing protected)
        * this protected value
        * this unprotected value if it is not NaN or infinite
        * other unprotected value if it is not NaN or infinte

        Args:
            other (Union[&quot;TimeSeries&quot;, List[&quot;TimeSeries&quot;]]): The other times series (one or a list) to merge.
                If a list, each other time series is merged in sequence, with earlier results acting as this time series for later merges
            in_place (bool, optional): Specifies whether to merge into this time series (True) or a copy of it (False). Defaults to False.

        Raises:
            TimeSeriesException: If this time series is a regular time series and the merged times are not all on the interval

        Returns:
            TimeSeries: The merged time series
        """
        # ---------------- #
        # set up variables #
        # ---------------- #
        others = other if isinstance(other, list) else [other]
        # ------------------------------ #
        # get the DataFrame to work with #
        # ------------------------------ #
        target = self if in_place else self.copy()
        data = cast(
            pd.DataFrame, target._data
        )  # doesn't affect selection, can't overwrite protected rows
        # ----------------- #
        # perform the merge #
        # ----------------- #
        for ts in others:
            if data is None:
                if ts._data is None:
                    continue
                data = ts._data.copy()
            elif ts._data is None:
                continue
            else:
                data2 = ts._data
                # Align data2 with data by reindexing
                aligned_data2 = data2.reindex(data.index.union(data2.index))
                # Convert 'quality' column in aligned_data2 to integers
                aligned_data2["quality"] = (
                    pd.to_numeric(aligned_data2["quality"], errors="coerce")
                    .fillna(5)  # set to missing quality
                    .astype(int)
                )
                # Create overwrite_mask
                overwrite_mask = (
                    (data["value"].isna() | np.isinf(data["value"]))  # NaN or infinite
                    & ~((data["quality"] & (1 << 31)) != 0)  # Bit 31 not set in data
                ) | (
                    ((aligned_data2["quality"] & (1 << 31)) != 0)  # Bit 31 set in data2
                )
                # Update rows in data where overwrite_mask is True
                updated_data = data.copy()
                updated_data.loc[overwrite_mask] = aligned_data2.loc[overwrite_mask]
                # Add rows from data2 not in data
                data = pd.concat(
                    [updated_data, aligned_data2[~aligned_data2.index.isin(data.index)]]
                )
            target._data = data
        target._validate()
        return target

    def imerge(self, other: Union["TimeSeries", List["TimeSeries"]]) -> "TimeSeries":
        """
        Merges one or more time series into either this time series, and returns the merged time series.

        When the same time exists while merging, the following precedence is followed:
        * other protected value (incoming protected trumps existing protected)
        * this protected value
        * this unprotected value if it is not NaN or infinite
        * other unprotected value if it is not NaN or infinte

        Identical to calling merge(..., in_place=True)

        Args:
            other (Union[&quot;TimeSeries&quot;, List[&quot;TimeSeries&quot;]]): The other times series (one or a list) to merge.
                If a list, each other time series is merged in sequence, with earlier results acting as this time series for later merges

        Raises:
            TimeSeriesException: If this time series is a regular time series and the merged times are not all on the interval

        Returns:
            TimeSeries: The merged time series
        """
        return self.merge(other, in_place=True)
