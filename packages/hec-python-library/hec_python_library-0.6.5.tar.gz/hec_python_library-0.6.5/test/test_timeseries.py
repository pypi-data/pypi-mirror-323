import copy
import math
import os
import statistics as stat
import sys
import warnings
from datetime import timedelta
from typing import cast

import numpy as np
import pandas as pd

from hec.const import Combine, Select, SelectionState
from hec.duration import Duration
from hec.hectime import HecTime
from hec.interval import Interval
from hec.parameter import Parameter
from hec.quality import Quality as Qual
from hec.timeseries import TimeSeries, TimeSeriesException, TimeSeriesValue
from hec.unit import UnitQuantity as UQ


def equal_values(v1: list[float], v2: list[float]) -> bool:
    if len(v1) != len(v2):
        return False
    for i in range(len(v1)):
        if math.isnan(v1[i]) == math.isnan(v2[i]):
            continue
        if not v1[i] == v2[i]:
            print(f"{v1[i]} != {v2[i]} at position {i}")
            for i1, i2 in zip(v1, v2):
                print(f"{i1}\t{i2}")
            return False
    return True


def test_time_series_value() -> None:
    # --------------------------------------- #
    # - create TSV without specifying quality #
    # --------------------------------------- #
    tsv = TimeSeriesValue("14Oct2024 10:55", UQ(230, "cfs"))
    assert (
        repr(tsv)
        == "TimeSeriesValue(HecTime([2024, 10, 14, 10, 55, 0], MINUTE_GRANULARITY), UnitQuantity(230, 'cfs'), Quality(0))"
    )
    assert str(tsv) == "(2024-10-14T10:55:00, 230 cfs, ~)"
    assert tsv.time == HecTime("2024-10-14T10:55:00")
    assert tsv.value == UQ(230, "cfs")
    # --------------------------------- #
    # create TSV with quality specified #
    # --------------------------------- #
    assert (
        tsv.quality.text
        == "Unscreened Unknown No_Range Original None None None Unprotected"
    )
    tsv = TimeSeriesValue("14Oct2024 10:55", UQ(12.3, "ft"), Qual("okay"))
    assert (
        repr(tsv)
        == "TimeSeriesValue(HecTime([2024, 10, 14, 10, 55, 0], MINUTE_GRANULARITY), UnitQuantity(12.3, 'ft'), Quality(3))"
    )
    assert str(tsv) == "(2024-10-14T10:55:00, 12.3 ft, o)"
    assert tsv.time == HecTime("2024-10-14T10:55:00")
    assert tsv.value == UQ(12.3, "ft")
    assert (
        tsv.quality.text == "Screened Okay No_Range Original None None None Unprotected"
    )
    # -------------------------------------- #
    # modify TSV (modify value without unit) #
    # -------------------------------------- #
    tsv.time += timedelta(minutes=65)
    tsv.value += 0.7
    tsv.quality = Qual("missing").setProtection(1)
    assert (
        repr(tsv)
        == "TimeSeriesValue(HecTime([2024, 10, 14, 12, 0, 0], MINUTE_GRANULARITY), UnitQuantity(13.0, 'ft'), Quality(-2147483643))"
    )
    assert str(tsv) == "(2024-10-14T12:00:00, 13.0 ft, M)"
    assert tsv.time == HecTime("2024-10-14T12:00:00")
    assert tsv.value == UQ(13, "ft")
    assert (
        tsv.quality.text
        == "Screened Missing No_Range Original None None None Protected"
    )
    # ----------------------------------- #
    # modify TSV (modify value with unit) #
    # ----------------------------------- #
    tsv.value = UQ(3.96, "m")
    assert (
        repr(tsv)
        == "TimeSeriesValue(HecTime([2024, 10, 14, 12, 0, 0], MINUTE_GRANULARITY), UnitQuantity(3.96, 'm'), Quality(-2147483643))"
    )
    assert str(tsv) == "(2024-10-14T12:00:00, 3.96 m, M)"
    assert tsv.time == HecTime("2024-10-14T12:00:00")
    assert tsv.value == UQ(3.96, "m")
    assert (
        tsv.quality.text
        == "Screened Missing No_Range Original None None None Protected"
    )


def test_create_time_series_by_name() -> None:
    ts = TimeSeries("SWT/Keystone.Elev-Pool.Inst.1Hour.0.Raw-Goes")
    assert ts.name == "SWT/Keystone.Elev-Pool.Inst.1Hour.0.Raw-Goes"
    assert ts.location.office == "SWT"
    assert ts.location.name == "Keystone"
    assert ts.parameter.name == "Elev-Pool"
    assert ts.unit == "ft"
    assert ts.interval.name == "1Hour"
    assert cast(Duration, ts.duration).name == "0"
    assert ts.version == "Raw-Goes"
    assert ts.vertical_datum_info is None
    ts = TimeSeries("//KEYS/ELEV-POOL//1HOUR/OBS/")
    assert ts.name == "//KEYS/ELEV-POOL//1Hour/OBS/"
    assert ts.location.office is None
    assert ts.location.name == "KEYS"
    assert ts.parameter.name == "ELEV-POOL"
    assert ts.unit == "ft"
    assert ts.interval.name == "1Hour"
    assert ts.duration == None
    assert ts.version == "OBS"
    assert ts.vertical_datum_info is None


def test_math_ops_scalar() -> None:
    assert Parameter("Flow").to("EN").unit_name == "cfs"
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    value_count = 24
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(value_count)], name="time"
    )
    area = TimeSeries(f"Loc1.Area-Xsec.Inst.{intvl.name}.0.Raw-Goes")
    assert area.unit == "ft2"
    area._data = pd.DataFrame(
        {"value": value_count * [10.0], "quality": value_count * [0]}, index=times
    )
    # ---------------- #
    # unitless scalars #
    # ---------------- #
    area2 = area + 3
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 + 3])
    area2 = area - 3
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 - 3])
    area2 = area * 3
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 * 3])
    area2 = area / 3
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 / 3])
    area2 = area // 3
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 // 3])
    area2 = area % 3
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 % 3])
    area2 = area**3
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0**3])

    area2 = area.copy()
    area2 += 3
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 + 3])
    area2 = area.copy()
    area2 -= 3
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 - 3])
    area2 = area.copy()
    area2 *= 3
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 * 3])
    area2 = area.copy()
    area2 /= 3
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 / 3])
    area2 = area.copy()
    area2 //= 3
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 // 3])
    area2 = area.copy()
    area2 %= 3
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 % 3])
    area2 = area.copy()
    area2 **= 3
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0**3])
    # -------------------------------- #
    # scalars with dimensionless units #
    # -------------------------------- #
    scalar = UQ(3, "n/a")
    area2 = area + scalar
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 + 3])
    area2 = area - scalar
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 - 3])
    area2 = area * scalar
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 * 3])
    area2 = area / scalar
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 / 3])
    area2 = area // scalar
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 // 3])
    area2 = area % scalar
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 % 3])
    area2 = area**scalar
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0**3])

    area2 = area.copy()
    area2 += scalar
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 + 3])
    area2 = area.copy()
    area2 -= scalar
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 - 3])
    area2 = area.copy()
    area2 *= scalar
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 * 3])
    area2 = area.copy()
    area2 /= scalar
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 / 3])
    area2 = area.copy()
    area2 //= scalar
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 // 3])
    area2 = area.copy()
    area2 %= scalar
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0 % 3])
    area2 = area.copy()
    area2 **= scalar
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10.0**3])
    # ------------------------------------ #
    # scalars with non-dimensionless units #
    # ------------------------------------ #
    speed = UQ(4, "mph")
    flow = (area * speed).to("Flow")
    assert flow.name == area.name.replace(area.parameter.name, "Flow")
    assert flow.unit == "cfs"
    assert np.allclose(flow.values, value_count * [58.66666666666667])
    speed2 = (flow / UQ(10, "ft2")).to("Speed-Water")
    assert speed2.name == flow.name.replace("Flow", "Speed-Water")
    assert np.allclose(speed2.values, value_count * [4.0])
    area2 = (flow / speed.to("ft/s")).to("Area-Xsec")
    assert area2.name == flow.name.replace("Flow", "Area-Xsec")
    assert np.allclose(area2.values, value_count * [10.0])


def test_math_ops_ts() -> None:
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    value_count = 24
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(value_count)], name="time"
    )
    area = TimeSeries(f"Loc1.Area-Xsec.Inst.{intvl.name}.0.Raw-Goes")
    assert area.unit == "ft2"
    area._data = pd.DataFrame(
        {"value": value_count * [10.0], "quality": value_count * [0]}, index=times
    )
    other_ts = TimeSeries(f"Loc1.Code-Modifier.Inst.{intvl.name}.0.Test")
    assert other_ts.unit == "n/a"
    other_ts._data = pd.DataFrame(
        {"value": value_count * [3.0], "quality": value_count * [0]}, index=times
    )
    # ------------------------------------ #
    # time series with dimensionless units #
    # ------------------------------------ #
    area2 = area + other_ts
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10 + 3])
    area2 = area - other_ts
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10 - 3])
    area2 = area * other_ts
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10 * 3])
    area2 = area / other_ts
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10 / 3])
    area2 = area // other_ts
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10 // 3])
    area2 = area % other_ts
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10 % 3])
    area2 = area**other_ts
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10**3])

    area2 = area.copy()
    area2 += other_ts
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10 + 3])
    area2 = area.copy()
    area2 -= other_ts
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10 - 3])
    area2 = area.copy()
    area2 *= other_ts
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10 * 3])
    area2 = area.copy()
    area2 /= other_ts
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10 / 3])
    area2 = area.copy()
    area2 //= other_ts
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10 // 3])
    area2 = area.copy()
    area2 %= other_ts
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10 % 3])
    area2 = area.copy()
    area2 **= other_ts
    assert area2.name == area.name
    assert np.allclose(area2.values, value_count * [10**3])
    # ---------------------------------------- #
    # time series with non-dimensionless units #
    # ---------------------------------------- #
    speed = TimeSeries(f"Loc1.Speed-Water.Inst.{intvl.name}.0.Raw-Goes")
    speed._data = pd.DataFrame(
        {"value": [3.0 + i for i in range(value_count)], "quality": value_count * [0]},
        index=times,
    )
    flow = (area * speed).to("Flow")
    assert flow.name == area.name.replace(area.parameter.name, "Flow")
    assert flow.unit == "cfs"
    assert flow.values == np.multiply(area.values, speed.to("ft/s").values).tolist()
    speed2 = (flow / area).to("Speed-Water")
    assert speed2.name == speed.name
    assert np.allclose(speed2.values, speed.values)
    try:
        area2 = (flow / speed).to("Area-Xsec")
        had_exception = False
    except TimeSeriesException as e:
        had_exception = True
        assert str(e).find("Cannot automtically determine conversion") != -1
    assert had_exception
    area2 = (flow / speed.to("ft/s")).to("Area-Xsec")
    assert area2.name == area.name
    assert np.allclose(area.values, area2.values)


def test_selections() -> None:
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getDss("1Hour")
    value_count = 24
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(value_count)], name="time"
    )
    flow = TimeSeries(f"//Loc1/Flow//{intvl.name}/Computed/")
    flow._data = pd.DataFrame(
        {"value": 6 * [100, 125, 112, -100], "quality": value_count * [0]},
        index=times,
    )
    flow2 = flow.select(lambda tsv: tsv.value < 0)
    assert flow2.has_selection
    assert flow2.selected == 6 * [False, False, False, True]
    flow2.isetValueQuality(
        math.nan, Qual(0).setScreened("SCREENED").setValidity("MISSING")
    )
    print(flow2.data)
    assert not flow2.has_selection
    assert np.nan_to_num(flow2.values, nan=-1).tolist() == 6 * [100.0, 125.0, 112.0, -1]
    assert flow2.qualities == 6 * [0, 0, 0, 5]
    flow2.selection_state = SelectionState.DURABLE
    flow2.iselect(lambda tsv: tsv.value > 120)
    assert flow2.has_selection
    assert flow2.selected == 6 * [False, True, False, False]
    flow2 -= 5
    assert flow2.has_selection
    assert flow2.selected == 6 * [False, True, False, False]
    assert np.nan_to_num(flow2.values, nan=-1).tolist() == 6 * [100.0, 120.0, 112.0, -1]
    flow2.iselect(Select.INVERT)
    assert flow2.selected == 6 * [True, False, True, True]
    flow2.iselect(Select.ALL)
    assert not flow2.has_selection
    assert flow2.selection_state == SelectionState.DURABLE
    flow2.selection_state = SelectionState.TRANSIENT
    assert flow2.selection_state == SelectionState.TRANSIENT


