"""
Tests for PyConviva.
"""

import pytest
import requests

from pyconviva.pyconviva import ConvivaAPI

SUCCESS = {"status": "success"}


# Fixtures.
@pytest.fixture(name="api")
def authenticated_api():
    """
    The authenticated ConvivaAPI.
    """
    return ConvivaAPI(client_id="kdYTItw0W0", client_key="Ev1XoZHLAm")


# Tests.
def test_authentication(api):
    """
    Test ConvivaAPI's client ID and key authentication.
    """
    assert api._authentication == requests.auth.HTTPBasicAuth(
        "kdYTItw0W0", "Ev1XoZHLAm"
    )


def test_get_historical_data(api, requests_mock):
    """
    Tests for get_historical_data().
    """

    # Exceptions.
    with pytest.raises(ValueError):
        api.get_historical_data(
            "attempts", filter_by={"isp": "Optus", "filter_id": 2100}
        )

    with pytest.raises(ValueError):
        api.get_historical_data(list("abcdefghijklm"))  # 13 elements/'metrics'.

    with pytest.raises(ValueError):
        api.get_historical_data("attempts", time_range=95)

    with pytest.raises(ValueError):
        api.get_historical_data("attempts", sort_by=["attempts", "desc"])

    with pytest.raises(requests.exceptions.HTTPError):
        requests_mock.get(
            "https://api.conviva.com/insights/3.0/metrics/attempts?days=1",
            json=SUCCESS,
            complete_qs=True,
            status_code=400,
        )
        api.get_historical_data("attempts")

    # Verify correct URLS being called.
    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/attempts/group-by/device-name?days=1",
        json=SUCCESS,
        complete_qs=True,
    )
    assert api.get_historical_data("attempts", group_by="device-name") == SUCCESS

    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/attempts/group-by/device-name?days=1&isp=Optus",
        json=SUCCESS,
        complete_qs=True,
    )
    assert (
        api.get_historical_data(
            "attempts", group_by="device-name", filter_by={"isp": "Optus"}
        )
        == SUCCESS
    )

    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/attempts/group-by/device-name?days=5&isp=Optus",
        json=SUCCESS,
        complete_qs=True,
    )
    assert (
        api.get_historical_data(
            "attempts",
            group_by="device-name",
            filter_by={"isp": "Optus"},
            time_range=5,
        )
        == SUCCESS
    )

    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/attempts/group-by/device-name?days=5&isp=Optus&granularity=PT6H",
        json=SUCCESS,
        complete_qs=True,
    )
    assert (
        api.get_historical_data(
            "attempts",
            group_by="device-name",
            filter_by={"isp": "Optus"},
            time_range=5,
            granularity="PT6H",
        )
        == SUCCESS
    )

    # Custom tag.
    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/attempts/group-by/dimension-tag/appVersion?days=5&isp=Optus&granularity=PT6H",
        json=SUCCESS,
        complete_qs=True,
    )
    assert (
        api.get_historical_data(
            "attempts",
            group_by={"custom-tag": "appVersion"},
            filter_by={"isp": "Optus"},
            time_range=5,
            granularity="PT6H",
        )
        == SUCCESS
    )

    # Multiple metrics.
    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/custom-selection?days=1&metric=attempts&metric=bitrate",
        json=SUCCESS,
        complete_qs=True,
    )
    assert api.get_historical_data(["attempts", "bitrate"]) == SUCCESS

    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/custom-selection/group-by/device-name?days=5&isp=Optus&granularity=PT6H&metric=attempts&metric=bitrate",
        json=SUCCESS,
        complete_qs=True,
    )
    assert (
        api.get_historical_data(
            ["attempts", "bitrate"],
            group_by="device-name",
            filter_by={"isp": "Optus"},
            time_range=5,
            granularity="PT6H",
        )
        == SUCCESS
    )

    # Sorting.
    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/attempts/group-by/device-name?days=1&sort_by=attempts&order=desc",
        json=SUCCESS,
        complete_qs=True,
    )
    assert (
        api.get_historical_data(
            "attempts",
            group_by="device-name",
            sort_by=["attempts", "desc"],
        )
        == SUCCESS
    )

    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/attempts/group-by/dimension-tag/appVersion?days=1&sort_by=attempts&order=desc",
        json=SUCCESS,
        complete_qs=True,
    )
    assert (
        api.get_historical_data(
            "attempts",
            group_by={"custom-tag": "appVersion"},
            sort_by=["attempts", "desc"],
        )
        == SUCCESS
    )

    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/attempts/group-by/dimension-tag/appVersion?days=1&sort_by=attempts",
        json=SUCCESS,
        complete_qs=True,
    )
    assert (
        api.get_historical_data(
            "attempts", group_by={"custom-tag": "appVersion"}, sort_by="attempts"
        )
        == SUCCESS
    )

    # OR filtering.
    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/attempts?isp=Optus&isp=Vodafone&days=1",
        json=SUCCESS,
        complete_qs=True,
    )
    assert (
        api.get_historical_data("attempts", filter_by={"isp": ["Optus", "Vodafone"]})
        == SUCCESS
    )


