# PyConviva

PyConviva is a Python wrapper for Conviva's [Metrics V3 API](https://developer.conviva.com/docs/metrics-api-v3), which provides programmatic access to historical and real-time metrics data.

For example, to get attempts metric data for the past 5 days, grouped by ISP:

```py
import os

from pyconviva import ConvivaAPI

api = ConvivaAPI(os.environ["client_key"], os.environ["client_id"])
data = api.get_historical_data("attempts", group_by="isp", time_range=5)
```

## Getting started

### Prerequisites 

First you need to generate API client-based credentials from Conviva.

Once you have your `client_id` and `client_key` simply pass it to an instance of `ConvivaAPI`, as above.

### Installation

```
pip install pyconviva
```

## Usage

All API endpoints are available as a method of `ConvivaAPI`.

You'll most likely be using either `get_historical_data()` or `get_real_time_data()`.

Check out the official [Conviva Metrics API documentation](https://developer.conviva.com/docs/metrics-api-v3) for more detail.

### Retrieving metric data

When retrieving real-time or historical data you have to
specify the metric (or metrics) you want:

```py
attempts = api.get_historical_data("attempts")

multiple_metrics = api.get_historical_data(["attempts", "bitrate"])
```

All other parameters are optional and are documented as follows. Note that
all examples use `get_historical_data()` but are applicable to `get_real_time_data()`:

**Grouping**

Simply pass the name of the dimension you want to group by.

If you want to group by a custom tag you need to pass a dictionary,
the key of which is `"custom-tag"` and the value of which is the name of your custom tag:

```py
# Grouping by Conviva dimension.
api.get_historical_data("attempts", group_by="isp")

# Grouping by custom tag.
api.get_historical_data("attempts", group_by={"custom-tag":"appVersion"})
```

Use `api.get_available_dimensions()` to find dimensions you can group by.

**Filtering**

To filter the data, pass a dictionary with the dimension and value by which you want to filter.

To filter by the same dimension but with different values (essentially an OR statement) you can 
pass a list of values (e.g. `{"isp":["Optus", "Vodafone"]}`).

Note that you can also filter by a saved Conviva filter but if you do so you can't filter
by dimensions.

```py
# To filter to ISPs that are Optus.
api.get_historical_data("attempts", filter_by={"isp":"Optus"})

# To filter to ISPs that are Optus OR Vodafone.
api.get_historical_data("attempts", filter_by={"isp":["Optus", "Vodafone"]})

# Filtering using a saved filter.
api.get_historical_data(["attempts", "bitrate"], filter_by={"filter_id":"180"})
```

**Time range**

With `get_real_time_data()` simply specify the number of minutes ago you want to retrieve data (note that there is a maximum of 15 minutes):

```py
# Get data that is 5 minutes old or fresher.
api.get_real_time_data("attempts", time_range=5)
```

With `get_historical_data()` there are numerous ways (start/end_date, start/end_epoch) in which to specify the time range.

See the [official Metrics documentation](https://developer.conviva.com/docs/metrics-api-v3/3434cc866b1a9-options-to-select-a-time-range) for detail.

```py
# Getting Ended Plays metric data per country for the last 5 days:
api.get_historical_data("attempts", time_range=5)

# Getting attempts metric data for January 1st 2025 to January 5th 2025
api.get_historical_data("attempts", time_range={"start_date":"2025-01-01T12:00:00.000Z",
                                                "end_date":"2025-01-06T12:59:59.000Z"})
```

**Sorting**

To sort the data returned you can pass the name of the metric you want to sort by.

Default order of sorting is descending but if you want to sort in ascending order you can
also pass this as the second argument of a list.

Note that you need to group by a dimension in order to sort.

```py
# Ordering by bitrate in descending order.
api.get_historical_data(["attempts", "bitrate"], group_by="isp", sort_by="bitrate")

# Ordering by bitrate in ascending order.
api.get_historical_data(["attempts", "bitrate"], group_by="isp", sort_by=["bitrate", "asc"])
```

**Granularity**

To specify the time interval granularity by which the data will be broken down
just pass the name of the granularity. 

Ensure it's in ISO 8601 duration format.

```py
# Data broken down by week:
api.get_historical_data("attempts", granularity="P1W")
```