def test_aggregate_ts() -> None:
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    value_count = 24
    ts_count = 10
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(value_count)], name="time"
    )
    timeseries = []
    for i in range(ts_count - 2):
        ts = TimeSeries(f"Loc{i+1}.Flow.Inst.{intvl.name}.0.Computed")
        ts._data = pd.DataFrame(
            {
                "value": [(1000 + i * 10) + j * 15 for j in range(value_count)],
                "quality": value_count * [0],
            },
            index=times,
        )
        timeseries.append(ts)
        if i in (3, 7):
            timeseries.append(ts)
    cast(pd.DataFrame, timeseries[0]._data).loc[
        "2024-10-10 01:00:00", "value"
    ] = math.nan
    test_rows = [
        [timeseries[i].values[j] for i in range(ts_count)] for j in range(value_count)
    ]
    # ----------- #
    # builtin all #
    # ----------- #
    ts = TimeSeries.aggregate_ts(all, timeseries)
    for i in range(value_count):
        assert ts.values[i] == all(test_rows[i])
    # ----------- #
    # builtin any #
    # ----------- #
    ts = TimeSeries.aggregate_ts(any, timeseries)
    for i in range(value_count):
        assert ts.values[i] == any(test_rows[i])
    # ----------- #
    # builtin len #
    # ----------- #
    ts = TimeSeries.aggregate_ts(len, timeseries)
    for i in range(value_count):
        assert ts.values[i] == len(test_rows[i])
    # ----------- #
    # builtin max # generates warning
    # ----------- #
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        ts = TimeSeries.aggregate_ts(max, timeseries)
        for i in range(value_count):
            assert ts.values[i] == max([v for v in test_rows[i] if not math.isnan(v)])
    # ----------- #
    # builtin min # generates warning
    # ----------- #
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        ts = TimeSeries.aggregate_ts(min, timeseries)
        for i in range(value_count):
            assert ts.values[i] == min([v for v in test_rows[i] if not math.isnan(v)])
    # ----------- #
    # builtin sum # generates warning
    # ----------- #
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        ts = TimeSeries.aggregate_ts(sum, timeseries)
        for i in range(value_count):
            assert ts.values[i] == sum([v for v in test_rows[i] if not math.isnan(v)])
    # --------- #
    # math.prod #
    # --------- #
    ts = TimeSeries.aggregate_ts(math.prod, timeseries)
    for i in range(value_count):
        assert ts.values[i] == math.prod(test_rows[i]) or (
            math.isnan(ts.values[i]) and math.isnan(math.prod(test_rows[i]))
        )
    # ---------------- #
    # statistics.fmean #
    # ---------------- #
    ts = TimeSeries.aggregate_ts(stat.fmean, timeseries)
    for i in range(value_count):
        assert ts.values[i] == stat.fmean(test_rows[i]) or (
            math.isnan(ts.values[i]) and math.isnan(stat.fmean(test_rows[i]))
        )
    # ------------------------- #
    # statistics.geometric_mean #
    # ------------------------- #
    ts = TimeSeries.aggregate_ts(stat.geometric_mean, timeseries)
    for i in range(value_count):
        assert ts.values[i] == stat.geometric_mean(test_rows[i]) or (
            math.isnan(ts.values[i]) and math.isnan(stat.geometric_mean(test_rows[i]))
        )
    # ------------------------ #
    # statistics.harmonic_mean #
    # ------------------------ #
    ts = TimeSeries.aggregate_ts(stat.harmonic_mean, timeseries)
    for i in range(value_count):
        assert ts.values[i] == stat.harmonic_mean(test_rows[i]) or (
            math.isnan(ts.values[i]) and math.isnan(stat.harmonic_mean(test_rows[i]))
        )
    # --------------- #
    # statistics.mean #
    # --------------- #
    ts = TimeSeries.aggregate_ts(stat.mean, timeseries)
    for i in range(value_count):
        assert ts.values[i] == stat.mean(test_rows[i]) or (
            math.isnan(ts.values[i]) and math.isnan(stat.mean(test_rows[i]))
        )
    # ----------------- #
    # statistics.median #
    # ----------------- #
    ts = TimeSeries.aggregate_ts(stat.median, timeseries)
    for i in range(value_count):
        assert ts.values[i] == stat.median(test_rows[i]) or (
            math.isnan(ts.values[i]) and math.isnan(stat.median(test_rows[i]))
        )
    # ------------------------- #
    # statistics.median_grouped #
    # ------------------------- #
    ts = TimeSeries.aggregate_ts(stat.median_grouped, timeseries)
    for i in range(value_count):
        assert ts.values[i] == stat.median_grouped(test_rows[i]) or (
            math.isnan(ts.values[i]) and math.isnan(stat.median_grouped(test_rows[i]))
        )
    # ---------------------- #
    # statistics.median_high #
    # ---------------------- #
    ts = TimeSeries.aggregate_ts(stat.median_high, timeseries)
    for i in range(value_count):
        assert ts.values[i] == stat.median_high(test_rows[i]) or (
            math.isnan(ts.values[i]) and math.isnan(stat.median_high(test_rows[i]))
        )
    # --------------------- #
    # statistics.median_low #
    # --------------------- #
    ts = TimeSeries.aggregate_ts(stat.median_low, timeseries)
    for i in range(value_count):
        assert ts.values[i] == stat.median_low(test_rows[i]) or (
            math.isnan(ts.values[i]) and math.isnan(stat.median_low(test_rows[i]))
        )
    # --------------- #
    # statistics.mode #
    # --------------- #
    ts = TimeSeries.aggregate_ts(stat.mode, timeseries)
    for i in range(value_count):
        assert ts.values[i] == stat.mode(test_rows[i]) or (
            math.isnan(ts.values[i]) and math.isnan(stat.mode(test_rows[i]))
        )
    # -------------------- #
    # statistics.multimode # generates non-standard TimeSeries
    # -------------------- #
    ts = TimeSeries.aggregate_ts(stat.multimode, timeseries)
    for i in range(value_count):
        assert cast(list[float], ts.values[i]) == stat.multimode(test_rows[i])
    # ----------------- #
    # statistics.pstdev #
    # ----------------- #
    ts = TimeSeries.aggregate_ts(stat.pstdev, timeseries)
    for i in range(value_count):
        assert ts.values[i] == stat.pstdev(test_rows[i]) or (
            math.isnan(ts.values[i]) and math.isnan(stat.pstdev(test_rows[i]))
        )
    # -------------------- #
    # statistics.pvariance #
    # -------------------- #
    ts = TimeSeries.aggregate_ts(stat.pvariance, timeseries)
    for i in range(value_count):
        assert ts.values[i] == stat.pvariance(test_rows[i]) or (
            math.isnan(ts.values[i]) and math.isnan(stat.pvariance(test_rows[i]))
        )
    # -------------------- #
    # statistics.quantiles # generates non-standard TimeSeries
    # -------------------- #
    ts = TimeSeries.aggregate_ts(stat.quantiles, timeseries)
    for i in range(value_count):
        assert cast(list[float], ts.values[i]) == stat.quantiles(test_rows[i])
    # ---------------- #
    # statistics.stdev #
    # ---------------- #
    ts = TimeSeries.aggregate_ts(stat.stdev, timeseries)
    for i in range(value_count):
        assert ts.values[i] == stat.stdev(test_rows[i]) or (
            math.isnan(ts.values[i]) and math.isnan(stat.stdev(test_rows[i]))
        )
    # ------------------- #
    # statistics.variance #
    # ------------------- #
    ts = TimeSeries.aggregate_ts(stat.variance, timeseries)
    for i in range(value_count):
        assert ts.values[i] == stat.variance(test_rows[i]) or (
            math.isnan(ts.values[i]) and math.isnan(stat.variance(test_rows[i]))
        )
    # ----- #
    # "all" #
    # ----- #
    ts = TimeSeries.aggregate_ts("all", timeseries)
    for i in range(value_count):
        assert ts.values[i] == all(test_rows[i]) or (
            math.isnan(ts.values[i]) and math.isnan(all(test_rows[i]))
        )
    # ----- #
    # "any" #
    # ----- #
    ts = TimeSeries.aggregate_ts("any", timeseries)
    for i in range(value_count):
        assert ts.values[i] == any(test_rows[i]) or (
            math.isnan(ts.values[i]) and math.isnan(any(test_rows[i]))
        )
    # ------- #
    # "count" #
    # ------- #
    ts = TimeSeries.aggregate_ts("count", timeseries)
    for i in range(value_count):
        assert ts.values[i] == len(test_rows[i]) - len(
            [v for v in test_rows[i] if math.isnan(v)]
        )
    # ---------- #
    # "describe" #
    # ---------- #
    ts = TimeSeries.aggregate_ts("describe", timeseries)
    df = cast(pd.DataFrame, ts.data)["value"]
    p25s = []
    p50s = []
    p75s = []
    for i in range(value_count):
        p25, p50, p75 = stat.quantiles(
            [v for v in test_rows[i] if not math.isnan(v)], n=4, method="inclusive"
        )
        p25s.append(p25)
        p50s.append(p50)
        p75s.append(p75)
        assert df.loc[times[i], "count"] == len(test_rows[i]) - len(
            [v for v in test_rows[i] if math.isnan(v)]
        )
        assert df.loc[times[i], "mean"] == stat.mean(
            [v for v in test_rows[i] if not math.isnan(v)]
        )
        assert df.loc[times[i], "std"] == stat.stdev(
            [v for v in test_rows[i] if not math.isnan(v)]
        )
        assert df.loc[times[i], "25%"] == p25
        assert df.loc[times[i], "50%"] == p50
        assert df.loc[times[i], "75%"] == p75
        assert df.loc[times[i], "min"] == min(
            [v for v in test_rows[i] if not math.isnan(v)]
        )
        assert df.loc[times[i], "max"] == max(
            [v for v in test_rows[i] if not math.isnan(v)]
        )
    # ---- #
    # fmod #
    # ---- #
    ts = TimeSeries.aggregate_ts(
        lambda i: math.fmod(i[0], i[1]), [timeseries[ts_count - 1], timeseries[0]]
    )
    for i in range(value_count):
        expected = math.fmod(
            timeseries[ts_count - 1].values[i], timeseries[0].values[i]
        )
        assert (
            math.isnan(ts.values[i])
            and math.isnan(expected)
            or ts.values[i] == expected
        )
    # --- #
    # rms #
    # --- #
    ts = TimeSeries.aggregate_ts(
        lambda s: np.sqrt(np.mean(np.array(s) ** 2)), timeseries
    )
    for i in range(value_count):
        expected = math.sqrt(stat.mean([v**2 for v in test_rows[i]]))
        assert (
            math.isnan(ts.values[i])
            and math.isnan(expected)
            or ts.values[i] == expected
        )
    # ----------- #
    # percentiles #
    # ----------- #
    pct = {}
    for ts in timeseries:
        ts.selection_state = SelectionState.DURABLE
        ts.iselect(lambda tsv: not math.isnan(tsv.value))
    for p in (1, 2, 5, 10, 20, 25, 50, 75, 80, 90, 95, 98, 99):
        pct[p] = TimeSeries.percentile_ts(p, timeseries)
    ts.selection_state = SelectionState.TRANSIENT
    ts.iselect(Select.ALL)
    pvals = sorted(pct)
    for i in range(1, len(pvals)):
        for j in range(value_count):
            assert pct[pvals[i]].values[j] >= pct[pvals[i - 1]].values[j]
    assert pct[25].values == p25s
    assert pct[50].values == p50s
    assert pct[75].values == p75s
    for ts in timeseries:
        ts.selection_state = SelectionState.TRANSIENT
        ts.iselect(Select.ALL)


def test_aggregate_values() -> None:
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    values = [
        1000,
        1015,
        1030,
        1045,
        1060,
        1075,
        1090,
        1090,
        1120,
        1135,
        math.nan,
        1165,
        1180,
        1195,
        1210,
        1225,
        1240,
        1240,
        1270,
        1285,
        1300,
        1315,
        1330,
        1345,
    ]
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(len(values))], name="time"
    )
    ts = TimeSeries(f"Loc1.Flow.Inst.{intvl.name}.0.Computed")
    ts._data = pd.DataFrame(
        {
            "value": values,
            "quality": len(values) * [0],
        },
        index=times,
    )
    # ----------- #
    # builtin all #
    # ----------- #
    assert ts.aggregate(all) == all(values)
    # ----------- #
    # builtin any #
    # ----------- #
    assert ts.aggregate(any) == any(values)
    # ----------- #
    # builtin len #
    # ----------- #
    assert ts.aggregate(len) == len(values)
    # ----------- #
    # builtin max # generates warning
    # ----------- #
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        assert ts.aggregate(max) == max([v for v in values if not math.isnan(v)])
    # ----------- #
    # builtin min # generates warning
    # ----------- #
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        assert ts.aggregate(min) == min([v for v in values if not math.isnan(v)])
    # ----------- #
    # builtin sum # generates warning
    # ----------- #
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        assert ts.aggregate(sum) == sum([v for v in values if not math.isnan(v)])
    # --------- #
    # math.prod #
    # --------- #
    assert math.isnan(ts.aggregate(math.prod))
    ts2 = ts / 1000.0
    ts2.iselect(lambda tsv: not math.isnan(tsv.value))
    assert ts2.aggregate(math.prod) == math.prod(
        [v / 1000.0 for v in values if not math.isnan(v)]
    )
    # ---------------- #
    # statistics.fmean #
    # ---------------- #
    assert ts.aggregate(stat.fmean) == stat.fmean(values) or (
        math.isnan(ts.aggregate(stat.fmean)) and math.isnan(stat.fmean(values))
    )
    # ------------------------- #
    # statistics.geometric_mean #
    # ------------------------- #
    assert ts.aggregate(stat.geometric_mean) == stat.geometric_mean(values) or (
        math.isnan(ts.aggregate(stat.geometric_mean))
        and math.isnan(stat.geometric_mean(values))
    )
    # ------------------------ #
    # statistics.harmonic_mean #
    # ------------------------ #
    assert ts.aggregate(stat.harmonic_mean) == stat.harmonic_mean(values) or (
        math.isnan(ts.aggregate(stat.harmonic_mean))
        and math.isnan(stat.harmonic_mean(values))
    )
    # --------------- #
    # statistics.mean #
    # --------------- #
    assert ts.aggregate(stat.mean) == stat.mean(values) or (
        math.isnan(ts.aggregate(stat.mean)) and math.isnan(stat.mean(values))
    )
    # ----------------- #
    # statistics.median #
    # ----------------- #
    assert ts.aggregate(stat.median) == stat.median(values) or (
        math.isnan(ts.aggregate(stat.median)) and math.isnan(stat.median(values))
    )
    # ------------------------- #
    # statistics.median_grouped #
    # ------------------------- #
    assert ts.aggregate(stat.median_grouped) == stat.median_grouped(values) or (
        math.isnan(ts.aggregate(stat.median_grouped))
        and math.isnan(stat.median_grouped(values))
    )
    # ---------------------- #
    # statistics.median_high #
    # ---------------------- #
    assert ts.aggregate(stat.median_high) == stat.median_high(values) or (
        math.isnan(ts.aggregate(stat.median_high))
        and math.isnan(stat.median_high(values))
    )
    # --------------------- #
    # statistics.median_low #
    # --------------------- #
    assert ts.aggregate(stat.median_low) == stat.median_low(values) or (
        math.isnan(ts.aggregate(stat.median_low))
        and math.isnan(stat.median_low(values))
    )
    # --------------- #
    # statistics.mode #
    # --------------- #
    assert ts.aggregate(stat.mode) == stat.mode(values) or (
        math.isnan(ts.aggregate(stat.mode)) and math.isnan(stat.mode(values))
    )
    # -------------------- #
    # statistics.multimode #
    # -------------------- #
    assert ts.aggregate(stat.multimode) == stat.multimode(values)
    # ----------------- #
    # statistics.pstdev #
    # ----------------- #
    assert ts.aggregate(stat.pstdev) == stat.pstdev(values) or (
        math.isnan(ts.aggregate(stat.pstdev)) and math.isnan(stat.pstdev(values))
    )
    # -------------------- #
    # statistics.pvariance #
    # -------------------- #
    assert ts.aggregate(stat.pvariance) == stat.pvariance(values) or (
        math.isnan(ts.aggregate(stat.pvariance)) and math.isnan(stat.pvariance(values))
    )
    # -------------------- #
    # statistics.quantiles #
    # -------------------- #
    assert ts.aggregate(stat.quantiles) == stat.quantiles(values)
    # ---------------- #
    # statistics.stdev #
    # ---------------- #
    assert ts.aggregate(stat.stdev) == stat.stdev(values) or (
        math.isnan(ts.aggregate(stat.stdev)) and math.isnan(stat.stdev(values))
    )
    # ------------------- #
    # statistics.variance #
    # ------------------- #
    assert ts.aggregate(stat.variance) == stat.variance(values) or (
        math.isnan(ts.aggregate(stat.variance)) and math.isnan(stat.variance(values))
    )
    # ----- #
    # "all" #
    # ----- #
    assert ts.aggregate("all") == all([v for v in values if not math.isnan(v)])
    # ----- #
    # "any" #
    # ----- #
    assert ts.aggregate("any") == any([v for v in values if not math.isnan(v)])
    # ------- #
    # "count" #
    # ------- #
    assert ts.aggregate("count") == len([v for v in values if not math.isnan(v)])
    # ---------- #
    # "describe" #
    # ---------- #
    df = ts.aggregate("describe")
    p25, p50, p75 = stat.quantiles(
        [v for v in values if not math.isnan(v)], n=4, method="inclusive"
    )
    assert df["count"] == len(values) - len([v for v in values if math.isnan(v)])
    assert df["mean"] == stat.mean([v for v in values if not math.isnan(v)])
    assert df["std"] == stat.stdev([v for v in values if not math.isnan(v)])
    assert df["min"] == min([v for v in values if not math.isnan(v)])
    assert df["25%"] == p25
    assert df["50%"] == p50
    assert df["75%"] == p75
    assert df["max"] == max([v for v in values if not math.isnan(v)])
    # -------- #
    # kurtosis #
    # -------- #
    assert abs(ts.kurtosis() - -1.284) < 0.05
    # ----------- #
    # percentiles #
    # ----------- #
    pct = {}
    ts.selection_state = SelectionState.DURABLE
    ts.iselect(lambda tsv: not math.isnan(tsv.value))
    for p in (1, 2, 5, 10, 20, 25, 50, 75, 80, 90, 95, 98, 99):
        pct[p] = ts.percentile(p)
    ts.selection_state = SelectionState.TRANSIENT
    ts.iselect(Select.ALL)
    pvals = sorted(pct)
    for i in range(1, len(pvals)):
        assert pct[pvals[i]] >= pct[pvals[i - 1]]
    assert pct[25] == p25
    assert pct[50] == p50
    assert pct[75] == p75