def test_get_real_time_data(api, requests_mock):
    """
    Tests for get_real_time_data().
    """

    # Exceptions.
    with pytest.raises(ValueError):
        api.get_real_time_data("attempts", time_range=20)

    with pytest.raises(ValueError):
        api.get_real_time_data(list("abcdefghijklm"))  # 13 elements/'metrics'.

    with pytest.raises(ValueError):
        api.get_real_time_data("attempts", sort_by=("attempts", "desc"))

    with pytest.raises(ValueError):
        api.get_real_time_data(
            "attempts", filter_by={"isp": "Optus", "filter_id": 2100}
        )
    with pytest.raises(requests.exceptions.HTTPError):
        requests_mock.get(
            "https://api.conviva.com/insights/3.0/real-time-metrics/attempts",
            json=SUCCESS,
            complete_qs=True,
            status_code=400,
        )
        api.get_real_time_data("attempts")

    # Verify correct URLS being called.
    requests_mock.get(
        "https://api.conviva.com/insights/3.0/real-time-metrics/attempts",
        json=SUCCESS,
        complete_qs=True,
    )
    assert api.get_real_time_data("attempts") == SUCCESS

    requests_mock.get(
        "https://api.conviva.com/insights/3.0/real-time-metrics/attempts/group-by/device-name",
        json=SUCCESS,
        complete_qs=True,
    )
    assert api.get_real_time_data("attempts", group_by="device-name") == SUCCESS

    requests_mock.get(
        "https://api.conviva.com/insights/3.0/real-time-metrics/attempts/group-by/device-name?isp=Optus",
        json=SUCCESS,
        complete_qs=True,
    )
    assert (
        api.get_real_time_data(
            "attempts", group_by="device-name", filter_by={"isp": "Optus"}
        )
        == SUCCESS
    )

    requests_mock.get(
        "https://api.conviva.com/insights/3.0/real-time-metrics/attempts/group-by/device-name?isp=Optus&minutes=10",
        json=SUCCESS,
        complete_qs=True,
    )
    assert (
        api.get_real_time_data(
            "attempts",
            group_by="device-name",
            filter_by={"isp": "Optus"},
            time_range=10,
        )
        == SUCCESS
    )

    requests_mock.get(
        "https://api.conviva.com/insights/3.0/real-time-metrics/attempts/group-by/device-name?isp=Optus&minutes=10&granularity=PT10S",
        json=SUCCESS,
        complete_qs=True,
    )
    assert (
        api.get_real_time_data(
            "attempts",
            group_by="device-name",
            filter_by={"isp": "Optus"},
            time_range=10,
            granularity="PT10S",
        )
        == SUCCESS
    )

    requests_mock.get(
        "https://api.conviva.com/insights/3.0/real-time-metrics/attempts/group-by/device-name?kpi_id=2&minutes=10&granularity=PT10S",
        json=SUCCESS,
        complete_qs=True,
    )
    assert (
        api.get_real_time_data(
            "attempts",
            group_by="device-name",
            filter_by={"kpi_id": 2},
            time_range=10,
            granularity="PT10S",
        )
        == SUCCESS
    )

    # Custom tag.
    requests_mock.get(
        "https://api.conviva.com/insights/3.0/real-time-metrics/attempts/group-by/dimension-tag/appVersion?isp=Optus",
        json=SUCCESS,
        complete_qs=True,
    )
    assert (
        api.get_real_time_data(
            "attempts",
            group_by={"custom-tag": "appVersion"},
            filter_by={"isp": "Optus"},
        )
        == SUCCESS
    )

    # Multiple metrics.
    requests_mock.get(
        "https://api.conviva.com/insights/3.0/real-time-metrics/custom-selection?metric=attempts&metric=bitrate",
        json=SUCCESS,
        complete_qs=True,
    )
    assert api.get_real_time_data(["attempts", "bitrate"]) == SUCCESS

    # Sorting.

    requests_mock.get(
        "https://api.conviva.com/insights/3.0/real-time-metrics/attempts/group-by/device-name?sort_by=attempts&order=desc",
        json=SUCCESS,
        complete_qs=True,
    )
    assert api.get_real_time_data(
        "attempts",
        group_by="device-name",
        sort_by=["attempts", "desc"],
    )

    requests_mock.get(
        "https://api.conviva.com/insights/3.0/real-time-metrics/attempts/group-by/dimension-tag/appVersion?sort_by=attempts&order=desc",
        json=SUCCESS,
        complete_qs=True,
    )
    assert api.get_real_time_data(
        "attempts", group_by={"custom-tag": "appVersion"}, sort_by=["attempts", "desc"]
    )

    requests_mock.get(
        "https://api.conviva.com/insights/3.0/real-time-metrics/attempts/group-by/dimension-tag/appVersion?sort_by=attempts",
        json=SUCCESS,
        complete_qs=True,
    )
    assert api.get_real_time_data(
        "attempts", group_by={"custom-tag": "appVersion"}, sort_by="attempts"
    )

    # OR filtering.
    requests_mock.get(
        "https://api.conviva.com/insights/3.0/real-time-metrics/attempts?isp=Optus&isp=Vodafone",
        json=SUCCESS,
        complete_qs=True,
    )
    assert (
        api.get_real_time_data("attempts", filter_by={"isp": ["Optus", "Vodafone"]})
        == SUCCESS
    )


