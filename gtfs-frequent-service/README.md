# GTFS frequent-transit toolbox (ArcGIS Pro)

An ArcGIS Pro Python toolbox (`GTFS_Frequent_Service.pyt`) that reads a GTFS transit feed, such
as TriMet's, and:

- classifies each stop as **Frequent** or **Not Frequent**. By default a stop is Frequent if it has
  at least 4 boardable departures in its busiest clock-hour on a representative service day,
  counting all routes together;
- writes a stop point layer, symbolized green for Frequent and grey for Not Frequent;
- builds a **dissolved half-mile access-area polygon** around frequent stops and rail centerlines,
  using geodesic buffers;
- derives rail centerlines from `shapes.txt`, covering light rail, streetcar and commuter rail by
  default;
- writes a field dictionary next to the output.

## Options

- **Method:** peak hour (the default), average over the analysis window, or minimum hourly (a stop
  must be frequent all day).
- **Aggregation:** all routes at the stop combined (the default), or any single route on its own.
- **Threshold, analysis window and date.** If the date is left blank, a representative weekday,
  Saturday or Sunday is picked automatically.
- **Optional boundary clips** for city limits or an urban growth boundary. Rail lines are clipped
  before buffering, so segments outside the boundary don't inflate the access area.

## Data handling

- Only boardable departures count. Drop-off-only stops (`pickup_type = 1`) are excluded.
- Times after midnight (`24:00:00`+) are parsed correctly.
- `calendar_dates` holiday exceptions are honored.

## Validation

The analytical core (calendar resolution, after-midnight times, pickup filtering, the three
methods and the two aggregations) was tested against a synthetic feed with known answers. It was
also tested against the real TriMet calendar, including Labor Day service swaps.

## Install

In ArcGIS Pro, open the Catalog pane, right-click a folder, choose **Add Toolbox**, and pick the
`.pyt`. It needs `arcpy`, pandas and numpy, which all ship with Pro's default environment.

Version history: v2 fixed the multi-value parameter lookups, v3 fixed the Dissolve call, and v4
applies symbology in code, so no `.lyrx` file is needed.