def test_min_max() -> None:
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    value_count = 24
    values = [10.0 + i for i in range(value_count)]
    values[3] = math.nan
    values[2] = values[8] = -1.0
    values[5] = values[9] = 1000.0
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(value_count)], name="time"
    )
    ts = TimeSeries(f"Loc1.Code.Inst.{intvl.name}.0.Raw-Goes")
    ts._data = pd.DataFrame(
        {"value": values, "quality": value_count * [0]}, index=times
    )
    assert ts.minValue() == -1.0
    assert ts.maxValue() == 1000.0
    assert ts.minValueTime() == start_time + 2 * intvl
    assert ts.maxValueTime() == start_time + 5 * intvl
    ts.selection_state = SelectionState.DURABLE
    ts.iselect(lambda tsv: 10 < tsv.value < 100)
    assert ts.minValue() == 11.0
    assert ts.maxValue() == 33.0
    assert ts.minValueTime() == start_time + intvl
    assert ts.maxValueTime() == start_time + 23 * intvl


def test_accum_diff() -> None:
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    # Col 1 = starting values (made up)
    # Col 2 = from TimeSeriesMath.accumualtion() using col 1
    # Col 3 = from TimeSeriesMath.successiveDiffereneces using col 2(except for first value)
    data = [
        [10.0, 10.0, math.nan],
        [11.0, 21.0, 11.0],
        [-1.0, 20.0, -1.0],
        [math.nan, 20.0, 0.0],
        [14.0, 34.0, 14.0],
        [1000.0, 1034.0, 1000.0],
        [16.0, 1050.0, 16.0],
        [17.0, 1067.0, 17.0],
        [-1.0, 1066.0, -1.0],
        [1000.0, 2066.0, 1000.0],
        [20.0, 2086.0, 20.0],
        [21.0, 2107.0, 21.0],
        [22.0, 2129.0, 22.0],
        [23.0, 2152.0, 23.0],
        [24.0, 2176.0, 24.0],
        [25.0, 2201.0, 25.0],
        [26.0, 2227.0, 26.0],
        [27.0, 2254.0, 27.0],
        [28.0, 2282.0, 28.0],
        [29.0, 2311.0, 29.0],
        [30.0, 2341.0, 30.0],
        [31.0, 2372.0, 31.0],
        [32.0, 2404.0, 32.0],
        [33.0, 2437.0, 33.0],
    ]
    value_count = len(data)
    values, accum, diffs = map(list, zip(*data))
    diffs = diffs[1:]
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(value_count)], name="time"
    )
    ts = TimeSeries(f"Loc1.Code.Inst.{intvl.name}.0.Raw-Goes")
    ts._data = pd.DataFrame(
        {"value": values, "quality": value_count * [0]}, index=times
    )
    ts_accum = ts.accum()
    assert ts_accum.values == accum
    ts_diffs = ts_accum.diff()
    assert ts_diffs.values == diffs
    ts_time_diffs = ts_accum.time_derivative()
    assert ts_time_diffs.values == list(map(lambda x: x / 60, diffs))
    accum[10] = math.nan
    diffs[9] = diffs[10] = math.nan
    ts._data = pd.DataFrame({"value": accum, "quality": value_count * [0]}, index=times)
    vals = ts.diff().values
    assert len(vals) == len(diffs)
    if len(vals) == len(diffs):
        for i in range(len(vals)):
            assert math.isnan(vals[i]) and math.isnan(diffs[i]) or vals[i] == diffs[i]


def test_value_counts() -> None:
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    values = [
        1000,
        1015,
        1030,
        1045,
        1060,
        math.inf,
        1090,
        1090,
        1120,
        1135,
        math.nan,
        1165,
        1180,
        1195,
        1210,
        1225,
        1240,
        1240,
        1270,
        math.inf,
        1300,
        1315,
        1330,
        1345,
    ]
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(len(values))], name="time"
    )
    ts = TimeSeries(f"Loc1.Flow.Inst.{intvl.name}.0.Computed")
    ts._data = pd.DataFrame(
        {
            "value": values,
            "quality": len(values) * [0],
        },
        index=times,
    )
    ts._data.loc[ts.indexOf(0), "quality"] = Qual("Rejected").code
    ts._data.loc[ts.indexOf(1), "quality"] = Qual("Missing").code
    ts._data.loc[ts.indexOf(2), "quality"] = Qual("Questionable").code
    # --------------#
    # no selection #
    # --------------#
    assert ts.number_values == len(values)
    assert ts.number_invalid_values == 5
    assert ts.number_valid_values == len(values) - 5
    assert ts.number_missing_values == 2
    assert ts.number_questioned_values == 1
    assert ts.number_rejected_values == 1
    assert ts.first_valid_value == 1030
    assert HecTime("2024-10-10T03:00:00") == ts.first_valid_time
    assert ts.last_valid_value == 1345
    assert HecTime("2024-10-10T24:00:00") == ts.last_valid_time
    # ----------------#
    # with selection #
    # ----------------#
    ts2 = ts.select(
        lambda tsv: HecTime("2024-10-10T11:00:00")
        <= tsv.time
        <= HecTime("2024-10-10T20:00:00"),
    )
    ts2.selection_state = SelectionState.DURABLE
    assert ts2.number_values == 10
    assert ts2.number_invalid_values == 2
    assert ts2.number_valid_values == 8
    assert ts2.number_missing_values == 1
    assert ts2.number_questioned_values == 0
    assert ts2.number_rejected_values == 0
    assert ts2.first_valid_value == 1165
    assert HecTime("2024-10-10T12:00:00") == ts2.first_valid_time
    assert ts2.last_valid_value == 1270
    assert HecTime("2024-10-10T19:00:00") == ts2.last_valid_time


def test_unit() -> None:
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    values = [
        1000,
        1015,
        1030,
        1045,
        1060,
        math.inf,
        1090,
        1090,
        1120,
        1135,
        math.nan,
        1165,
        1180,
        1195,
        1210,
        1225,
        1240,
        1240,
        1270,
        math.inf,
        1300,
        1315,
        1330,
        1345,
    ]
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(len(values))], name="time"
    )
    ts = TimeSeries(f"Loc1.Flow.Inst.{intvl.name}.0.Computed")
    ts._data = pd.DataFrame(
        {
            "value": values,
            "quality": len(values) * [0],
        },
        index=times,
    )
    assert ts.is_english
    assert not ts.is_metric
    assert ts.can_determine_unit_system
    assert ts.parameter.unit_name == "cfs"
    assert ts.parameter.to("EN").unit_name == "cfs"
    assert ts.parameter.to("SI").unit_name == "cms"


def test_roundoff() -> None:
    data = [
        #       value  prec,  mgntude,       result
        [12345.678912, 1, -5, 10000.0],
        [12345.678912, 1, -4, 10000.0],
        [12345.678912, 1, -3, 10000.0],
        [12345.678912, 1, -2, 10000.0],
        [12345.678912, 1, -1, 10000.0],
        [12345.678912, 1, 0, 10000.0],
        [12345.678912, 1, 1, 10000.0],
        [12345.678912, 1, 2, 10000.0],
        [12345.678912, 1, 3, 10000.0],
        [12345.678912, 1, 4, 10000.0],
        [12345.678912, 1, 5, 0.0],
        [12345.678912, 2, -5, 12000.0],
        [12345.678912, 2, -4, 12000.0],
        [12345.678912, 2, -3, 12000.0],
        [12345.678912, 2, -2, 12000.0],
        [12345.678912, 2, -1, 12000.0],
        [12345.678912, 2, 0, 12000.0],
        [12345.678912, 2, 1, 12000.0],
        [12345.678912, 2, 2, 12000.0],
        [12345.678912, 2, 3, 12000.0],
        [12345.678912, 2, 4, 10000.0],
        [12345.678912, 2, 5, 0.0],
        [12345.678912, 3, -5, 12300.0],
        [12345.678912, 3, -4, 12300.0],
        [12345.678912, 3, -3, 12300.0],
        [12345.678912, 3, -2, 12300.0],
        [12345.678912, 3, -1, 12300.0],
        [12345.678912, 3, 0, 12300.0],
        [12345.678912, 3, 1, 12300.0],
        [12345.678912, 3, 2, 12300.0],
        [12345.678912, 3, 3, 12000.0],
        [12345.678912, 3, 4, 10000.0],
        [12345.678912, 3, 5, 0.0],
        [12345.678912, 4, -5, 12350.0],
        [12345.678912, 4, -4, 12350.0],
        [12345.678912, 4, -3, 12350.0],
        [12345.678912, 4, -2, 12350.0],
        [12345.678912, 4, -1, 12350.0],
        [12345.678912, 4, 0, 12350.0],
        [12345.678912, 4, 1, 12350.0],
        [12345.678912, 4, 2, 12300.0],
        [12345.678912, 4, 3, 12000.0],
        [12345.678912, 4, 4, 10000.0],
        [12345.678912, 4, 5, 0.0],
        [12345.678912, 5, -5, 12346.0],
        [12345.678912, 5, -4, 12346.0],
        [12345.678912, 5, -3, 12346.0],
        [12345.678912, 5, -2, 12346.0],
        [12345.678912, 5, -1, 12346.0],
        [12345.678912, 5, 0, 12346.0],
        [12345.678912, 5, 1, 12350.0],
        [12345.678912, 5, 2, 12300.0],
        [12345.678912, 5, 3, 12000.0],
        [12345.678912, 5, 4, 10000.0],
        [12345.678912, 5, 5, 0.0],
        [12345.678912, 6, -5, 12345.7],
        [12345.678912, 6, -4, 12345.7],
        [12345.678912, 6, -3, 12345.7],
        [12345.678912, 6, -2, 12345.7],
        [12345.678912, 6, -1, 12345.7],
        [12345.678912, 6, 0, 12346.0],
        [12345.678912, 6, 1, 12350.0],
        [12345.678912, 6, 2, 12300.0],
        [12345.678912, 6, 3, 12000.0],
        [12345.678912, 6, 4, 10000.0],
        [12345.678912, 6, 5, 0.0],
        [12345.678912, 7, -5, 12345.68],
        [12345.678912, 7, -4, 12345.68],
        [12345.678912, 7, -3, 12345.68],
        [12345.678912, 7, -2, 12345.68],
        [12345.678912, 7, -1, 12345.7],
        [12345.678912, 7, 0, 12346.0],
        [12345.678912, 7, 1, 12350.0],
        [12345.678912, 7, 2, 12300.0],
        [12345.678912, 7, 3, 12000.0],
        [12345.678912, 7, 4, 10000.0],
        [12345.678912, 7, 5, 0.0],
        [12345.678912, 8, -5, 12345.679],
        [12345.678912, 8, -4, 12345.679],
        [12345.678912, 8, -3, 12345.679],
        [12345.678912, 8, -2, 12345.68],
        [12345.678912, 8, -1, 12345.7],
        [12345.678912, 8, 0, 12346.0],
        [12345.678912, 8, 1, 12350.0],
        [12345.678912, 8, 2, 12300.0],
        [12345.678912, 8, 3, 12000.0],
        [12345.678912, 8, 4, 10000.0],
        [12345.678912, 8, 5, 0.0],
        [12345.678912, 9, -5, 12345.6789],
        [12345.678912, 9, -4, 12345.6789],
        [12345.678912, 9, -3, 12345.679],
        [12345.678912, 9, -2, 12345.68],
        [12345.678912, 9, -1, 12345.7],
        [12345.678912, 9, 0, 12346.0],
        [12345.678912, 9, 1, 12350.0],
        [12345.678912, 9, 2, 12300.0],
        [12345.678912, 9, 3, 12000.0],
        [12345.678912, 9, 4, 10000.0],
        [12345.678912, 9, 5, 0.0],
        [12345.678912, 10, -5, 12345.67891],
        [12345.678912, 10, -4, 12345.6789],
        [12345.678912, 10, -3, 12345.679],
        [12345.678912, 10, -2, 12345.68],
        [12345.678912, 10, -1, 12345.7],
        [12345.678912, 10, 0, 12346.0],
        [12345.678912, 10, 1, 12350.0],
        [12345.678912, 10, 2, 12300.0],
        [12345.678912, 10, 3, 12000.0],
        [12345.678912, 10, 4, 10000.0],
        [12345.678912, 10, 5, 0.0],
        [12345.678912, 11, -5, 12345.67891],
        [12345.678912, 11, -4, 12345.6789],
        [12345.678912, 11, -3, 12345.679],
        [12345.678912, 11, -2, 12345.68],
        [12345.678912, 11, -1, 12345.7],
        [12345.678912, 11, 0, 12346.0],
        [12345.678912, 11, 1, 12350.0],
        [12345.678912, 11, 2, 12300.0],
        [12345.678912, 11, 3, 12000.0],
        [12345.678912, 11, 4, 10000.0],
        [12345.678912, 11, 5, 0.0],
        [12345.678912, 12, -5, 12345.67891],
        [12345.678912, 12, -4, 12345.6789],
        [12345.678912, 12, -3, 12345.679],
        [12345.678912, 12, -2, 12345.68],
        [12345.678912, 12, -1, 12345.7],
        [12345.678912, 12, 0, 12346.0],
        [12345.678912, 12, 1, 12350.0],
        [12345.678912, 12, 2, 12300.0],
        [12345.678912, 12, 3, 12000.0],
        [12345.678912, 12, 4, 10000.0],
        [12345.678912, 12, 5, 0.0],
    ]

    for value, precsion, magnitude, result in data:
        assert TimeSeries._roundOff(value, int(precsion), int(magnitude)) == result
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    values = [
        1000.123,
        1015.123,
        1030.123,
        1045.123,
        1060.123,
        1075.123,
        1090.123,
        1090.123,
        1120.123,
        1135.123,
        1150.123,
        1165.123,
        1180.123,
        1195.123,
        1210.123,
        1225.123,
        1240.123,
        1240.123,
        1270.123,
        1285.123,
        1300.123,
        1315.123,
        1330.123,
        1345.123,
    ]
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(len(values))], name="time"
    )
    ts = TimeSeries(f"Loc1.Flow.Inst.{intvl.name}.0.Computed")
    ts._data = pd.DataFrame(
        {
            "value": values,
            "quality": len(values) * [0],
        },
        index=times,
    )
    assert ts.roundOff(4, 0).values == list(
        map(lambda v: TimeSeries._roundOff(v, 4, 0), values)
    )
    assert ts.roundOff(5, -1).values == list(
        map(lambda v: TimeSeries._roundOff(v, 5, -1), values)
    )


