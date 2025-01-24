"""
PyConviva is a Python wrapper for Conviva's Metrics Video V3 API.
"""

import requests


class ConvivaAPI:
    """The Conviva Metrics V3 API.

    Parameters
    ----------
    client_id: str
        The credential client ID issued by Conviva.
    client: str
        The credential client key issued by Conviva.

    Examples
    --------
    Initialising the API.

    >>> client_id = os.environ['CONVIVA_CLIENT_ID']
    >>> client_key = os.environ['CONVIVA_CLIENT_KEY']
    >>> api = pyconviva.ConvivaAPI(client_id, client_key)
    """

    def __init__(self, client_id: str, client_key: str) -> None:
        self._authentication = requests.auth.HTTPBasicAuth(client_id, client_key)

    # Time series data.
    def _get_metrics_data(
        self,
        metric_type: str,
        metrics: str | list,
        group_by: str | dict | None = None,
        sort_by: list | None = None,
        filter_by: dict | None = None,
        time_range: dict | None = None,
        granularity: str | None = None,
    ) -> dict:

        query_string: dict[str, str | list] = {}

        # Path parameters.
        base_url = f"https://api.conviva.com/insights/3.0/{metric_type}"

        if isinstance(
            metrics, list
        ):  # Multiple measures need to be passed in query string rather than path parameter.
            if len(metrics) > 12:
                raise ValueError("There is a maximum of 12 metrics in one request.")
            base_url += "/custom-selection"
            query_string = {"metric": metrics}
        else:
            base_url = base_url + "/" + metrics

        if group_by:
            base_url += "/group-by"
            if isinstance(group_by, dict) and (group_by := group_by.get("custom-tag")):
                base_url += "/dimension-tag"
            base_url += f"/{group_by}"

        # Query string.
        if time_range:
            query_string = query_string | time_range
        if filter_by:
            if filter_by.get("filter_id") and len(filter_by.keys()) > 1:
                raise ValueError(
                    "You can only filter using a saved filter (filter_id) or a combination of dimensional filters, but not both types."
                )
            query_string = query_string | filter_by
        if granularity:
            query_string = query_string | {"granularity": granularity}
        if sort_by:
            if len(sort_by) == 1:
                sort_by = {"sort_by": sort_by[0]}  # type: ignore
            else:
                sort_by = {"sort_by": sort_by[0], "order": sort_by[1]}  # type: ignore
            query_string = query_string | sort_by  # type: ignore

        # Call the API and return data.
        response = requests.get(
            base_url,
            params=query_string,
            auth=self._authentication,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_real_time_data(
        self,
        metrics: str | list[str],
        group_by: str | dict[str, str] | None = None,
        sort_by: list | str | None = None,
        filter_by: dict[str, str | list[str]] | None = None,
        time_range: int | None = None,
        granularity: str | None = None,
    ) -> dict:
        """Get real-time metric data.

        Parameters
        ----------
        metrics: str or list of str
            The metrics(s) you want to recieve. A single metric can be passed
            as a string or multiple metrics passed in a list.
        group_by: str or dict, optional
            The dimension you want to group the metric data by. A Conviva
            dimension is passed as a string or if you want to group by a
            custom dimension/tag pass a dictionary as: {"custom-tag": value},
            where value is the name of your custom tag.
        sort_by: str or list, optional
            The first value is the metric you want to sort by and the second
            value (optional) the direction ('desc' or 'asc').
        filter_by: dict, optional
            The dimensions you want to filter by (e.g. {"isp":"Optus"}).
            To filter by the same dimension but with different values (essentially
            an OR statement) you can pass a list of values (e.g. {"isp":["Optus", "Vodafone"]}
            ) to one key.
        time_range: int, optional
            How recent the data is/the number of minutes ago from the current
            time that the data is retrieved.

            Default is 5 minutes.
            Max is 15 minutes.

        granularity: str, optional
            The time interval granularity.
            Must be in ISO 8601 duration format.
            Default is PT1M (per 1 minute).

        Returns
        -------
        dict
            The JSON response of the API.

        Examples
        --------
        Getting Ended Plays metric per country for the last 5 minutes:

        >>> api.get_real_time_data("ended-plays", group_by="geo-country-code", time_range=15)

        Attempts grouped by a custom tag

        >>> api.get_real_time_data("attempts", group_by={"custom-tag": "appVersion"})

        Attempts and bitrate data from Optus or Vodafone ISPs where the device_name is Mac.
        Data is ordered by bitrate in descending order (default when no value specified).

        >>> api.get_real_time_data(["bitrate", "attempts"],
                                    group_by="device-name",
                                    filter_by={
                                        "device_name": "Mac",
                                        "isp": ["Optus", "Vodafone"],
                                    },
                                    sort_by="bitrate"
                                )
        """

        if time_range:
            if time_range > 15:
                raise ValueError("Start time cannot be farther than 15 minutes ago.")
            time_range = {"minutes": str(time_range)}  # type: ignore

        if sort_by:
            if not group_by:
                raise ValueError("Data can only be sorted if grouped by a dimension.")
            if isinstance(sort_by, str):
                sort_by = [sort_by]

        return self._get_metrics_data(
            "real-time-metrics",
            metrics,
            group_by,
            sort_by,  # type: ignore
            filter_by,
            time_range,  # type: ignore
            granularity,
        )

    def get_historical_data(
        self,
        metrics: str | list[str],
        group_by: str | dict[str, str] | None = None,
        sort_by: list | str | None = None,
        filter_by: dict[str, str | list[str | int]] | None = None,
        time_range: dict[str, str] | int | None = None,
        granularity: str | None = None,
    ) -> dict:
        """Get historical metric data.

        Parameters
        ----------
        metrics: str or list of str
            The metrics(s) you want to recieve. A single metric can be passed
            as a string or multiple metrics passed in a list.
        group_by: str or dict of str, optional
            The dimension you want to group the metric data by. A Conviva
            dimension is passed as a string or if you want to group by a
            custom dimension/tag pass a dictionary as: {"custom-tag": value},
            where value is the name of your custom dimension.
        sort_by: str or list, optional
            The first value is the metric you want to sort by and the second
            value (optional) the direction ('desc' or 'asc').

        filter_by: dict, optional
            The dimensions you want to filter by (e.g. {"isp":"Optus"}).
            To filter by the same dimension but with different values (essentially
            an OR statement) you can pass a list of values (e.g. {"isp":["Optus", "Vodafone"]}
            ).
        time_range: int or dict, optional
            The time range of the data you are requesting.

            You can pass the number of previous days from which you want the data
            or a dictionary if you want to specify start_date and end_date or
            start_epoch and end_epoch, etc. Note that the start date is
            inclusive and end date is exclusive.

            Default is 1 day if no argument is passed.

        granularity: str, optional
            The time interval granularity.
            Must be in ISO 8601 duration format.
            Default is PT1H (per 1 hour).

        Returns
        -------
        dict
            The JSON response of the API.

        Examples
        --------

        Getting Ended Plays metric per country for the last 5 days:

        >>> api.get_historical_data("ended-plays",
                                    group_by="geo-country-code",
                                    time_range=5
                                    )

        Getting bitrate and attempts metric data for January 1st 2025 to
        January 5th 2025, filterd by isp. Note that the end date is exclusive:

        >>> api.get_historical_data(["bitrate", "attempts"],
                                    filter_by={"isp": "Optus"},
                                    time_range={"start_date":"2025-01-01T12:00:00.000Z",
                                    "end_date":"2025-01-06T12:59:59.000Z"})

        Attempts grouped by a custom tag

        >>> api.get_historical_data("attempts", group_by={"custom-tag": "appVersion"})

        Attempts and bitrate data from Optus or Vodafone ISPs where the device_name is Mac.
        Data is ordered by attempts in ascending order.

        >>> api.get_historical_data(["bitrate", "attempts"],
                                    group_by="device-name",
                                    filter_by={
                                        "device_name": "Mac",
                                        "isp": ["Optus", "Vodafone"],
                                    },
                                    sort_by=["bitrate", "asc"],
                                )

        """

        if not time_range:
            time_range = {
                "days": "1"
            }  # A time range MUST be passed in historical API call.
        else:
            if isinstance(time_range, int):
                if time_range > 90:
                    raise ValueError(
                        "The maximum length of a query time range per API request is 90 days."
                    )
                time_range = {"days": str(time_range)}

        if sort_by:
            if not group_by:
                raise ValueError("Data can only be sorted if grouped by a dimension.")
            if isinstance(sort_by, str):
                sort_by = [sort_by]

        return self._get_metrics_data(
            "metrics",
            metrics,
            group_by,
            sort_by,  # type: ignore
            filter_by,
            time_range,
            granularity,
        )

    # Discovery/metadata endpoints.
    def get_available_endpoints(self) -> dict:
        """Retrieve available API endpoints.

        Returns
        -------
        dict
            The JSON response of the API.
        """
        response = requests.get(
            "https://api.conviva.com/insights/3.0/metrics",
            auth=self._authentication,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_available_dimensions(self) -> dict:
        """Retrieve available dimensions.

        Returns
        -------
        dict
            The JSON response of the API.
        """
        response = requests.get(
            "https://api.conviva.com/insights/3.0/metrics/_meta/references/dimensions",
            auth=self._authentication,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_saved_filters(self) -> dict:
        """Retrieve saved filters.

        Returns
        -------
        dict
            The JSON response of the API.
        """
        response = requests.get(
            "https://api.conviva.com/insights/3.0/metrics/_meta/references/filters",
            auth=self._authentication,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_kpis(self) -> dict:
        """Retrieve defined KPI ids and names for your account.

        Returns
        -------
        dict
            The JSON response of the API.
        """
        response = requests.get(
            "https://api.conviva.com/insights/3.0/kpis",
            auth=self._authentication,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_available_group_by_endpoints(
        self, metric_group_name: str, dimension_tag_only: bool = False
    ) -> dict:
        """Retrieve available group-by endpoints, by metric group.

        Parameters
        ----------
        metric_group_name: str
            Name of metric group.
        dimension_tag_only: bool, optional
            Whether to only return dimension/custom tag endpoints only.

        Returns
        -------
        dict
            The JSON response of the API.
        """
        url = (
            f"https://api.conviva.com/insights/3.0/metrics/{metric_group_name}/group-by"
        )
        if dimension_tag_only:
            url = url + "/dimension-tag"
        response = requests.get(url, auth=self._authentication, timeout=30)
        response.raise_for_status()
        return response.json()
