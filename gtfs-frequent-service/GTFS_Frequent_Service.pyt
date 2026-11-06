# -*- coding: utf-8 -*-
"""
GTFS_Frequent_Service.pyt  - ArcGIS Pro Python Toolbox  (v4)

Tool: "GTFS Frequent Service Stops"
Classifies GTFS stops as "Frequent Stops" vs "Not Frequent Stops" (default:
>= 4 boardable departures in the busiest clock-hour, all routes combined, on a
representative service day), outputs a symbolized point feature class, a
dissolved 1/2-mile access-area polygon around frequent stops and rail
centerlines, the derived rail centerlines, and a field dictionary text file.

v2: multiValue label->code lookups strip the single quotes ArcGIS adds.
v3: Dissolve is in Data Management (arcpy.management.Dissolve), not Analysis.
v4: green/grey symbology is applied programmatically at runtime via arcpy.mp
    (no freq_stops.lyrx dependency). Frequent = green, Not Frequent = grey.

Requires: ArcGIS Pro (arcpy) + pandas/numpy (ship with Pro's default env).
"""

import os
import datetime as _dt
import arcpy

try:
    import pandas as pd
    import numpy as np
except ImportError:  # pragma: no cover
    pd = None
    np = None

# =========================================================================== #
#  Analytical core (GIS-independent).                                         #
# =========================================================================== #
REQUIRED_FILES = ["stops.txt", "stop_times.txt", "trips.txt", "calendar.txt"]
OPTIONAL_FILES = ["calendar_dates.txt", "routes.txt"]


def load_gtfs(folder):
    missing = [f for f in REQUIRED_FILES
               if not os.path.isfile(os.path.join(folder, f))]
    if missing:
        raise FileNotFoundError(
            "GTFS folder is missing required file(s): " + ", ".join(missing))

    def _read(name, dtype=None, usecols=None):
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            return None
        return pd.read_csv(path, dtype=dtype, usecols=usecols,
                           low_memory=False, skipinitialspace=True)

    g = {}
    g["stops"] = _read("stops.txt", dtype={"stop_id": str, "stop_code": str,
                                           "parent_station": str})
    g["stop_times"] = _read(
        "stop_times.txt",
        dtype={"trip_id": str, "stop_id": str},
        usecols=lambda c: c in ("trip_id", "stop_id", "departure_time",
                                "arrival_time", "pickup_type"))
    g["trips"] = _read(
        "trips.txt",
        dtype={"trip_id": str, "route_id": str, "service_id": str},
        usecols=lambda c: c in ("trip_id", "route_id", "service_id",
                                "direction_id", "shape_id"))
    g["calendar"] = _read("calendar.txt", dtype={"service_id": str})
    g["calendar_dates"] = _read("calendar_dates.txt", dtype={"service_id": str})
    g["routes"] = _read(
        "routes.txt", dtype={"route_id": str},
        usecols=lambda c: c in ("route_id", "route_short_name",
                                "route_long_name", "route_type", "network_id"))
    return g


def gtfs_time_to_seconds(series):
    """'HH:MM:SS' -> seconds since service-day midnight; allows hours >= 24."""
    s = series.astype(str).str.strip()
    parts = s.str.split(":", expand=True)
    for i in range(3):
        if i not in parts.columns:
            parts[i] = np.nan
    h = pd.to_numeric(parts[0], errors="coerce")
    m = pd.to_numeric(parts[1], errors="coerce")
    sec = pd.to_numeric(parts[2], errors="coerce")
    return h * 3600 + m * 60 + sec


def hhmm_to_seconds(text):
    text = str(text).strip()
    bits = [int(x) for x in text.split(":")]
    while len(bits) < 3:
        bits.append(0)
    return bits[0] * 3600 + bits[1] * 60 + bits[2]


def active_services(calendar, calendar_dates, date):
    ymd = int(date.strftime("%Y%m%d"))
    weekday_col = ["monday", "tuesday", "wednesday", "thursday",
                   "friday", "saturday", "sunday"][date.weekday()]
    active = set()
    if calendar is not None and len(calendar):
        cal = calendar.copy()
        cal["start_date"] = pd.to_numeric(cal["start_date"], errors="coerce")
        cal["end_date"] = pd.to_numeric(cal["end_date"], errors="coerce")
        runs = ((cal[weekday_col] == 1)
                & (cal["start_date"] <= ymd)
                & (cal["end_date"] >= ymd))
        active |= set(cal.loc[runs, "service_id"].astype(str))
    if calendar_dates is not None and len(calendar_dates):
        cd = calendar_dates.copy()
        cd["date"] = pd.to_numeric(cd["date"], errors="coerce")
        today = cd[cd["date"] == ymd]
        added = set(today.loc[today["exception_type"] == 1, "service_id"].astype(str))
        removed = set(today.loc[today["exception_type"] == 2, "service_id"].astype(str))
        active |= added
        active -= removed
    return active