def test_smoothing() -> None:
    with open(
        os.path.join(
            os.path.dirname(__file__), "resources", "timeseries", "smoothing.txt"
        )
    ) as f:
        data = eval(f.read())
    values = [data[i][0] for i in range(len(data))]
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(len(values))], name="time"
    )
    ts = TimeSeries(f"Loc1.Flow.Inst.{intvl.name}.0.Computed")
    ts._data = pd.DataFrame(
        {
            "value": values,
            "quality": len(values) * [0],
        },
        index=times,
    )
    assert equal_values(
        ts.forwardMovingAverage(window=3, onlyValid=False, useReduced=False).values,
        [data[i][1] for i in range(len(data))],
    )
    assert equal_values(
        ts.forwardMovingAverage(window=3, onlyValid=False, useReduced=True).values,
        [data[i][4] for i in range(len(data))],
    )
    assert equal_values(
        ts.forwardMovingAverage(window=3, onlyValid=True, useReduced=False).values,
        [data[i][7] for i in range(len(data))],
    )
    assert equal_values(
        ts.forwardMovingAverage(window=3, onlyValid=True, useReduced=True).values,
        [data[i][10] for i in range(len(data))],
    )
    assert equal_values(
        ts.forwardMovingAverage(window=5, onlyValid=False, useReduced=False).values,
        [data[i][13] for i in range(len(data))],
    )
    assert equal_values(
        ts.forwardMovingAverage(window=5, onlyValid=False, useReduced=True).values,
        [data[i][16] for i in range(len(data))],
    )
    assert equal_values(
        ts.forwardMovingAverage(window=5, onlyValid=True, useReduced=False).values,
        [data[i][19] for i in range(len(data))],
    )
    assert equal_values(
        ts.forwardMovingAverage(window=5, onlyValid=True, useReduced=True).values,
        [data[i][22] for i in range(len(data))],
    )
    assert equal_values(
        ts.centeredMovingAverage(window=3, onlyValid=False, useReduced=False).values,
        [data[i][2] for i in range(len(data))],
    )
    assert equal_values(
        ts.centeredMovingAverage(window=3, onlyValid=False, useReduced=True).values,
        [data[i][5] for i in range(len(data))],
    )
    assert equal_values(
        ts.centeredMovingAverage(window=3, onlyValid=True, useReduced=False).values,
        [data[i][8] for i in range(len(data))],
    )
    assert equal_values(
        ts.centeredMovingAverage(window=3, onlyValid=True, useReduced=True).values,
        [data[i][11] for i in range(len(data))],
    )
    assert equal_values(
        ts.centeredMovingAverage(window=5, onlyValid=False, useReduced=False).values,
        [data[i][14] for i in range(len(data))],
    )
    assert equal_values(
        ts.centeredMovingAverage(window=5, onlyValid=False, useReduced=True).values,
        [data[i][17] for i in range(len(data))],
    )
    assert equal_values(
        ts.centeredMovingAverage(window=5, onlyValid=True, useReduced=False).values,
        [data[i][20] for i in range(len(data))],
    )
    assert equal_values(
        ts.centeredMovingAverage(window=5, onlyValid=True, useReduced=True).values,
        [data[i][23] for i in range(len(data))],
    )
    assert equal_values(
        ts.olympicMovingAverage(window=3, onlyValid=False, useReduced=False).values,
        [data[i][3] for i in range(len(data))],
    )
    assert equal_values(
        ts.olympicMovingAverage(window=3, onlyValid=False, useReduced=True).values,
        [data[i][6] for i in range(len(data))],
    )
    assert equal_values(
        ts.olympicMovingAverage(window=3, onlyValid=True, useReduced=False).values,
        [data[i][9] for i in range(len(data))],
    )
    assert equal_values(
        ts.olympicMovingAverage(window=3, onlyValid=True, useReduced=True).values,
        [data[i][12] for i in range(len(data))],
    )
    assert equal_values(
        ts.olympicMovingAverage(window=5, onlyValid=False, useReduced=False).values,
        [data[i][15] for i in range(len(data))],
    )
    assert equal_values(
        ts.olympicMovingAverage(window=5, onlyValid=False, useReduced=True).values,
        [data[i][18] for i in range(len(data))],
    )
    assert equal_values(
        ts.olympicMovingAverage(window=5, onlyValid=True, useReduced=False).values,
        [data[i][21] for i in range(len(data))],
    )
    assert equal_values(
        ts.olympicMovingAverage(window=5, onlyValid=True, useReduced=True).values,
        [data[i][24] for i in range(len(data))],
    )


def test_protected() -> None:
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    values = [
        1000,
        1015,
        1030,
        1045,
        1060,
        math.inf,
        1090,
        1090,
        1120,
        1135,
        math.nan,
        1165,
        1180,
        1195,
        1210,
        1225,
        1240,
        1240,
        1270,
        math.inf,
        1300,
        1315,
        1330,
        1345,
    ]
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(len(values))], name="time"
    )
    ts = TimeSeries(f"Loc1.Flow.Inst.{intvl.name}.0.Computed")
    ts._data = pd.DataFrame(
        {
            "value": values,
            "quality": len(values) * [0],
        },
        index=times,
    )
    ts.iselectValid().isetProtected()
    unscreened_code = 0
    protected_code = Qual(
        [
            "Screened",
            "Unknown",
            "No_Range",
            "Original",
            "None",
            "None",
            "None",
            "Protected",
        ]
    ).code
    unprotected_code = Qual(
        [
            "Screened",
            "Unknown",
            "No_Range",
            "Original",
            "None",
            "None",
            "None",
            "Unprotected",
        ]
    ).code
    for tsv in ts.tsv:
        if np.isfinite(tsv.value.magnitude):
            assert tsv.quality.code == protected_code
        else:
            assert tsv.quality.code == unscreened_code
    ts.isetUnprotected()
    for tsv in ts.tsv:
        if np.isfinite(tsv.value.magnitude):
            assert tsv.quality.code == unprotected_code
        else:
            assert tsv.quality.code == unscreened_code


def test_screenWithValueRange() -> None:
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    values = [
        1000,
        1015,
        1030,
        1045,
        1060,
        math.inf,
        1090,
        1090,
        1120,
        1135,
        math.nan,
        1165,
        1180,
        1195,
        1210,
        1225,
        1240,
        1240,
        1270,
        -math.inf,
        1300,
        1315,
        1330,
        1300,
    ]
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(len(values))], name="time"
    )
    ts = TimeSeries(f"Loc1.Flow.Inst.{intvl.name}.0.Computed")
    ts._data = pd.DataFrame(
        {
            "value": values,
            "quality": len(values) * [0],
        },
        index=times,
    )
    minRejectLimit = 1030
    minQuestionLimit = 1060
    maxQuestionLimit = 1240
    maxRejectLimit = 1300
    unscreened_code = Qual(
        "Unscreened Unknown No_range Original None None None Unprotected".split()
    ).code
    okay_code = Qual(
        "Screened Okay No_range Original None None None Unprotected".split()
    ).code
    protected_code = Qual(
        "Screened Unknown No_range Original None None None Protected".split()
    ).code
    missing_code = Qual(
        "Screened Missing No_range Original None None None Unprotected".split()
    ).code
    question_code = Qual(
        "Screened Questionable No_range Original None None Absolute_Value Unprotected".split()
    ).code
    reject_code = Qual(
        "Screened Rejected No_range Original None None Absolute_Value Unprotected".split()
    ).code
    # -------------------- #
    # screenWithValueRange #
    # -------------------- #
    for minr in (minRejectLimit, math.nan):
        for minq in (minQuestionLimit, math.nan):
            for maxq in (maxQuestionLimit, math.nan):
                for maxr in (maxRejectLimit, math.nan):
                    ts2 = ts.screenWithValueRange(minr, minq, maxq, maxr)
                    for tsv in ts2.tsv:
                        if tsv.value.magnitude < minr or tsv.value.magnitude > maxr:
                            assert tsv.quality == reject_code
                        elif tsv.value.magnitude < minq or tsv.value.magnitude > maxq:
                            assert tsv.quality == question_code
                        elif math.isnan(tsv.value.magnitude):
                            assert tsv.quality == missing_code
                        else:
                            assert tsv.quality == okay_code
    # ------------------------------------------------ #
    # screenWithValueRange: work with protected values #
    # ------------------------------------------------ #
    for minr in (minRejectLimit, math.nan):
        for minq in (minQuestionLimit, math.nan):
            for maxq in (maxQuestionLimit, math.nan):
                for maxr in (maxRejectLimit, math.nan):
                    ts2 = (
                        ts.select(lambda tsv: cast(int, tsv.time.hour) % 2 == 0)
                        .isetProtected()
                        .screenWithValueRange(minr, minq, maxq, maxr)
                    )
                    for tsv in ts2.tsv:
                        if tsv.quality.protection:
                            assert tsv.quality == protected_code
                        elif tsv.value.magnitude < minr or tsv.value.magnitude > maxr:
                            assert tsv.quality == reject_code
                        elif tsv.value.magnitude < minq or tsv.value.magnitude > maxq:
                            assert tsv.quality == question_code
                        elif math.isnan(tsv.value.magnitude):
                            assert tsv.quality == missing_code
                        else:
                            assert tsv.quality == okay_code
    # ----------------------------------------- #
    # screenWithValueRange: work with selection #
    # ----------------------------------------- #
    time = HecTime("2024-10-10T06:00:00")
    for minr in (minRejectLimit, math.nan):
        for minq in (minQuestionLimit, math.nan):
            for maxq in (maxQuestionLimit, math.nan):
                for maxr in (maxRejectLimit, math.nan):
                    ts2 = ts.select(lambda tsv: tsv.time > time).screenWithValueRange(
                        minr, minq, maxq, maxr
                    )
                    for tsv in ts2.tsv:
                        if tsv.time <= time:
                            assert tsv.quality == unscreened_code
                        elif tsv.value.magnitude < minr or tsv.value.magnitude > maxr:
                            assert tsv.quality == reject_code
                        elif tsv.value.magnitude < minq or tsv.value.magnitude > maxq:
                            assert tsv.quality == question_code
                        elif math.isnan(tsv.value.magnitude):
                            assert tsv.quality == missing_code
                        else:
                            assert tsv.quality == okay_code