# Discovery/metadata tests.
def test_get_available_endpoints(api, requests_mock):
    """
    Tests for get_available_endpoints().
    """
    requests_mock.get("https://api.conviva.com/insights/3.0/metrics", status_code=400)
    with pytest.raises(requests.exceptions.HTTPError):
        api.get_available_endpoints()

    requests_mock.get("https://api.conviva.com/insights/3.0/metrics", json=SUCCESS)
    assert api.get_available_endpoints() == SUCCESS


def test_get_available_dimensions(api, requests_mock):
    """
    Tests for get_available_dimensions().
    """
    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/_meta/references/dimensions",
        status_code=400,
    )
    with pytest.raises(requests.exceptions.HTTPError):
        api.get_available_dimensions()

    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/_meta/references/dimensions",
        json=SUCCESS,
    )
    assert api.get_available_dimensions() == SUCCESS


def test_get_saved_filters(api, requests_mock):
    """
    Tests for get_saved_filters().
    """
    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/_meta/references/filters",
        status_code=400,
    )
    with pytest.raises(requests.exceptions.HTTPError):
        api.get_saved_filters()

    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/_meta/references/filters",
        json=SUCCESS,
    )
    assert api.get_saved_filters() == SUCCESS


def test_get_kpis(api, requests_mock):
    """
    Tests for get_kpis().
    """
    requests_mock.get("https://api.conviva.com/insights/3.0/kpis", status_code=400)
    with pytest.raises(requests.exceptions.HTTPError):
        api.get_kpis()

    requests_mock.get("https://api.conviva.com/insights/3.0/kpis", json=SUCCESS)
    assert api.get_kpis() == SUCCESS


def test_get_available_group_by_endpoints(api, requests_mock):
    """
    Tests for get_available_group_by_endpoints().
    """
    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/audience/group-by",
        status_code=400,
    )
    with pytest.raises(requests.exceptions.HTTPError):
        api.get_available_group_by_endpoints("audience")

    # Roundabout way of testing function is working with boolean parameter.
    requests_mock.get(
        "https://api.conviva.com/insights/3.0/metrics/audience/group-by/dimension-tag",
        json={"status": "success"},
    )
    data = api.get_available_group_by_endpoints("audience", True)
    assert data == {"status": "success"}