def pick_representative_date(calendar, calendar_dates, day_type="weekday"):
    if calendar is None or not len(calendar):
        return None
    lo = int(pd.to_numeric(calendar["start_date"], errors="coerce").min())
    hi = int(pd.to_numeric(calendar["end_date"], errors="coerce").max())
    d0 = _dt.datetime.strptime(str(lo), "%Y%m%d").date()
    d1 = _dt.datetime.strptime(str(hi), "%Y%m%d").date()
    want = {"weekday": range(0, 5), "saturday": {5}, "sunday": {6}}[day_type]
    preferred = {2} if day_type == "weekday" else want
    for pref in (preferred, want):
        d = d0
        while d <= d1:
            if d.weekday() in pref and active_services(calendar, calendar_dates, d):
                return d
            d += _dt.timedelta(days=1)
    return None


def compute_stop_frequency(gtfs, date, start="06:00", end="19:00",
                           threshold=4.0, method="peak",
                           aggregation="combined", route_types=None):
    start_sec = hhmm_to_seconds(start)
    end_sec = hhmm_to_seconds(end)
    if end_sec <= start_sec:
        raise ValueError("end time must be after start time")
    window_hours = (end_sec - start_sec) / 3600.0

    services = active_services(gtfs.get("calendar"),
                               gtfs.get("calendar_dates"), date)
    trips = gtfs["trips"]
    trips = trips[trips["service_id"].astype(str).isin(services)].copy()

    routes = gtfs.get("routes")
    if route_types is not None and routes is not None:
        rt = routes[["route_id", "route_type"]].copy()
        rt["route_type"] = pd.to_numeric(rt["route_type"], errors="coerce")
        keep_routes = set(rt.loc[rt["route_type"].isin(route_types), "route_id"])
        trips = trips[trips["route_id"].isin(keep_routes)]

    active_trip_ids = set(trips["trip_id"])
    st = gtfs["stop_times"]
    st = st[st["trip_id"].isin(active_trip_ids)].copy()

    if "pickup_type" in st.columns:
        pk = pd.to_numeric(st["pickup_type"], errors="coerce").fillna(0)
        st = st[pk != 1]

    dep = gtfs_time_to_seconds(st["departure_time"])
    if "arrival_time" in st.columns:
        arr = gtfs_time_to_seconds(st["arrival_time"])
        dep = dep.fillna(arr)
    st["dep_sec"] = dep
    st = st[(st["dep_sec"] >= start_sec) & (st["dep_sec"] < end_sec)]

    st = st.merge(trips[["trip_id", "route_id"]], on="trip_id", how="left")
    st["clock_hour"] = (st["dep_sec"] // 3600).astype(int)
    whole_hours = list(range(start_sec // 3600, end_sec // 3600))

    grp = st.groupby("stop_id")
    n_dep = grp.size().rename("n_dep_window")

    hourly = (st.groupby(["stop_id", "clock_hour"]).size()
                .rename("cnt").reset_index())
    hourly = hourly[hourly["clock_hour"].isin(whole_hours)]

    def _hourly_stat(fn):
        if not whole_hours:
            return pd.Series(dtype=float)
        idx = pd.MultiIndex.from_product(
            [hourly["stop_id"].unique() if len(hourly) else [], whole_hours],
            names=["stop_id", "clock_hour"])
        h = hourly.set_index(["stop_id", "clock_hour"]).reindex(idx, fill_value=0)
        return h.groupby("stop_id")["cnt"].agg(fn)

    min_hourly = _hourly_stat("min").rename("min_hourly_dep")
    peak_hourly = _hourly_stat("max").rename("peak_hourly_dep")
    routes_at = (grp["route_id"].apply(lambda s: sorted(set(s.dropna())))
                 .rename("route_list"))

    stop_tbl = pd.concat([n_dep, min_hourly, peak_hourly, routes_at], axis=1).reset_index()
    stop_tbl["n_dep_window"] = stop_tbl["n_dep_window"].fillna(0).astype(int)
    stop_tbl["min_hourly_dep"] = stop_tbl["min_hourly_dep"].fillna(0).astype(int)
    stop_tbl["peak_hourly_dep"] = stop_tbl["peak_hourly_dep"].fillna(0).astype(int)
    stop_tbl["window_hours"] = window_hours
    stop_tbl["avg_dep_hr"] = stop_tbl["n_dep_window"] / window_hours
    stop_tbl["n_routes"] = stop_tbl["route_list"].apply(len)
    stop_tbl["routes"] = stop_tbl["route_list"].apply(lambda x: ",".join(map(str, x)))

    rr = (st.groupby(["stop_id", "route_id"]).size().rename("n").reset_index())
    rr["avg_hr"] = rr["n"] / window_hours
    if method in ("min_hourly", "peak"):
        rh = (st.groupby(["stop_id", "route_id", "clock_hour"]).size()
                .rename("cnt").reset_index())
        rh = rh[rh["clock_hour"].isin(whole_hours)]
        keys = rr[["stop_id", "route_id"]].drop_duplicates()
        if len(keys) and whole_hours:
            grid = keys.assign(key=1).merge(
                pd.DataFrame({"clock_hour": whole_hours, "key": 1}), on="key"
            ).drop(columns="key")
            rh = grid.merge(rh, on=["stop_id", "route_id", "clock_hour"], how="left")
            rh["cnt"] = rh["cnt"].fillna(0)
            agg = "min" if method == "min_hourly" else "max"
            rstat = (rh.groupby(["stop_id", "route_id"])["cnt"].agg(agg)
                       .rename("route_metric").reset_index())
        else:
            rstat = rr.assign(route_metric=0.0)[["stop_id", "route_id", "route_metric"]]
        rr = rr.merge(rstat, on=["stop_id", "route_id"], how="left")
    else:
        rr["route_metric"] = rr["avg_hr"]

    best = (rr.sort_values("route_metric", ascending=False)
              .groupby("stop_id").first().reset_index()
              [["stop_id", "route_id", "route_metric"]])
    best = best.rename(columns={"route_id": "best_route",
                                "route_metric": "best_route_dep_hr"})
    stop_tbl = stop_tbl.merge(best, on="stop_id", how="left")

    if aggregation == "combined":
        if method == "average":
            metric = stop_tbl["avg_dep_hr"]
        elif method == "min_hourly":
            metric = stop_tbl["min_hourly_dep"].astype(float)
        elif method == "peak":
            metric = stop_tbl["peak_hourly_dep"].astype(float)
        else:
            raise ValueError("method must be average|min_hourly|peak")
    elif aggregation == "route":
        metric = stop_tbl["best_route_dep_hr"].astype(float)
    else:
        raise ValueError("aggregation must be combined|route")

    stop_tbl["metric_value"] = metric.fillna(0.0)
    stop_tbl["is_frequent"] = stop_tbl["metric_value"] >= threshold
    stop_tbl["freq_class"] = np.where(stop_tbl["is_frequent"],
                                      "Frequent Stops", "Not Frequent Stops")

    stops = gtfs["stops"].copy()
    stops["stop_lat"] = pd.to_numeric(stops["stop_lat"], errors="coerce")
    stops["stop_lon"] = pd.to_numeric(stops["stop_lon"], errors="coerce")
    keep_cols = [c for c in ["stop_id", "stop_code", "stop_name",
                             "stop_lat", "stop_lon"] if c in stops.columns]
    out = stops[keep_cols].merge(stop_tbl.drop(columns=["route_list"]),
                                 on="stop_id", how="left")

    for c in ["n_dep_window", "min_hourly_dep", "peak_hourly_dep", "n_routes",
              "avg_dep_hr", "metric_value", "best_route_dep_hr"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0)
    out["window_hours"] = window_hours
    out["routes"] = out["routes"].fillna("")
    out["best_route"] = out["best_route"].fillna("")
    out["is_frequent"] = out["is_frequent"].fillna(False)
    out["freq_class"] = out["freq_class"].fillna("Not Frequent Stops")
    out["analysis_date"] = date.strftime("%Y-%m-%d")
    out["method"] = method
    out["aggregation"] = aggregation
    out["threshold"] = threshold
    return out


# =========================================================================== #
#  Toolbox helpers / lookups                                                  #
# =========================================================================== #
METHOD_MAP = {
    "Peak hour (loosest)": "peak",
    "Average over window": "average",
    "Minimum hourly (strictest)": "min_hourly",
}
AGG_MAP = {
    "All routes combined (stop-level)": "combined",
    "Any single route (line-level)": "route",
}
ROUTE_TYPE_MAP = {
    "Tram / Streetcar / Light Rail (0)": 0, "Subway / Metro (1)": 1,
    "Rail / Commuter Rail (2)": 2, "Bus (3)": 3, "Ferry (4)": 4,
    "Cable Tram (5)": 5, "Aerial Lift / Gondola (6)": 6, "Funicular (7)": 7,
}
RAIL_TYPE_MAP = {
    "Tram / Streetcar / Light Rail (0)": 0,
    "Subway / Metro (1)": 1,
    "Commuter Rail (2)": 2,
}

# freq_class value -> (RGB with alpha, marker size)
FREQ_SYMBOLOGY = {
    "Frequent Stops": ([0, 168, 0, 100], 7),
    "Not Frequent Stops": ([150, 150, 150, 100], 6),
}


def _selected_codes(param, mapping):
    # Map a multiValue GPString parameter's selected labels to numeric codes.
    # ArcGIS wraps values containing spaces/special chars in single quotes when
    # serialized, so strip surrounding quotes before the dict lookup. quote_chars
    # is built with chr() to avoid quote literals (robust to smart-quote paste).
    if not param.values:
        return None
    quote_chars = chr(39) + chr(34)  # single quote + double quote
    codes = set()
    for v in param.values:
        key = str(v).strip().strip(quote_chars).strip()
        if key in mapping:
            codes.add(mapping[key])
    return codes or None


def _symbolize_freq(lyr):
    """Set a green/grey unique-value renderer on freq_class for a point layer."""
    sym = lyr.symbology
    if not hasattr(sym, "renderer"):
        return
    sym.updateRenderer("UniqueValueRenderer")
    sym.renderer.fields = ["freq_class"]
    lyr.symbology = sym
    sym = lyr.symbology
    for grp in sym.renderer.groups:
        for itm in grp.items:
            try:
                val = itm.values[0][0]
            except Exception:
                val = itm.label
            if val in FREQ_SYMBOLOGY:
                rgb, size = FREQ_SYMBOLOGY[val]
                itm.symbol.color = {"RGB": rgb}
                itm.symbol.size = size
                itm.label = val
    lyr.symbology = sym


def _finalize_map(out_fc, extra_paths):
    """Add outputs to the active map; symbolize the stops. Returns True if added."""
    try:
        aprx = arcpy.mp.ArcGISProject("CURRENT")
    except Exception:
        return False
    m = aprx.activeMap
    if m is None:
        maps = aprx.listMaps()
        m = maps[0] if maps else None
    if m is None:
        return False
    all_paths = [out_fc] + [p for p in extra_paths if p]
    norm = {os.path.normpath(p).lower() for p in all_paths}
    for lyr in list(m.listLayers()):
        try:
            if lyr.isFeatureLayer and os.path.normpath(lyr.dataSource).lower() in norm:
                m.removeLayer(lyr)
        except Exception:
            pass
    stops_lyr = m.addDataFromPath(out_fc)
    try:
        _symbolize_freq(stops_lyr)
    except Exception as e:
        arcpy.AddWarning("Auto-symbology skipped: %s" % e)
    for p in extra_paths:
        if p and arcpy.Exists(p):
            try:
                m.addDataFromPath(p)
            except Exception:
                pass
    return True


# (name, type, length, source_key, alias)
FIELD_SCHEMA = [
    ("stop_id", "TEXT", 50, "stop_id", "Stop ID"),
    ("stop_code", "TEXT", 50, "stop_code", "Stop Code"),
    ("stop_name", "TEXT", 150, "stop_name", "Stop Name"),
    ("dep_in_window", "LONG", None, "n_dep_window", "Departures in Window"),
    ("window_hours", "DOUBLE", None, "window_hours", "Window Length (hrs)"),
    ("avg_dep_per_hr", "DOUBLE", None, "avg_dep_hr", "Avg Departures per Hour"),
    ("min_hourly_dep", "LONG", None, "min_hourly_dep", "Min Departures in an Hour"),
    ("peak_hourly_dep", "LONG", None, "peak_hourly_dep", "Peak Departures in an Hour"),
    ("n_routes", "LONG", None, "n_routes", "Number of Routes"),
    ("routes", "TEXT", 255, "routes", "Routes Serving Stop"),
    ("best_route", "TEXT", 50, "best_route", "Best Single Route"),
    ("best_route_per_hr", "DOUBLE", None, "best_route_dep_hr", "Best Route Dep per Hour"),
    ("freq_value", "DOUBLE", None, "metric_value", "Classifying Frequency Value"),
    ("freq_class", "TEXT", 20, "freq_class", "Frequency Class"),
    ("is_frequent", "SHORT", None, "is_frequent", "Is Frequent (1=yes)"),
    ("analysis_date", "TEXT", 12, "analysis_date", "Analysis Date"),
    ("method", "TEXT", 20, "method", "Frequency Method"),
    ("aggregation", "TEXT", 20, "aggregation", "Route Aggregation"),
    ("threshold", "DOUBLE", None, "threshold", "Threshold (dep/hr)"),
]

FIELD_DESCS = {
    "stop_id": "GTFS stop identifier (stops.txt).",
    "stop_code": "Public-facing stop code, if published.",
    "stop_name": "Stop name.",
    "dep_in_window": "Boardable departures at this stop within the analysis window on the analysis date.",
    "window_hours": "Length of the analysis window in hours.",
    "avg_dep_per_hr": "dep_in_window / window_hours.",
    "min_hourly_dep": "Fewest departures in any whole clock-hour of the window.",
    "peak_hourly_dep": "Most departures in any whole clock-hour (value the Peak baseline classifies on).",
    "n_routes": "Distinct routes serving the stop in the window.",
    "routes": "Comma-separated route_ids serving the stop.",
    "best_route": "Single route with the highest frequency at the stop.",
    "best_route_per_hr": "That best route's departures/hour (used only for line-level aggregation).",
    "freq_value": "The metric compared against the threshold (depends on method + aggregation).",
    "freq_class": "'Frequent Stops' if freq_value >= threshold, else 'Not Frequent Stops'.",
    "is_frequent": "1 if Frequent, 0 if not.",
    "analysis_date": "Service date analyzed (YYYY-MM-DD).",
    "method": "peak | average | min_hourly.",
    "aggregation": "combined (all routes) | route (any single route).",
    "threshold": "Departures/hour cutoff (default 4 = 15-min headway).",
}


def write_field_dictionary(out_fc, summary):
    out_dir = os.path.dirname(out_fc)
    if out_dir.lower().endswith(".gdb"):
        out_dir = os.path.dirname(out_dir)
    base = os.path.splitext(os.path.basename(out_fc))[0]
    path = os.path.join(out_dir, base + "_field_dictionary.txt")
    lines = ["GTFS Frequent Service Stops - Field Dictionary",
             "=" * 46, "", summary, ""]
    for name, ftype, _len, _src, alias in FIELD_SCHEMA:
        lines += ["%s  [%s]  (%s)" % (name, alias, ftype),
                  "    " + FIELD_DESCS.get(name, ""), ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def _sibling(fc, suffix):
    d = os.path.dirname(fc)
    return os.path.join(d, arcpy.ValidateTableName(
        os.path.basename(fc) + suffix, d))


def build_rail_centerlines(folder, gtfs, rail_types, ws):
    """One polyline per rail shape_id from shapes.txt. None if not derivable."""
    shp_path = os.path.join(folder, "shapes.txt")
    trips, routes = gtfs["trips"], gtfs.get("routes")
    if (not os.path.isfile(shp_path) or routes is None
            or "shape_id" not in trips.columns):
        return None
    rt = routes[["route_id", "route_type"]].copy()
    rt["route_type"] = pd.to_numeric(rt["route_type"], errors="coerce")
    rail_routes = set(rt.loc[rt["route_type"].isin(rail_types), "route_id"])
    rail_shapes = set(trips.loc[trips["route_id"].isin(rail_routes),
                                "shape_id"].dropna().astype(str))
    if not rail_shapes:
        return None
    shp = pd.read_csv(shp_path, dtype={"shape_id": str})
    shp = shp[shp["shape_id"].isin(rail_shapes)].sort_values(
        ["shape_id", "shape_pt_sequence"])
    fc = os.path.join(ws, "rail_lines")
    if arcpy.Exists(fc):
        arcpy.management.Delete(fc)
    sr = arcpy.SpatialReference(4326)
    arcpy.management.CreateFeatureclass(ws, "rail_lines", "POLYLINE",
                                        spatial_reference=sr)
    arcpy.management.AddField(fc, "shape_id", "TEXT", field_length=80)
    with arcpy.da.InsertCursor(fc, ["SHAPE@", "shape_id"]) as cur:
        for sid, grp in shp.groupby("shape_id"):
            arr = arcpy.Array([arcpy.Point(float(r.shape_pt_lon),
                                           float(r.shape_pt_lat))
                               for r in grp.itertuples()])
            if arr.count >= 2:
                cur.insertRow([arcpy.Polyline(arr, sr), str(sid)])
    return fc


# =========================================================================== #
#  Toolbox / Tool                                                             #
# =========================================================================== #
class Toolbox(object):
    def __init__(self):
        self.label = "GTFS Transit Frequency"
        self.alias = "gtfsfreq"
        self.tools = [FrequentServiceStops]


class FrequentServiceStops(object):
    def __init__(self):
        self.label = "GTFS Frequent Service Stops"
        self.description = ("Classify GTFS stops as Frequent vs Not Frequent, "
                            "symbolize them green/grey, and build a dissolved "
                            "access-area polygon around frequent stops and rail "
                            "centerlines.")
        self.canRunInBackground = False

    _P = dict(FOLDER=0, OUT=1, DATE=2, DAY=3, START=4, END=5, THR=6,
              METHOD=7, AGG=8, MODES=9, LOC=10, SVC=11, ONLY=12,
              BUFDIST=13, OUTBUF=14, INCRAIL=15, RAILM=16, OUTRAIL=17)

    def getParameterInfo(self):
        p = []

        gtfs = arcpy.Parameter("gtfs_folder", "GTFS folder (unzipped)",
                               "Input", "DEFolder", "Required")
        p.append(gtfs)

        out = arcpy.Parameter("out_fc", "Output stops feature class",
                              "Output", "DEFeatureClass", "Required")
        p.append(out)

        date = arcpy.Parameter("analysis_date",
                               "Analysis date (blank = auto-pick)",
                               "Input", "GPDate", "Optional")
        p.append(date)

        day = arcpy.Parameter("day_type",
                              "Auto-pick day type (used only if date blank)",
                              "Input", "GPString", "Optional")
        day.filter.type = "ValueList"
        day.filter.list = ["weekday", "saturday", "sunday"]
        day.value = "weekday"
        p.append(day)

        start = arcpy.Parameter("start_time", "Window start (HH:MM)",
                                "Input", "GPString", "Required")
        start.value = "06:00"
        p.append(start)

        end = arcpy.Parameter("end_time", "Window end (HH:MM)",
                              "Input", "GPString", "Required")
        end.value = "19:00"
        p.append(end)

        thr = arcpy.Parameter("threshold",
                              "Frequent threshold (departures/hour)",
                              "Input", "GPDouble", "Required")
        thr.value = 4.0
        p.append(thr)

        method = arcpy.Parameter("method", "Frequency method",
                                 "Input", "GPString", "Required")
        method.filter.type = "ValueList"
        method.filter.list = list(METHOD_MAP.keys())
        method.value = "Peak hour (loosest)"
        p.append(method)

        agg = arcpy.Parameter("aggregation", "Route aggregation",
                              "Input", "GPString", "Required")
        agg.filter.type = "ValueList"
        agg.filter.list = list(AGG_MAP.keys())
        agg.value = "All routes combined (stop-level)"
        p.append(agg)

        modes = arcpy.Parameter("route_types", "Modes to include (blank = all)",
                                "Input", "GPString", "Optional", multiValue=True)
        modes.filter.type = "ValueList"
        modes.filter.list = list(ROUTE_TYPE_MAP.keys())
        p.append(modes)

        loc = arcpy.Parameter("locality_boundary",
                              "Locality boundary to clip (optional)",
                              "Input", "GPFeatureLayer", "Optional")
        loc.filter.list = ["Polygon"]
        p.append(loc)

        svc = arcpy.Parameter("service_boundary",
                              "Service area / UGB boundary to clip (optional)",
                              "Input", "GPFeatureLayer", "Optional")
        svc.filter.list = ["Polygon"]
        p.append(svc)

        only = arcpy.Parameter("frequent_only", "Output frequent stops only",
                               "Input", "GPBoolean", "Optional")
        only.value = False
        p.append(only)

        buf = arcpy.Parameter("buffer_distance",
                              "Access buffer distance (blank = no buffer)",
                              "Input", "GPLinearUnit", "Optional")
        buf.value = "0.5 Miles"
        p.append(buf)

        outbuf = arcpy.Parameter("out_buffer_fc",
                                 "Output access-area polygon (dissolved)",
                                 "Output", "DEFeatureClass", "Optional")
        p.append(outbuf)

        incrail = arcpy.Parameter("include_rail",
                                  "Include rail centerline buffers",
                                  "Input", "GPBoolean", "Optional")
        incrail.value = True
        p.append(incrail)

        rail = arcpy.Parameter("rail_modes", "Rail types for centerline buffer",
                               "Input", "GPString", "Optional", multiValue=True)
        rail.filter.type = "ValueList"
        rail.filter.list = list(RAIL_TYPE_MAP.keys())
        rail.value = rail.filter.list  # default = all rail
        p.append(rail)

        outrail = arcpy.Parameter("out_rail_fc", "Output rail centerlines",
                                  "Output", "DEFeatureClass", "Optional")
        p.append(outrail)

        return p

    def isLicensed(self):
        return True

    @staticmethod
    def _valid_hhmm(text):
        try:
            bits = [int(x) for x in str(text).strip().split(":")]
        except (ValueError, AttributeError):
            return None
        if not (1 <= len(bits) <= 3):
            return None
        while len(bits) < 3:
            bits.append(0)
        h, m, s = bits
        if m > 59 or s > 59 or h < 0 or m < 0 or s < 0:
            return None
        return h * 3600 + m * 60 + s

    def updateParameters(self, params):
        P = self._P
        params[P["DAY"]].enabled = params[P["DATE"]].value is None
        if not params[P["START"]].value:
            params[P["START"]].value = "06:00"
        if not params[P["END"]].value:
            params[P["END"]].value = "19:00"
        if (params[P["THR"]].value is not None and params[P["THR"]].value <= 0
                and not params[P["THR"]].hasBeenValidated):
            params[P["THR"]].value = 4.0
        has_buf = bool(params[P["BUFDIST"]].value)
        params[P["OUTBUF"]].enabled = has_buf
        params[P["INCRAIL"]].enabled = has_buf
        rail_on = has_buf and bool(params[P["INCRAIL"]].value)
        params[P["RAILM"]].enabled = rail_on
        params[P["OUTRAIL"]].enabled = rail_on
        return

    def updateMessages(self, params):
        P = self._P
        if pd is None:
            params[P["FOLDER"]].setErrorMessage(
                "pandas/numpy not found. Run from ArcGIS Pro's default "
                "'arcgispro-py3' Python environment.")
        folder = params[P["FOLDER"]].valueAsText
        have_routes = True
        if folder and os.path.isdir(folder):
            missing = [f for f in REQUIRED_FILES
                       if not os.path.isfile(os.path.join(folder, f))]
            if missing:
                params[P["FOLDER"]].setErrorMessage(
                    "GTFS folder is missing required file(s): %s. Point to the "
                    "unzipped feed folder." % ", ".join(missing))
            have_routes = os.path.isfile(os.path.join(folder, "routes.txt"))
        elif folder:
            params[P["FOLDER"]].setErrorMessage("Folder does not exist.")

        s_sec = self._valid_hhmm(params[P["START"]].value) if params[P["START"]].value else None
        e_sec = self._valid_hhmm(params[P["END"]].value) if params[P["END"]].value else None
        if params[P["START"]].value and s_sec is None:
            params[P["START"]].setErrorMessage("Use HH:MM (24-hour), e.g. 06:00.")
        if params[P["END"]].value and e_sec is None:
            params[P["END"]].setErrorMessage(
                "Use HH:MM (24-hour); past-midnight allowed (e.g. 25:00 = 1 AM).")
        if s_sec is not None and e_sec is not None and e_sec <= s_sec:
            params[P["END"]].setErrorMessage("Window end must be after start.")

        thr = params[P["THR"]].value
        if thr is not None and thr <= 0:
            params[P["THR"]].setErrorMessage("Threshold must be greater than 0.")

        if params[P["MODES"]].values and not have_routes:
            params[P["MODES"]].setWarningMessage(
                "routes.txt not found; mode filter can't apply, all modes used.")
        return

    def execute(self, params, messages):
        # We add + symbolize outputs ourselves, so suppress the default auto-add.
        arcpy.env.addOutputsToMap = False

        vals = {p.name: p for p in params}
        folder = vals["gtfs_folder"].valueAsText
        out_fc = vals["out_fc"].valueAsText
        start = vals["start_time"].valueAsText or "06:00"
        end = vals["end_time"].valueAsText or "19:00"
        threshold = float(vals["threshold"].value)
        method = METHOD_MAP[vals["method"].valueAsText]
        aggregation = AGG_MAP[vals["aggregation"].valueAsText]
        frequent_only = bool(vals["frequent_only"].value)

        route_types = _selected_codes(vals["route_types"], ROUTE_TYPE_MAP)

        arcpy.AddMessage("Loading GTFS files...")
        gtfs = load_gtfs(folder)

        if vals["analysis_date"].value:
            d = vals["analysis_date"].value
            date = _dt.date(d.year, d.month, d.day)
        else:
            day_type = vals["day_type"].valueAsText or "weekday"
            date = pick_representative_date(gtfs["calendar"],
                                            gtfs.get("calendar_dates"), day_type)
            if date is None:
                raise arcpy.ExecuteError("Could not auto-pick a service date.")
            arcpy.AddMessage("Auto-picked analysis date: %s (%s)"
                             % (date.isoformat(), date.strftime("%A")))

        services = active_services(gtfs["calendar"],
                                   gtfs.get("calendar_dates"), date)
        arcpy.AddMessage("Active services on %s: %d"
                         % (date.isoformat(), len(services)))

        arcpy.AddMessage("Computing stop frequencies (%s / %s, %s-%s, >= %g dep/hr)..."
                         % (method, aggregation, start, end, threshold))
        df = compute_stop_frequency(gtfs, date, start, end, threshold,
                                    method, aggregation, route_types)
        df = df.dropna(subset=["stop_lat", "stop_lon"])
        if frequent_only:
            df = df[df["is_frequent"]]
        n_freq = int(df["is_frequent"].sum())
        arcpy.AddMessage("Stops: %d total, %d Frequent, %d Not Frequent"
                         % (len(df), n_freq, len(df) - n_freq))

        scratch = arcpy.env.scratchGDB
        tmp_fc = os.path.join(scratch, "gtfs_freq_tmp")
        if arcpy.Exists(tmp_fc):
            arcpy.management.Delete(tmp_fc)
        sr = arcpy.SpatialReference(4326)
        arcpy.management.CreateFeatureclass(scratch, "gtfs_freq_tmp", "POINT",
                                            spatial_reference=sr)

        for name, ftype, length, _src, alias in FIELD_SCHEMA:
            if length:
                arcpy.management.AddField(tmp_fc, name, ftype,
                                          field_length=length, field_alias=alias)
            else:
                arcpy.management.AddField(tmp_fc, name, ftype, field_alias=alias)

        insert_fields = ["SHAPE@XY"] + [f[0] for f in FIELD_SCHEMA]
        src_keys = [f[3] for f in FIELD_SCHEMA]
        with arcpy.da.InsertCursor(tmp_fc, insert_fields) as cur:
            for _, r in df.iterrows():
                row = [(float(r["stop_lon"]), float(r["stop_lat"]))]
                for key in src_keys:
                    v = r.get(key)
                    if key == "is_frequent":
                        v = 1 if bool(v) else 0
                    elif isinstance(v, float) and np.isnan(v):
                        v = None
                    row.append(v)
                cur.insertRow(row)

        current = tmp_fc
        clip_layers = []
        if vals["locality_boundary"].value:
            clip_layers.append(vals["locality_boundary"].valueAsText)
        if vals["service_boundary"].value:
            clip_layers.append(vals["service_boundary"].valueAsText)

        step = 0
        for clip_src in clip_layers:
            step += 1
            nxt = os.path.join(scratch, "gtfs_freq_clip%d" % step)
            if arcpy.Exists(nxt):
                arcpy.management.Delete(nxt)
            arcpy.AddMessage("Clipping stops to boundary: %s" % clip_src)
            try:
                arcpy.analysis.PairwiseClip(current, clip_src, nxt)
            except Exception:
                arcpy.analysis.Clip(current, clip_src, nxt)
            current = nxt

        arcpy.management.CopyFeatures(current, out_fc)
        arcpy.AddMessage("Wrote %s stops to %s"
                         % (arcpy.management.GetCount(out_fc)[0], out_fc))

        # ---- field dictionary ----
        try:
            summary = ("Analysis %s (%s) | method=%s aggregation=%s | "
                       "window %s-%s | threshold >= %g dep/hr"
                       % (date.isoformat(), date.strftime("%A"), method,
                          aggregation, start, end, threshold))
            dp = write_field_dictionary(out_fc, summary)
            arcpy.AddMessage("Field dictionary: %s" % dp)
        except Exception as e:
            arcpy.AddWarning("Field dictionary skipped: %s" % e)

        # ---- buffers / access-area polygon ----
        out_buffer_path = None
        out_rail_path = vals["out_rail_fc"].valueAsText or None
        buffer_dist = vals["buffer_distance"].valueAsText
        if buffer_dist:
            ws = arcpy.env.scratchGDB
            freq_lyr = "freq_only_lyr"
            if arcpy.Exists(freq_lyr):
                arcpy.management.Delete(freq_lyr)
            arcpy.management.MakeFeatureLayer(out_fc, freq_lyr, "is_frequent = 1")
            stop_buf = os.path.join(ws, "stop_buf")
            if arcpy.Exists(stop_buf):
                arcpy.management.Delete(stop_buf)
            arcpy.AddMessage("Buffering frequent stops by %s (geodesic)..." % buffer_dist)
            arcpy.analysis.Buffer(freq_lyr, stop_buf, buffer_dist,
                                  dissolve_option="NONE", method="GEODESIC")
            to_merge = [stop_buf]

            if bool(vals["include_rail"].value):
                rail_types = _selected_codes(vals["rail_modes"], RAIL_TYPE_MAP) or {0, 1, 2}
                arcpy.AddMessage("Deriving rail centerlines (types %s)..."
                                 % sorted(rail_types))
                rail_lines = build_rail_centerlines(folder, gtfs, rail_types, ws)
                if rail_lines:
                    for clip_src in clip_layers:
                        nxt = arcpy.CreateUniqueName("rail_clip", ws)
                        try:
                            arcpy.analysis.PairwiseClip(rail_lines, clip_src, nxt)
                        except Exception:
                            arcpy.analysis.Clip(rail_lines, clip_src, nxt)
                        rail_lines = nxt
                    if out_rail_path:
                        arcpy.management.CopyFeatures(rail_lines, out_rail_path)
                        arcpy.AddMessage("Rail centerlines: %s" % out_rail_path)
                    rail_buf = os.path.join(ws, "rail_buf")
                    if arcpy.Exists(rail_buf):
                        arcpy.management.Delete(rail_buf)
                    arcpy.analysis.Buffer(rail_lines, rail_buf, buffer_dist,
                                          dissolve_option="NONE", method="GEODESIC")
                    to_merge.append(rail_buf)
                else:
                    arcpy.AddWarning("No shapes.txt / rail shapes found; "
                                     "rail buffer skipped.")

            out_buffer_path = (vals["out_buffer_fc"].valueAsText
                               or _sibling(out_fc, "_freq_access"))
            if len(to_merge) > 1:
                merged = os.path.join(ws, "acc_merge")
                if arcpy.Exists(merged):
                    arcpy.management.Delete(merged)
                arcpy.management.Merge(to_merge, merged)
            else:
                merged = to_merge[0]
            arcpy.management.Dissolve(merged, out_buffer_path)  # dissolve ALL
            arcpy.AddMessage("Access-area polygon (dissolved): %s" % out_buffer_path)

        # ---- cleanup scratch ----
        for tmp in [tmp_fc] + [os.path.join(scratch, "gtfs_freq_clip%d" % i)
                               for i in range(1, step)]:
            if arcpy.Exists(tmp) and tmp != out_fc:
                try:
                    arcpy.management.Delete(tmp)
                except Exception:
                    pass

        # ---- add to map + symbolize (green/grey). If no project, let the
        #      framework add the outputs plainly instead. ----
        added = _finalize_map(out_fc, [out_buffer_path, out_rail_path])
        if not added:
            arcpy.env.addOutputsToMap = True
        return