def test_screenWithValueChangeRate() -> None:
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    values = [
        1000,
        1015,  #      0.25, o
        1030,  #      0.25, o
        1045,  #      0.25, o
        1060,  #      0.25, o
        math.inf,  #   inf, r
        1090,  #      -inf, r
        1090,  #      0.00, o
        1120,  #      0.50, q
        1135,  #      0.25, o
        math.nan,  #   nan, m
        1165,  #       nan, m
        1180,  #      0.25, o
        1195,  #      0.25, o
        1210,  #      0.25, o
        1225,  #      0.25, o
        1240,  #      0.25, o
        1240,  #      0.00, o
        1270,  #      0.50, q
        -math.inf,  # -inf, r
        1300,  #       inf, r
        1315,  #      0.25, o
        1330,  #      0.25, o
        1300,  #     -0.50, q
    ]
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(len(values))], name="time"
    )
    ts = TimeSeries(f"Loc1.Flow.Inst.{intvl.name}.0.Computed")
    ts._data = pd.DataFrame(
        {
            "value": values,
            "quality": len(values) * [0],
        },
        index=times,
    )
    minRejectLimit = -0.6
    minQuestionLimit = -0.4
    maxQuestionLimit = 0.4
    maxRejectLimit = 0.6
    unscreened_code = Qual(
        "Unscreened Unknown No_range Original None None None Unprotected".split()
    ).code
    okay_code = Qual(
        "Screened Okay No_range Original None None None Unprotected".split()
    ).code
    protected_code = Qual(
        "Screened Unknown No_range Original None None None Protected".split()
    ).code
    missing_code = Qual(
        "Screened Missing No_range Original None None None Unprotected".split()
    ).code
    question_code = Qual(
        "Screened Questionable No_range Original None None Rate_of_Change Unprotected".split()
    ).code
    reject_code = Qual(
        "Screened Rejected No_range Original None None Rate_of_Change Unprotected".split()
    ).code
    # ------------------------- #
    # screenWithValueChangeRate #
    # ------------------------- #
    for minr in (minRejectLimit, math.nan):
        for minq in (minQuestionLimit, math.nan):
            for maxq in (maxQuestionLimit, math.nan):
                for maxr in (maxRejectLimit, math.nan):
                    ts2 = ts.screenWithValueChangeRate(minr, minq, maxq, maxr)
                    tsvs = ts2.tsv
                    for i, tsv in enumerate(tsvs):
                        if i == 0:
                            assert tsv.quality == unscreened_code
                        elif (
                            tsv.value.magnitude - tsvs[i - 1].value.magnitude
                        ) / 60.0 < minr or (
                            tsv.value.magnitude - tsvs[i - 1].value.magnitude
                        ) / 60.0 > maxr:
                            assert tsv.quality == reject_code
                        elif (
                            tsv.value.magnitude - tsvs[i - 1].value.magnitude
                        ) / 60.0 < minq or (
                            tsv.value.magnitude - tsvs[i - 1].value.magnitude
                        ) / 60.0 > maxq:
                            assert tsv.quality == question_code
                        elif math.isnan(tsv.value.magnitude) or math.isnan(
                            tsvs[i - 1].value.magnitude
                        ):
                            assert tsv.quality == missing_code
                        else:
                            assert tsv.quality == okay_code
    # ----------------------------------------------------- #
    # screenWithValueChangeRate: work with protected values #
    # ----------------------------------------------------- #
    for minr in (minRejectLimit, math.nan):
        for minq in (minQuestionLimit, math.nan):
            for maxq in (maxQuestionLimit, math.nan):
                for maxr in (maxRejectLimit, math.nan):
                    ts2 = (
                        ts.select(lambda tsv: cast(int, tsv.time.hour) % 2 == 0)
                        .isetProtected()
                        .screenWithValueChangeRate(minr, minq, maxq, maxr)
                    )
                    tsvs = ts2.tsv
                    for i, tsv in enumerate(tsvs):
                        if i == 0:
                            assert tsv.quality == unscreened_code
                        elif tsv.quality.protection:
                            assert tsv.quality == protected_code
                        elif (
                            tsv.value.magnitude - tsvs[i - 1].value.magnitude
                        ) / 60.0 < minr or (
                            tsv.value.magnitude - tsvs[i - 1].value.magnitude
                        ) / 60.0 > maxr:
                            assert tsv.quality == reject_code
                        elif (
                            tsv.value.magnitude - tsvs[i - 1].value.magnitude
                        ) / 60.0 < minq or (
                            tsv.value.magnitude - tsvs[i - 1].value.magnitude
                        ) / 60.0 > maxq:
                            assert tsv.quality == question_code
                        elif math.isnan(tsv.value.magnitude) or math.isnan(
                            tsvs[i - 1].value.magnitude
                        ):
                            assert tsv.quality == missing_code
                        else:
                            assert tsv.quality == okay_code
    # ---------------------------------------------- #
    # screenWithValueChangeRate: work with selection #
    # ---------------------------------------------- #
    time = HecTime("2024-10-10T06:00:00")
    for minr in (minRejectLimit, math.nan):
        for minq in (minQuestionLimit, math.nan):
            for maxq in (maxQuestionLimit, math.nan):
                for maxr in (maxRejectLimit, math.nan):
                    ts2 = ts.select(
                        lambda tsv: tsv.time > time
                    ).screenWithValueChangeRate(minr, minq, maxq, maxr)
                    tsvs = ts2.tsv
                    first = True
                    for i, tsv in enumerate(tsvs):
                        if tsv.time <= time:
                            first = True
                            assert tsv.quality == unscreened_code
                        elif (
                            tsv.value.magnitude - tsvs[i - 1].value.magnitude
                        ) / 60.0 < minr or (
                            tsv.value.magnitude - tsvs[i - 1].value.magnitude
                        ) / 60.0 > maxr:
                            first = False
                            assert tsv.quality == reject_code
                        elif (
                            tsv.value.magnitude - tsvs[i - 1].value.magnitude
                        ) / 60.0 < minq or (
                            tsv.value.magnitude - tsvs[i - 1].value.magnitude
                        ) / 60.0 > maxq:
                            first = False
                            assert tsv.quality == question_code
                        elif math.isnan(tsv.value.magnitude) or math.isnan(
                            tsvs[i - 1].value.magnitude
                        ):
                            first = False
                            assert tsv.quality == missing_code
                        else:
                            assert (
                                tsv.quality == unscreened_code if first else okay_code
                            )
                            first = False


def test_screenWithValueRangeOrChangeRate() -> None:
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    values = [
        1000,
        1015,
        1030,
        1045,
        1060,
        math.inf,
        1090,
        1090,
        1120,
        1135,
        math.nan,
        1165,
        1180,
        1195,
        1210,
        1225,
        1240,
        1240,
        1270,
        -math.inf,
        1300,
        1315,
        1330,
        1300,
    ]
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(len(values))], name="time"
    )
    ts = TimeSeries(f"Loc1.Flow.Inst.{intvl.name}.0.Computed")
    ts._data = pd.DataFrame(
        {
            "value": values,
            "quality": len(values) * [0],
        },
        index=times,
    )
    minValid = 1050
    maxValid = 1300
    maxChange = 15
    unscreened_code = Qual(
        "Unscreened Unknown No_range Original None None None Unprotected".split()
    ).code
    okay_code = Qual(
        "Screened Okay No_range Original None None None Unprotected".split()
    ).code
    protected_code = Qual(
        "Screened Unknown No_range Original None None None Protected".split()
    ).code
    missing_code = Qual(
        "Screened Missing No_range Original None None None Unprotected".split()
    ).code
    abs_value_code_original = Qual(
        "Screened Missing No_range Original None None Absolute_Value Unprotected".split()
    ).code
    abs_value_code_missing = Qual(
        "Screened Missing No_range Modified Automatic Missing Absolute_Value Unprotected".split()
    ).code
    abs_value_code_explicit = Qual(
        "Screened Rejected No_range Modified Automatic Explicit Absolute_Value Unprotected".split()
    ).code
    chg_value_code_original = Qual(
        "Screened Missing No_range Original None None Rate_of_Change Unprotected".split()
    ).code
    chg_value_code_missing = Qual(
        "Screened Missing No_range Modified Automatic Missing Rate_of_Change Unprotected".split()
    ).code
    chg_value_code_explicit = Qual(
        "Screened Rejected No_range Modified Automatic Explicit Rate_of_Change Unprotected".split()
    ).code
    # ----------------------------------------------------------- #
    #  screenValueRangeOrChangeRate: don't replace invalid values #
    # ----------------------------------------------------------- #
    for minv in (minValid, math.nan):
        for maxv in (maxValid, math.nan):
            for maxc in (maxChange, math.nan):
                ts2 = ts.screenWithValueRangeOrChange(minv, maxv, maxc, False)
                tsvs = ts2.tsv
                for i, tsv in enumerate(tsvs):
                    if tsv.value.magnitude < minv or tsv.value.magnitude > maxv:
                        assert tsv.quality == abs_value_code_original
                    elif (
                        i > 0
                        and abs(tsv.value.magnitude - tsvs[i - 1].value.magnitude)
                        > maxc
                    ):
                        assert tsv.quality == chg_value_code_original
                    elif math.isnan(tsv.value.magnitude):
                        assert tsv.quality == missing_code
                    else:
                        assert tsv.quality == okay_code
    # --------------------------------------------------------- #
    #  screenValueRangeOrChangeRate: work with protected values #
    # --------------------------------------------------------- #
    for minv in (minValid, math.nan):
        for maxv in (maxValid, math.nan):
            for maxc in (maxChange, math.nan):
                ts2 = (
                    ts.select(lambda tsv: cast(int, tsv.time.hour) % 2 == 0)
                    .isetProtected()
                    .iscreenWithValueRangeOrChange(minv, maxv, maxc)
                )
                tsvs = ts2.tsv
                for i, tsv in enumerate(tsvs):
                    if tsv.quality.protection:
                        assert tsv.quality == protected_code
                    elif math.isnan(tsv.value.magnitude):
                        assert tsv.quality in (
                            missing_code,
                            abs_value_code_missing,
                            chg_value_code_missing,
                        )
                    else:
                        assert tsv.quality == okay_code
    # -------------------------------------------------- #
    #  screenValueRangeOrChangeRate: work with selection #
    # -------------------------------------------------- #
    time = HecTime("2024-10-10T06:00:00")
    for minv in (minValid, math.nan):
        for maxv in (maxValid, math.nan):
            for maxc in (maxChange, math.nan):
                ts2 = ts.select(
                    lambda tsv: tsv.time > time
                ).screenWithValueRangeOrChange(minv, maxv, maxc)
                tsvs = ts2.tsv
                for i, tsv in enumerate(tsvs):
                    if tsv.time <= time:
                        assert tsv.quality == unscreened_code
                    elif math.isnan(tsv.value.magnitude):
                        assert tsv.quality in (
                            missing_code,
                            abs_value_code_missing,
                            chg_value_code_missing,
                        )
                    else:
                        assert tsv.quality == okay_code
    # -------------------------------------------------------------------------- #
    #  screenValueRangeOrChangeRate: specify non-NaN value, use Rejected quality #
    # -------------------------------------------------------------------------- #
    for minv in (minValid, math.nan):
        for maxv in (maxValid, math.nan):
            for maxc in (maxChange, math.nan):
                ts2 = ts.select(
                    lambda tsv: tsv.time > time
                ).screenWithValueRangeOrChange(minv, maxv, maxc, True, -901, "R")
                tsvs = ts2.tsv
                for i, tsv in enumerate(tsvs):
                    if tsv.time <= time:
                        assert tsv.quality == unscreened_code
                    elif tsv.value.magnitude == -901:
                        assert tsv.quality in (
                            abs_value_code_explicit,
                            chg_value_code_explicit,
                        )
                    elif math.isnan(tsv.value.magnitude):
                        assert tsv.quality == missing_code
                    else:
                        assert tsv.quality == okay_code


def test_screenWithDurationMagnitude() -> None:
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("6Hours")
    values = [
        0.300,
        0.250,
        0.450,
        0.400,
        0.400,
        math.inf,
        0.350,
        0.450,
        0.500,
        0.375,
        math.nan,
        0.000,
        0.000,
        0.050,
        0.350,
        0.100,
        0.350,
        0.275,
        0.425,
        -math.inf,
        0.125,
        0.075,
        0.225,
        0.150,
    ]
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(len(values))], name="time"
    )
    ts = TimeSeries(f"Loc1.Precip.Total.{intvl.name}.{intvl.name}.Raw")
    ts._data = pd.DataFrame(
        {
            "value": values,
            "quality": len(values) * [0],
        },
        index=times,
    )
    minMissingLimit = 0.051
    minRejectLimit = 0.101
    minQuestionLimit = 0.151
    maxQuestionLimit = 0.349
    maxRejectLimit = 0.399
    maxMissingLimit = 0.449
    unscreened_code = Qual(
        "Unscreened Unknown No_range Original None None None Unprotected".split()
    ).code
    okay_code = Qual(
        "Screened Okay No_range Original None None None Unprotected".split()
    ).code
    protected_code = Qual(
        "Screened Unknown No_range Original None None None Protected".split()
    ).code
    missing_code_unscreened = Qual(
        "Screened Missing No_range Original None None None Unprotected".split()
    ).code
    missing_code_screened = Qual(
        "Screened Missing No_Range Modified Automatic Missing Duration_Value Unprotected".split()
    ).code
    question_code = Qual(
        "Screened Questionable No_range Original None None Duration_Value Unprotected".split()
    ).code
    reject_code = Qual(
        "Screened Rejected No_range Original None None Duration_Value Unprotected".split()
    ).code
    # --------------------------- #
    # screenWithDurationMagnitude #
    # --------------------------- #
    for hours in 6, 8, 12:
        for pct in 50, 75:
            for minm in (minMissingLimit * hours / 6.0, math.nan):
                for minr in (minRejectLimit * hours / 6.0, math.nan):
                    for minq in (minQuestionLimit * hours / 6.0, math.nan):
                        for maxq in (maxQuestionLimit * hours / 6.0, math.nan):
                            for maxr in (maxRejectLimit * hours / 6.0, math.nan):
                                for maxm in (maxMissingLimit * hours / 6.0, math.nan):
                                    ts2 = ts.screenWithDurationMagnitude(
                                        f"{hours}Hours",
                                        minm,
                                        minr,
                                        minq,
                                        maxq,
                                        maxr,
                                        maxm,
                                        pct,
                                    )
                                    tsvs = ts2.tsv
                                    for i, tsv in enumerate(tsvs):
                                        invalid = (
                                            math.isnan(values[i])
                                            or math.isinf(values[i])
                                            or (
                                                hours > 6
                                                and pct > 50
                                                and (
                                                    math.isnan(values[i - 1])
                                                    or math.isinf(values[i - 1])
                                                )
                                            )
                                        )
                                        if not invalid:
                                            if (
                                                hours == 6
                                                or i == 0
                                                or math.isnan(values[i - 1])
                                                or math.isinf(values[i - 1])
                                            ):
                                                accum = values[i]
                                            else:
                                                if hours == 8:
                                                    accum = (
                                                        values[i] + values[i - 1] / 3.0
                                                    )
                                                else:
                                                    accum = values[i] + values[i - 1]
                                        if math.isnan(values[i]):
                                            assert tsv.quality == unscreened_code
                                        elif invalid:
                                            assert tsv.quality == unscreened_code
                                        elif hours > 6 and i == 0:
                                            assert tsv.quality == unscreened_code
                                        elif accum < minm or accum > maxm:
                                            assert tsv.quality == missing_code_screened
                                            assert math.isnan(tsv.value.magnitude)
                                        elif accum < minr or accum > maxr:
                                            assert tsv.quality == reject_code
                                        elif accum < minq or accum > maxq:
                                            assert tsv.quality == question_code
                                        elif math.isnan(tsv.value.magnitude):
                                            assert tsv.quality in (
                                                missing_code_unscreened,
                                                missing_code_screened,
                                            )
                                        elif all(
                                            [
                                                math.isnan(v)
                                                for v in (
                                                    minm,
                                                    maxm,
                                                    minr,
                                                    maxr,
                                                    minq,
                                                    maxq,
                                                )
                                            ]
                                        ):
                                            assert tsv.quality == unscreened_code
                                        else:
                                            assert tsv.quality == okay_code
    # ------------------------------------------------------- #
    # screenWithDurationMagnitude: work with protected values #
    # ------------------------------------------------------- #
    for hours in 6, 8, 12:
        for pct in 50, 75:
            for minm in (minMissingLimit * hours / 6.0, math.nan):
                for minr in (minRejectLimit * hours / 6.0, math.nan):
                    for minq in (minQuestionLimit * hours / 6.0, math.nan):
                        for maxq in (maxQuestionLimit * hours / 6.0, math.nan):
                            for maxr in (maxRejectLimit * hours / 6.0, math.nan):
                                for maxm in (maxMissingLimit * hours / 6.0, math.nan):
                                    ts2 = (
                                        ts.select(
                                            lambda tsv: cast(int, tsv.time.hour) % 24
                                            == 1
                                        )
                                        .isetProtected()
                                        .iscreenWithDurationMagnitude(
                                            f"{hours}Hours",
                                            minm,
                                            minr,
                                            minq,
                                            maxq,
                                            maxr,
                                            maxm,
                                            pct,
                                        )
                                    )
                                    tsvs = ts2.tsv
                                    for i, tsv in enumerate(tsvs):
                                        invalid = (
                                            math.isnan(values[i])
                                            or math.isinf(values[i])
                                            or (
                                                hours > 6
                                                and pct > 50
                                                and (
                                                    math.isnan(values[i - 1])
                                                    or math.isinf(values[i - 1])
                                                )
                                            )
                                        )
                                        if not invalid:
                                            if (
                                                hours == 6
                                                or i == 0
                                                or math.isnan(values[i - 1])
                                                or math.isinf(values[i - 1])
                                            ):
                                                accum = values[i]
                                            else:
                                                if hours == 8:
                                                    accum = (
                                                        values[i] + values[i - 1] / 3.0
                                                    )
                                                else:
                                                    accum = values[i] + values[i - 1]
                                        if tsv.quality.protection:
                                            assert tsv.quality == protected_code
                                            assert tsv.value.magnitude == values[i] or (
                                                math.isnan(tsv.value.magnitude)
                                                and math.isnan(values[i])
                                            )
                                        elif math.isnan(values[i]):
                                            assert tsv.quality == unscreened_code
                                        elif invalid:
                                            assert tsv.quality == unscreened_code
                                        elif hours > 6 and i == 0:
                                            assert tsv.quality == unscreened_code
                                        elif accum < minm or accum > maxm:
                                            assert tsv.quality == missing_code_screened
                                            assert math.isnan(tsv.value.magnitude)
                                        elif accum < minr or accum > maxr:
                                            assert tsv.quality == reject_code
                                        elif accum < minq or accum > maxq:
                                            assert tsv.quality == question_code
                                        elif math.isnan(tsv.value.magnitude):
                                            assert tsv.quality in (
                                                missing_code_unscreened,
                                                missing_code_screened,
                                            )
                                        elif all(
                                            [
                                                math.isnan(v)
                                                for v in (
                                                    minm,
                                                    maxm,
                                                    minr,
                                                    maxr,
                                                    minq,
                                                    maxq,
                                                )
                                            ]
                                        ):
                                            assert tsv.quality == unscreened_code
                                        else:
                                            assert tsv.quality == okay_code

    # ------------------------------------------------ #
    # screenWithDurationMagnitude: work with selection #
    # ------------------------------------------------ #
    time = HecTime("2024-10-11 07:00")
    for hours in 6, 8, 12:
        for pct in 50, 75:
            for minm in (minMissingLimit * hours / 6.0, math.nan):
                for minr in (minRejectLimit * hours / 6.0, math.nan):
                    for minq in (minQuestionLimit * hours / 6.0, math.nan):
                        for maxq in (maxQuestionLimit * hours / 6.0, math.nan):
                            for maxr in (maxRejectLimit * hours / 6.0, math.nan):
                                for maxm in (maxMissingLimit * hours / 6.0, math.nan):
                                    ts2 = ts.select(
                                        lambda tsv: tsv.time > time
                                    ).iscreenWithDurationMagnitude(
                                        f"{hours}Hours",
                                        minm,
                                        minr,
                                        minq,
                                        maxq,
                                        maxr,
                                        maxm,
                                        pct,
                                    )
                                    tsvs = ts2.tsv
                                    for i, tsv in enumerate(tsvs):
                                        invalid = (
                                            math.isnan(values[i])
                                            or math.isinf(values[i])
                                            or (
                                                hours > 6
                                                and pct > 50
                                                and (
                                                    math.isnan(values[i - 1])
                                                    or math.isinf(values[i - 1])
                                                )
                                            )
                                        )
                                        if not invalid:
                                            if (
                                                hours == 6
                                                or i == 0
                                                or math.isnan(values[i - 1])
                                                or math.isinf(values[i - 1])
                                            ):
                                                accum = values[i]
                                            else:
                                                if hours == 8:
                                                    accum = (
                                                        values[i] + values[i - 1] / 3.0
                                                    )
                                                else:
                                                    accum = values[i] + values[i - 1]
                                        if tsv.time <= time:
                                            assert tsv.quality == unscreened_code
                                        elif math.isnan(values[i]):
                                            assert tsv.quality == unscreened_code
                                        elif invalid:
                                            assert tsv.quality == unscreened_code
                                        elif (
                                            hours > 6 and i == 6
                                        ):  # first selected index
                                            assert tsv.quality == unscreened_code
                                        elif accum < minm or accum > maxm:
                                            assert tsv.quality == missing_code_screened
                                            assert math.isnan(tsv.value.magnitude)
                                        elif accum < minr or accum > maxr:
                                            assert tsv.quality == reject_code
                                        elif accum < minq or accum > maxq:
                                            assert tsv.quality == question_code
                                        elif math.isnan(tsv.value.magnitude):
                                            assert tsv.quality in (
                                                missing_code_unscreened,
                                                missing_code_screened,
                                            )
                                        elif all(
                                            [
                                                math.isnan(v)
                                                for v in (
                                                    minm,
                                                    maxm,
                                                    minr,
                                                    maxr,
                                                    minq,
                                                    maxq,
                                                )
                                            ]
                                        ):
                                            assert tsv.quality == unscreened_code
                                        else:
                                            assert tsv.quality == okay_code


def test_screenWithConstantValue() -> None:
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    values = [
        613.535,
        613.535,
        613.534,
        613.534,
        613.503,
        math.inf,
        613.532,
        613.504,
        613.537,
        613.51,
        math.nan,
        613.504,
        613.511,
        613.546,
        613.535,
        613.539,
        613.545,
        613.512,
        613.524,
        -math.inf,
        613.515,
        613.517,
        613.541,
        613.527,
    ]
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(len(values))], name="time"
    )
    ts = TimeSeries(f"Loc1.Elev.Inst.{intvl.name}.0.Computed")
    ts._data = pd.DataFrame(
        {
            "value": values,
            "quality": len(values) * [0],
        },
        index=times,
    )
    missingLimit = {2: 0.001, 4: 0.003, 6: 0.0035}
    rejectLimit = {2: 0.005, 4: 0.015, 6: 0.0175}
    questionLimit = {2: 0.01, 4: 0.03, 6: 0.035}
    unscreened_code = Qual(
        "Unscreened Unknown No_range Original None None None Unprotected".split()
    ).code
    okay_code = Qual(
        "Screened Okay No_range Original None None None Unprotected".split()
    ).code
    protected_code = Qual(
        "Screened Unknown No_range Original None None None Protected".split()
    ).code
    missing_code_unscreened = Qual(
        "Screened Missing No_range Original None None None Unprotected".split()
    ).code
    missing_code_screened = Qual(
        "Screened Missing No_range Modified Automatic Missing Constant_Value Unprotected".split()
    ).code
    question_code = Qual(
        "Screened Questionable No_range Original None None Constant_Value Unprotected".split()
    ).code
    reject_code = Qual(
        "Screened Rejected No_range Original None None Constant_Value Unprotected".split()
    ).code
    # ----------------------- #
    # screenWithConstantValue #
    # ----------------------- #
    for hours in 2, 4, 6:
        for m in missingLimit[hours], math.nan:
            for r in rejectLimit[hours], math.nan:
                for q in questionLimit[hours], math.nan:
                    for above in 613.5, 613.51:
                        for pct in 50, 90:
                            ts2 = ts.screenWithConstantValue(
                                f"{hours}Hours", m, r, q, above, pct
                            )
                            tsvs = ts2.tsv
                            for i, tsv in enumerate(tsvs):
                                vals = values[max(i - hours, 0) : i + 1]
                                valid_vals = [
                                    v
                                    for v in vals
                                    if not math.isnan(v) and not math.isinf(v)
                                ]
                                pct_valid = 100 * len(valid_vals) / len(vals)
                                max_change = max(valid_vals) - min(valid_vals)
                                if i < hours:
                                    assert tsv.quality == unscreened_code
                                elif pct_valid < pct:
                                    assert tsv.quality == unscreened_code
                                elif math.isnan(values[i]) or math.isinf(values[i]):
                                    assert tsv.quality == unscreened_code
                                elif values[i] < above:
                                    assert tsv.quality == unscreened_code
                                elif max_change < m:
                                    assert tsv.quality == missing_code_screened
                                    assert math.isnan(tsv.value.magnitude)
                                elif max_change < r:
                                    assert tsv.quality == reject_code
                                elif max_change < q:
                                    assert tsv.quality == question_code
                                elif all([math.isnan(v) for v in (m, r, q)]):
                                    assert tsv.quality == unscreened_code
                                else:
                                    assert tsv.quality == okay_code
    # --------------------------------------------------- #
    # screenWithConstantValue: work with protected values #
    # --------------------------------------------------- #
    for hours in 2, 4, 6:
        for m in missingLimit[hours], math.nan:
            for r in rejectLimit[hours], math.nan:
                for q in questionLimit[hours], math.nan:
                    for above in 613.5, 613.51:
                        for pct in 50, 90:
                            ts2 = (
                                ts.select(
                                    lambda tsv: cast(int, tsv.time.hour) % 24 == 1
                                )
                                .isetProtected()
                                .screenWithConstantValue(
                                    f"{hours}Hours", m, r, q, above, pct
                                )
                            )
                            tsvs = ts2.tsv
                            for i, tsv in enumerate(tsvs):
                                vals = values[max(i - hours, 0) : i + 1]
                                valid_vals = [
                                    v
                                    for v in vals
                                    if not math.isnan(v) and not math.isinf(v)
                                ]
                                pct_valid = 100 * len(valid_vals) / len(vals)
                                max_change = max(valid_vals) - min(valid_vals)
                                if tsv.quality.protection:
                                    assert tsv.quality == protected_code
                                    assert tsv.value.magnitude == values[i] or (
                                        math.isnan(tsv.value.magnitude)
                                        and math.isnan(values[i])
                                    )
                                elif i < hours:
                                    assert tsv.quality == unscreened_code
                                elif pct_valid < pct:
                                    assert tsv.quality == unscreened_code
                                elif math.isnan(values[i]) or math.isinf(values[i]):
                                    assert tsv.quality == unscreened_code
                                elif values[i] < above:
                                    assert tsv.quality == unscreened_code
                                elif max_change < m:
                                    assert tsv.quality == missing_code_screened
                                    assert math.isnan(tsv.value.magnitude)
                                elif max_change < r:
                                    assert tsv.quality == reject_code
                                elif max_change < q:
                                    assert tsv.quality == question_code
                                elif all([math.isnan(v) for v in (m, r, q)]):
                                    assert tsv.quality == unscreened_code
                                else:
                                    assert tsv.quality == okay_code
    # -------------------------------------------- #
    # screenWithConstantValue: work with selection #
    # -------------------------------------------- #
    time = HecTime("2024-10-10T06:00:00")
    for hours in 2, 4, 6:
        for m in missingLimit[hours], math.nan:
            for r in rejectLimit[hours], math.nan:
                for q in questionLimit[hours], math.nan:
                    for above in 613.5, 613.51:
                        for pct in 50, 90:
                            ts2 = ts.select(
                                lambda tsv: tsv.time > time
                            ).screenWithConstantValue(
                                f"{hours}Hours", m, r, q, above, pct
                            )
                            tsvs = ts2.tsv
                            for i, tsv in enumerate(tsvs):
                                vals = values[max(i - hours, 0) : i + 1]
                                valid_vals = [
                                    v
                                    for v in vals
                                    if not math.isnan(v) and not math.isinf(v)
                                ]
                                pct_valid = 100 * len(valid_vals) / len(vals)
                                max_change = max(valid_vals) - min(valid_vals)
                                if i < hours + 6:  # time is at hour 5
                                    assert tsv.quality == unscreened_code
                                elif pct_valid < pct:
                                    assert tsv.quality == unscreened_code
                                elif math.isnan(values[i]) or math.isinf(values[i]):
                                    assert tsv.quality == unscreened_code
                                elif values[i] < above:
                                    assert tsv.quality == unscreened_code
                                elif max_change < m:
                                    assert tsv.quality == missing_code_screened
                                    assert math.isnan(tsv.value.magnitude)
                                elif max_change < r:
                                    assert tsv.quality == reject_code
                                elif max_change < q:
                                    assert tsv.quality == question_code
                                elif all([math.isnan(v) for v in (m, r, q)]):
                                    assert tsv.quality == unscreened_code
                                else:
                                    assert tsv.quality == okay_code


def test_screenWithForwardMovingAverage() -> None:
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    values = [
        1000,
        1015,
        1030,
        1045,
        1060,
        math.inf,
        1090,
        1090,
        1120,
        1135,
        math.nan,
        1165,
        1180,
        1195,
        1210,
        1225,
        1240,
        1240,
        1270,
        -math.inf,
        1300,
        1315,
        1330,
        1300,
    ]
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(len(values))], name="time"
    )
    ts = TimeSeries(f"Loc1.Flow.Inst.{intvl.name}.0.Computed")
    ts._data = pd.DataFrame(
        {
            "value": values,
            "quality": len(values) * [0],
        },
        index=times,
    )
    unscreened_code = Qual(
        "Unscreened Unknown No_range Original None None None Unprotected".split()
    ).code
    okay_code = Qual(
        "Screened Okay No_range Original None None None Unprotected".split()
    ).code
    protected_code = Qual(
        "Screened Unknown No_range Original None None None Protected".split()
    ).code
    missing_code_unscreened = Qual(
        "Screened Missing No_range Original None None None Unprotected".split()
    ).code
    missing_code_screened = Qual(
        "Screened Missing No_range Modified Automatic Missing Relative_Value Unprotected".split()
    ).code
    question_code = Qual(
        "Screened Questionable No_range Original None None Relative_Value Unprotected".split()
    ).code
    reject_code = Qual(
        "Screened Rejected No_range Original None None Relative_Value Unprotected".split()
    ).code
    # ------------------------------ #
    # screenWithForwardMovingAverage #
    # ------------------------------ #
    for window in 3, 5:
        for onlyValid in False, True:
            for useReduced in False, True:
                for diffLimit in 10, 15:
                    for failedValidity in "QRM":
                        ts2 = ts.forwardMovingAverage(window, onlyValid, useReduced)
                        averaged = ts2.values
                        ts3 = ts.screenWithForwardMovingAverage(
                            window, onlyValid, useReduced, diffLimit, failedValidity
                        )
                        tsvs = ts3.tsv
                        for i, tsv in enumerate(tsvs):
                            if math.isnan(values[i]) or math.isinf(values[i]):
                                assert tsv.quality == missing_code_unscreened
                            elif math.isnan(averaged[i]):
                                assert tsv.quality == unscreened_code
                            elif abs(averaged[i] - values[i]) > diffLimit:
                                if failedValidity == "Q":
                                    assert tsv.quality == question_code
                                elif failedValidity == "R":
                                    assert tsv.quality == reject_code
                                else:
                                    assert tsv.quality == missing_code_screened
                                    assert math.isnan(tsv.value.magnitude)
                            else:
                                assert tsv.quality == okay_code
    # ---------------------------------------------------------- #
    # screenWithForwardMovingAverage: work with protected values #
    # ---------------------------------------------------------- #
    for window in 3, 5:
        for onlyValid in False, True:
            for useReduced in False, True:
                for diffLimit in 10, 15:
                    for failedValidity in "QRM":
                        ts2 = ts.forwardMovingAverage(window, onlyValid, useReduced)
                        averaged = ts2.values
                        ts3 = (
                            ts.select(lambda tsv: cast(int, tsv.time.hour) % 24 == 1)
                            .isetProtected()
                            .screenWithForwardMovingAverage(
                                window, onlyValid, useReduced, diffLimit, failedValidity
                            )
                        )
                        tsvs = ts3.tsv
                        for i, tsv in enumerate(tsvs):
                            if tsv.quality.protection:
                                assert tsv.quality == protected_code
                                assert tsv.value.magnitude == values[i] or (
                                    math.isnan(tsv.value.magnitude)
                                    and math.isnan(values[i])
                                )
                            elif math.isnan(values[i]) or math.isinf(values[i]):
                                assert tsv.quality == missing_code_unscreened
                            elif math.isnan(averaged[i]):
                                assert tsv.quality == unscreened_code
                            elif abs(averaged[i] - values[i]) > diffLimit:
                                if failedValidity == "Q":
                                    assert tsv.quality == question_code
                                elif failedValidity == "R":
                                    assert tsv.quality == reject_code
                                else:
                                    assert tsv.quality == missing_code_screened
                                    assert math.isnan(tsv.value.magnitude)
                            else:
                                assert tsv.quality == okay_code
    # --------------------------------------------------- #
    # screenWithForwardMovingAverage: work with selection #
    # --------------------------------------------------- #
    time = HecTime("2024-10-10T06:00:00")
    for window in 3, 5:
        for onlyValid in False, True:
            for useReduced in False, True:
                for diffLimit in 10, 15:
                    for failedValidity in "QRM":
                        ts2 = ts.forwardMovingAverage(window, onlyValid, useReduced)
                        averaged = ts2.values
                        ts3 = ts.select(
                            lambda tsv: tsv.time > time
                        ).screenWithForwardMovingAverage(
                            window, onlyValid, useReduced, diffLimit, failedValidity
                        )
                        tsvs = ts3.tsv
                        for i, tsv in enumerate(tsvs):
                            if tsv.time <= time:
                                assert tsv.quality == unscreened_code
                            elif math.isnan(values[i]) or math.isinf(values[i]):
                                assert tsv.quality == missing_code_unscreened
                            elif math.isnan(averaged[i]):
                                assert tsv.quality == unscreened_code
                            elif abs(averaged[i] - values[i]) > diffLimit:
                                if failedValidity == "Q":
                                    assert tsv.quality == question_code
                                elif failedValidity == "R":
                                    assert tsv.quality == reject_code
                                else:
                                    assert tsv.quality == missing_code_screened
                                    assert math.isnan(tsv.value.magnitude)
                            else:
                                assert tsv.quality == okay_code


def test_estimateMissingValues() -> None:
    #                  [-] Accumulation      [-] Accumulation      [-] Accumulation      [-] Accumulation      [+] Accumulation      [+] Accumulation      [+] Accumulation      [+] Accumulation
    #                  [-] Estimate Rejected [-] Estimate Rejected [+] Estimate Rejected [+] Estimate Rejected [-] Estimate Rejected [-] Estimate Rejected [+] Estimate Rejected [+] Estimate Rejected
    #    Original      [-] Set Questionable  [+] Set Questionable  [-] Set Questionable  [+] Set Questionable  [-] Set Questionable  [+] Set Questionable  [-] Set Questionable  [+] Set Questionable
    #    ------------- --------------------- --------------------- --------------------- --------------------- --------------------- --------------------- --------------------- ---------------------
    #            0   1              2     3                4     5               6     7               8     9              10    11              12    13             14    15              16    17
    data = """ 
        [[    1000,  3,          1000,    3,            1000,    3,           1000,    3,           1000,    3,           1000,    3,           1000,    3,          1000,    3,           1000,    3],
         [    1015,  3,          1015,    3,            1015,    3,           1015,    3,           1015,    3,           1015,    3,           1015,    3,          1015,    3,           1015,    3],
         [math.nan,  5,   323.3333333, 2435,     323.3333333, 2441,           1030, 2435,           1030, 2441,       math.nan,    5,       math.nan,    5,          1030, 2435,           1030, 2441],
         [math.nan,  5,  -368.3333333, 2435,    -368.3333333, 2441,           1045, 2435,           1045, 2441,       math.nan,    5,       math.nan,    5,          1045, 2435,           1045, 2441],
         [   -1060, 17,         -1060,   17,           -1060,   17,           1060, 2435,           1060, 2441,          -1060,   17,          -1060,   17,          1060, 2435,           1060, 2441],
         [math.nan,  5,  -338.3333333, 2435,    -338.3333333, 2441,           1075, 2435,           1075, 2441,   -338.3333333, 2435,   -338.3333333, 2441,          1075, 2435,           1075, 2441],
         [math.nan,  5,   383.3333333, 2435,     383.3333333, 2441,           1090, 2435,           1090, 2441,    383.3333333, 2435,    383.3333333, 2441,          1090, 2435,           1090, 2441],
         [    1105,  3,          1105,    3,            1105,    3,           1105,    3,           1105,    3,           1105,    3,           1105,    3,          1105,    3,           1105,    3],
         [    1120,  3,          1120,    3,            1120,    3,           1120,    3,           1120,    3,           1120,    3,           1120,    3,          1120,    3,           1120,    3],
         [    1135,  3,          1135,    3,            1135,    3,           1135,    3,           1135,    3,           1135,    3,           1135,    3,          1135,    3,           1135,    3],
         [    1050,  3,          1050,    3,            1050,    3,           1050,    3,           1050,    3,           1050,    3,           1050,    3,          1050,    3,           1050,    3],
         [    1165,  3,          1165,    3,            1165,    3,           1165,    3,           1165,    3,           1165,    3,           1165,    3,          1165,    3,           1165,    3],
         [    1180,  3,          1180,    3,            1180,    3,           1180,    3,           1180,    3,           1180,    3,           1180,    3,          1180,    3,           1180,    3],
         [    1195,  3,          1195,    3,            1195,    3,           1195,    3,           1195,    3,           1195,    3,           1195,    3,          1195,    3,           1195,    3],
         [math.nan,  5,      math.nan,    5,        math.nan,    5,       math.nan,    5,       math.nan,    5,           1195, 2435,           1195, 2441,          1195, 2435,           1195, 2441],
         [math.nan,  5,      math.nan,    5,        math.nan,    5,       math.nan,    5,       math.nan,    5,           1195, 2435,           1195, 2441,          1195, 2435,           1195, 2441],
         [math.nan,  5,      math.nan,    5,        math.nan,    5,       math.nan,    5,       math.nan,    5,           1195, 2435,           1195, 2441,          1195, 2435,           1195, 2441],
         [math.nan,  5,      math.nan,    5,        math.nan,    5,       math.nan,    5,       math.nan,    5,           1195, 2435,           1195, 2441,          1195, 2435,           1195, 2441],
         [math.nan,  5,      math.nan,    5,        math.nan,    5,       math.nan,    5,       math.nan,    5,           1195, 2435,           1195, 2441,          1195, 2435,           1195, 2441],
         [math.nan,  5,      math.nan,    5,        math.nan,    5,       math.nan,    5,       math.nan,    5,           1195, 2435,           1195, 2441,          1195, 2435,           1195, 2441],
         [    1195,  3,          1195,    3,            1195,    3,           1195,    3,           1195,    3,           1195,    3,           1195,    3,          1195,    3,           1195,    3],
         [    1315,  3,          1315,    3,            1315,    3,           1315,    3,           1315,    3,           1315,    3,           1315,    3,          1315,    3,           1315,    3],
         [    1330,  3,          1330,    3,            1330,    3,           1330,    3,           1330,    3,           1330,    3,           1330,    3,          1330,    3,           1330,    3],
         [    1300,  3,          1300,    3,            1300,    3,           1300,    3,           1300,    3,           1300,    3,           1300,    3,          1300,    3,           1300,    3]]
"""
    dataVals = np.transpose(eval(data.strip()))
    columns = {
        # value columns, quality columns are this plus 1
        (False, False, False): 2,
        (False, False, True): 4,
        (False, True, False): 6,
        (False, True, True): 8,
        (True, False, False): 10,
        (True, False, True): 12,
        (True, True, False): 14,
        (True, True, True): 16,
    }
    start_time = HecTime("2024-10-10T01:00:00")
    intvl = Interval.getCwms("1Hour")
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(len(dataVals[0]))],
        name="time",
    )
    ts = TimeSeries(f"Loc1.Flow.Inst.{intvl.name}.0.Computed")
    ts._data = pd.DataFrame(
        {
            "value": dataVals[0],
            "quality": list(map(int, dataVals[1])),
        },
        index=times,
    )
    max_missing_count = 5
    # --------------------- #
    # estimateMissingValues #
    # --------------------- #
    for accumulation in (False, True):
        for estimate_rejected in (False, True):
            for set_questionable in (False, True):
                ts2 = ts.estimateMissingValues(
                    max_missing_count, accumulation, estimate_rejected, set_questionable
                )
                key = (accumulation, estimate_rejected, set_questionable)
                expected_values = dataVals[columns[key]]
                expected_qualities = list(map(int, dataVals[columns[key] + 1]))
                assert np.allclose(ts2.values, expected_values, equal_nan=True)
                assert all(
                    [
                        ts2.qualities[i] == expected_qualities[i]
                        for i in range(len(expected_qualities))
                    ]
                )
    # ------------------------------------------------- #
    # estimateMissingValues: work with protected values #
    # ------------------------------------------------- #
    for accumulation in (False, True):
        for estimate_rejected in (False, True):
            for set_questionable in (False, True):
                ts2 = (
                    ts.select(lambda tsv: cast(int, tsv.time.hour) % 2 == 1)
                    .setProtected()
                    .estimateMissingValues(
                        max_missing_count,
                        accumulation,
                        estimate_rejected,
                        set_questionable,
                    )
                )
                key = (accumulation, estimate_rejected, set_questionable)
                expected_values = copy.deepcopy(dataVals[columns[key]])
                expected_qualities = list(map(int, dataVals[columns[key] + 1]))
                dv0 = dataVals[0][:]
                dv1 = dataVals[1][:]
                for i in range(0, len(dv0), 2):
                    expected_values[i] = dv0[i]
                    expected_qualities[i] = (
                        Qual(int(dv1[i])).setProtection("Protected").unsigned
                    )
                assert np.allclose(ts2.values, expected_values, equal_nan=True)
                assert all(
                    [
                        ts2.qualities[i] == expected_qualities[i]
                        for i in range(len(expected_qualities))
                    ]
                )
    # ------------------------------------------ #
    # estimateMissingValues: work with selection #
    # ------------------------------------------ #
    time = HecTime("2024-10-10T06:00:00")
    time_offset = 6
    for accumulation in (False, True):
        for estimate_rejected in (False, True):
            for set_questionable in (False, True):
                ts2 = ts.select(lambda tsv: tsv.time > time).estimateMissingValues(
                    max_missing_count,
                    accumulation,
                    estimate_rejected,
                    set_questionable,
                )
                key = (accumulation, estimate_rejected, set_questionable)
                expected_values = []
                expected_qualities = []
                for i in range(len(ts)):
                    expected_values.append(
                        dataVals[0][i]
                        if i <= time_offset
                        else dataVals[columns[key]][i]
                    )
                    expected_qualities.append(
                        int(dataVals[1][i])
                        if i <= time_offset
                        else dataVals[columns[key] + 1][i]
                    )
                assert np.allclose(ts2.values, expected_values, equal_nan=True)
                assert all(
                    [
                        ts2.qualities[i] == expected_qualities[i]
                        for i in range(len(expected_qualities))
                    ]
                )


def test_expand_collapse_trim() -> None:
    start_time = HecTime("2024-10-15T01:00:00")
    intvl = Interval.getCwms("1Day")
    values = [
        1000,
        1015,
        1030,
        1045,
        1060,
        math.nan,
        math.nan,
        math.nan,
        math.nan,
        math.nan,
        math.nan,
        1165,
        1180,
        1195,
        1210,
        1225,
        1240,
        math.inf,
        1270,
        -math.inf,
        1300,
        1315,
        1330,
        1300,
    ]
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(len(values))], name="time"
    )
    ts = TimeSeries(f"Loc1.Flow.Inst.{intvl.name}.0.Computed")
    ts._data = pd.DataFrame(
        {
            "value": values,
            "quality": 5 * [0] + 6 * [5] + 13 * [0],
        },
        index=times,
    )
    # ------------------------------------------#
    # RTS without protected values or selection #
    # ------------------------------------------#
    expectedLength1 = len(ts)
    expectedTimes1 = ts.times[:]
    expectedValues1 = ts.values[:]
    expectedQualities1 = ts.qualities[:]
    ts2 = ts.collapse()
    expectedLength2 = expectedLength1 - 6
    expectedTimes = expectedTimes1[:5] + expectedTimes1[11:]
    expectedValues = expectedValues1[:5] + expectedValues1[11:]
    expectedQualities = expectedQualities1[:5] + expectedQualities1[11:]
    assert len(ts2) == expectedLength1
    assert all(ts2.times[i] == expectedTimes[i] for i in range(expectedLength2))
    assert np.allclose(ts2.values, expectedValues, equal_nan=True)
    assert all(ts2.qualities[i] == expectedQualities[i] for i in range(expectedLength2))
    ts2.iexpand("2024-10-13T01:00:00", "2024-11-09T01:00:00")
    expectedLength2 = expectedLength1 + 4
    expectedTimes = (
        ["2024-10-13 01:00:00", "2024-10-14 01:00:00"]
        + expectedTimes1
        + ["2024-11-08 01:00:00", "2024-11-09 01:00:00"]
    )
    expectedValues = [math.nan, math.nan] + expectedValues1 + [math.nan, math.nan]
    expectedQualities = [5, 5] + expectedQualities1 + [5, 5]
    assert len(ts2) == expectedLength2
    assert all(ts2.times[i] == expectedTimes[i] for i in range(expectedLength2))
    assert np.allclose(ts2.values, expectedValues, equal_nan=True)
    assert all(ts2.qualities[i] == expectedQualities[i] for i in range(expectedLength2))
    ts2.itrim()
    assert len(ts2) == expectedLength1
    assert all(ts2.times[i] == expectedTimes1[i] for i in range(expectedLength1))
    assert np.allclose(ts2.values, expectedValues1, equal_nan=True)
    assert all(
        ts2.qualities[i] == expectedQualities1[i] for i in range(expectedLength1)
    )
    # ----------------------------------------#
    # RTS with protected values and selection #
    # ----------------------------------------#
    Qual.setReturnUnsignedCodes()
    ts2 = ts.select(
        lambda tsv: tsv.time == HecTime("2024-10-20T01:00:00")
    ).isetProtected()
    ts2.iselect(lambda tsv: tsv.time == HecTime("2024-10-25T01:00:00"))
    # print(ts.data)
    expectedLength1 = len(ts)
    expectedTimes1 = ts2.times[:]
    expectedValues1 = ts2.values[:]
    expectedQualities1 = ts2.qualities[:]
    ts2 = ts2.icollapse()
    # print(ts2.data)
    expectedLength2 = expectedLength1 - 4
    expectedTimes = expectedTimes1[:6] + expectedTimes1[10:]
    expectedValues = expectedValues1[:6] + expectedValues1[10:]
    expectedQualities = expectedQualities1[:6] + expectedQualities1[10:]
    assert len(ts2) == expectedLength1
    assert all(ts2.times[i] == expectedTimes[i] for i in range(expectedLength2))
    assert np.allclose(ts2.values, expectedValues, equal_nan=True)
    assert all(ts2.qualities[i] == expectedQualities[i] for i in range(expectedLength2))
    ts2.iexpand("2024-10-13T01:00:00", "2024-11-09T01:00:00")
    # print(ts2.data)
    expectedLength2 = expectedLength1 + 4
    expectedTimes = (
        ["2024-10-13 01:00:00", "2024-10-14 01:00:00"]
        + expectedTimes1
        + ["2024-11-08 01:00:00", "2024-11-09 01:00:00"]
    )
    expectedValues = [math.nan, math.nan] + expectedValues1 + [math.nan, math.nan]
    expectedQualities = [5, 5] + expectedQualities1 + [5, 5]
    assert len(ts2) == expectedLength2
    assert all(ts2.times[i] == expectedTimes[i] for i in range(expectedLength2))
    assert np.allclose(ts2.values, expectedValues, equal_nan=True)
    assert all(ts2.qualities[i] == expectedQualities[i] for i in range(expectedLength2))
    selected = ts2.selected  # save selection
    ts2.iselect(lambda tsv: tsv.time == HecTime("2024-11-08 01:00:00")).isetProtected()
    cast(pd.DataFrame, ts2.data)["selected"] = selected  # restore selection
    ts2.iselect(lambda tsv: tsv.time == HecTime("2024-10-14 01:00:00"), Combine.OR)
    ts2.itrim()
    # print(ts2.data)
    expectedLength2 = expectedLength1 + 2
    expectedTimes = ["2024-10-14 01:00:00"] + expectedTimes1 + ["2024-11-08 01:00:00"]
    expectedValues = [math.nan] + expectedValues1 + [math.nan]
    expectedQualities = [5] + expectedQualities1 + [2147483653]
    assert len(ts2) == expectedLength2
    assert all(ts2.times[i] == expectedTimes[i] for i in range(expectedLength2))
    assert np.allclose(ts2.values, expectedValues, equal_nan=True)
    assert all(ts2.qualities[i] == expectedQualities[i] for i in range(expectedLength2))
    # ----------------------------------------#
    # LRTS with protected values or selection #
    # ----------------------------------------#
    ts2 = ts.asTimeZone("US/Pacific")
    ts2.iselect(
        lambda tsv: tsv.time == HecTime("2024-10-20T01:00:00-07:00")
    ).isetProtected()
    ts2.iselect(lambda tsv: tsv.time == HecTime("2024-10-25T01:00:00-07:00"))
    # print(ts.data)
    expectedLength1 = len(ts)
    expectedTimes1 = ts2.times[:]
    expectedValues1 = ts2.values[:]
    expectedQualities1 = ts2.qualities[:]
    ts2 = ts2.icollapse()
    # print(ts2.data)
    expectedLength2 = expectedLength1 - 4
    expectedTimes = expectedTimes1[:6] + expectedTimes1[10:]
    expectedValues = expectedValues1[:6] + expectedValues1[10:]
    expectedQualities = expectedQualities1[:6] + expectedQualities1[10:]
    assert len(ts2) == expectedLength1
    assert all(ts2.times[i] == expectedTimes[i] for i in range(expectedLength2))
    assert np.allclose(ts2.values, expectedValues, equal_nan=True)
    assert all(ts2.qualities[i] == expectedQualities[i] for i in range(expectedLength2))
    ts2.iexpand("2024-10-13T01:00:00-07:00", "2024-11-09T01:00:00-08:00")
    # print(ts2.data)
    expectedLength2 = expectedLength1 + 4
    expectedTimes = (
        ["2024-10-13 01:00:00-07:00", "2024-10-14 01:00:00-07:00"]
        + expectedTimes1
        + ["2024-11-08 01:00:00-08:00", "2024-11-09 01:00:00-08:00"]
    )
    expectedValues = [math.nan, math.nan] + expectedValues1 + [math.nan, math.nan]
    expectedQualities = [5, 5] + expectedQualities1 + [5, 5]
    assert len(ts2) == expectedLength2
    assert all(ts2.times[i] == expectedTimes[i] for i in range(expectedLength2))
    assert np.allclose(ts2.values, expectedValues, equal_nan=True)
    assert all(ts2.qualities[i] == expectedQualities[i] for i in range(expectedLength2))
    selected = ts2.selected  # save selection
    ts2.iselect(
        lambda tsv: tsv.time == HecTime("2024-11-08 01:00:00-08:00")
    ).isetProtected()
    cast(pd.DataFrame, ts2.data)["selected"] = selected  # restore selection
    ts2.iselect(
        lambda tsv: tsv.time == HecTime("2024-10-14 01:00:00-07:00"), Combine.OR
    )
    ts2.itrim()
    # print(ts2.data)
    expectedLength2 = expectedLength1 + 2
    expectedTimes = (
        ["2024-10-14 01:00:00-07:00"] + expectedTimes1 + ["2024-11-08 01:00:00-08:00"]
    )
    expectedValues = [math.nan] + expectedValues1 + [math.nan]
    expectedQualities = [5] + expectedQualities1 + [2147483653]
    assert len(ts2) == expectedLength2
    assert all(ts2.times[i] == expectedTimes[i] for i in range(expectedLength2))
    assert np.allclose(ts2.values, expectedValues, equal_nan=True)
    assert all(ts2.qualities[i] == expectedQualities[i] for i in range(expectedLength2))


def test_merge() -> None:
    start_time = HecTime("2024-10-15T01:00:00")
    intvl = Interval.getCwms("1Day")
    values1 = [
        1000,
        1015,
        1030,
        1045,
        1060,
        math.nan,
        math.nan,
        math.nan,
        math.nan,
        math.nan,
        math.nan,
        1165,
        1180,
        1195,
        1210,
        1225,
        1240,
        math.inf,
        1270,
        -math.inf,
        1300,
        1315,
        1330,
        1300,
    ]
    times = pd.Index(  # type: ignore
        [(start_time + i * intvl).datetime() for i in range(len(values1))], name="time"
    )
    ts1 = TimeSeries(f"Loc1.Flow.Inst.{intvl.name}.0.Computed")
    ts1._data = pd.DataFrame(
        {
            "value": values1,
            "quality": 5 * [0] + 6 * [5] + 13 * [0],
        },
        index=times,
    )
    values2 = [
        2000,
        2015,
        2030,
        2045,
        2060,
        2075,
        math.inf,
        2105,
        -math.inf,
        2135,
        2150,
        2165,
        2180,
        2195,
        2210,
        2225,
        2240,
        2250,
        2270,
        2285,
        math.nan,
        math.nan,
        2330,
        2300,
    ]
    times = pd.Index(
        [(start_time + i * intvl).datetime() for i in range(len(values1))], name="time"
    )
    ts2 = TimeSeries(f"Loc1.Flow.Inst.{intvl.name}.0.Computed")
    ts2._data = pd.DataFrame(
        {
            "value": values2,
            "quality": 20 * [0] + 2 * [5] + 2 * [0],
        },
        index=times,
    )
    # ------------------------------------- #
    # same time window, no protected values #
    # ------------------------------------- #
    ts3 = ts1.merge(ts2)
    expectedLength = len(ts1)
    expectedValues = [
        (
            ts2.values[i]
            if math.isnan(ts1.values[i])
            or math.isinf(ts1.values[i])
            and not math.isnan(ts2.values[i])
            else ts1.values[i]
        )
        for i in range(expectedLength)
    ]
    expectedQualities = [
        (
            ts2.qualities[i]
            if math.isnan(ts1.values[i])
            or math.isinf(ts1.values[i])
            and not math.isnan(ts2.values[i])
            else ts1.qualities[i]
        )
        for i in range(expectedLength)
    ]
    assert len(ts3) == expectedLength
    assert all([ts3.times[i] == ts2.times[i] for i in range(len(ts1))])
    assert np.allclose(ts3.values, expectedValues, equal_nan=True)
    assert all(ts3.qualities[i] == expectedQualities[i] for i in range(expectedLength))
    # ------------------------------ #
    # test merging empty time series #
    # ------------------------------ #
    ts1_copy = ts1.copy()  # will restore later
    ts2_copy = ts2.copy()  # will restore later
    ts1._data = None
    ts3 = ts1.merge(ts2)
    assert len(ts3) == expectedLength
    assert all([ts3.times[i] == ts2.times[i] for i in range(expectedLength)])
    assert np.allclose(ts3.values, ts2.values, equal_nan=True)
    assert all(ts3.qualities[i] == ts2.qualities[i] for i in range(expectedLength))
    ts3 = ts2.merge(ts1)
    assert len(ts3) == expectedLength
    assert all([ts3.times[i] == ts2.times[i] for i in range(expectedLength)])
    assert np.allclose(ts3.values, ts2.values, equal_nan=True)
    assert all(ts3.qualities[i] == ts2.qualities[i] for i in range(expectedLength))
    # ---------------------------------- #
    # same time window, protected values #
    # ---------------------------------- #
    ts1 = ts1_copy
    ts2 = ts2_copy
    ts1.iselect(5).isetProtected()
    ts2.iselect(21).isetProtected()
    ts3 = ts1.merge(ts2)
    expectedValues[5] = ts1.values[5]
    expectedQualities[5] = ts1.qualities[5]
    expectedValues[21] = ts2.values[21]
    expectedQualities[21] = ts2.qualities[21]
    assert len(ts3) == expectedLength
    assert all([ts3.times[i] == ts2.times[i] for i in range(len(ts1))])
    assert np.allclose(ts3.values, expectedValues, equal_nan=True)
    assert all(ts3.qualities[i] == expectedQualities[i] for i in range(expectedLength))
    # ---------------------- #
    # differing time windows #
    # ---------------------- #
    ts1 = ts1_copy
    ts2 = ts2_copy
    shift_offset = 6  # intervals
    ts2 >>= shift_offset
    ts3 = ts1.merge(ts2)
    expectedLength += shift_offset
    expectedTimes = sorted(set(ts1.times) | set(ts2.times))
    expectedValues = (
        ts1.values[:shift_offset]
        + [
            (
                ts2.values[i - shift_offset]
                if math.isnan(ts1.values[i])
                or math.isinf(ts1.values[i])
                and not math.isnan(ts2.values[i - shift_offset])
                else ts1.values[i]
            )
            for i in range(shift_offset, len(ts1))
        ]
        + ts2.values[-shift_offset:]
    )
    expectedQualities = (
        ts1.qualities[:shift_offset]
        + [
            (
                ts2.qualities[i - shift_offset]
                if math.isnan(ts1.values[i])
                or math.isinf(ts1.values[i])
                and not math.isnan(ts2.values[i - shift_offset])
                else ts1.qualities[i]
            )
            for i in range(shift_offset, len(ts1))
        ]
        + ts2.qualities[-shift_offset:]
    )
    assert len(ts3) == expectedLength
    assert all([ts3.times[i] == expectedTimes[i] for i in range(len(ts1))])
    assert np.allclose(ts3.values, expectedValues, equal_nan=True)
    assert all(ts3.qualities[i] == expectedQualities[i] for i in range(expectedLength))
    # --------------------- #
    # test mixing intervals #
    # --------------------- #
    intvl = Interval.getCwms("12Hours")
    times = pd.Index(
        [(start_time + i * intvl).datetime() for i in range(len(values1))], name="time"
    )
    ts4 = TimeSeries(f"Loc1.Flow.Inst.{intvl.name}.0.Computed")
    ts4._data = pd.DataFrame(
        {
            "value": values2,
            "quality": 20 * [0] + 2 * [5] + 2 * [0],
        },
        index=times,
    )
    try:
        ts1.merge(ts4)
    except TimeSeriesException as tse:
        assert str(tse).find("Times do not match interval") != -1


if __name__ == "__main__":
    # test_time_series_value()
    # test_create_time_series_by_name()
    # test_math_ops_scalar()
    # test_math_ops_ts()
    # test_selections()
    # test_aggregate_ts()
    # test_aggregate_values()
    # test_min_max()
    # test_accum_diff()
    # test_value_counts()
    # test_unit()
    # test_roundoff()
    # test_smoothing()
    # test_protected()
    # test_screenWithValueRange()
    # test_screenWithValueChangeRate()
    # test_screenWithValueRangeOrChangeRate()
    # test_screenWithDurationMagnitude()
    # test_screenWithConstantValue()
    # test_screenWithForwardMovingAverage()
    # test_estimateMissingValues()
    # test_expand_collapse_trim()
    test_merge()
