#!/usr/bin/env python
# Copyright Salient Predictions 2024

"""Historical data timeseries.

This module is an interface to the Salient `data_timeseries` API, which returns historical
observed data.  It also includes utility functions for operating on the returned data.

Command line usage example:

```
cd ~/salientsdk
# this will get a single variable in a single file:
python -m salientsdk data_timeseries -lat 42 -lon -73 -fld all --start 2020-01-01 --end 2020-12-31 --force  -u username -p password
# this will get multiple variables in separate files:
python -m salientsdk data_timeseries -lat 42 -lon -73 -fld all -var temp,precip -u username -p password
# test with an apikey
python -m salientsdk data_timeseries -lat 42 -lon -73 -fld anom --start 2020-01-01 --end 2020-12-31 --force --apikey testkey
```

"""

from datetime import datetime

import numpy as np
import pandas as pd
import requests
import xarray as xr

from .constants import _build_urls, _expand_comma
from .location import Location
from .login_api import download_queries

HOURLY_VARIABLES = [
    "cc",
    "precip",
    "sm",
    "snow",
    "st",
    "temp",
    "tsi",
    "dhi",
    "dni",
    "wdir",
    "wdir100",
    "wgst",
    "wspd",
    "wspd100",
]


def data_timeseries(
    # API inputs -------
    loc: Location,
    variable: str | list[str] = "temp",
    field: str | list[str] = "anom",
    debias: bool = False,
    start: str = "1950-01-01",
    end: str = "-today",
    format: str = "nc",
    frequency: str = "daily",
    weights: str | None = None,
    # non-API arguments ---
    destination: str = "-default",
    force: bool = False,
    session: requests.Session | None = None,
    apikey: str | None = None,
    verify: bool | None = None,
    verbose: bool = False,
    **kwargs,
) -> str | pd.DataFrame:
    """Get a historical time series of ERA5 data.

    This function is a convenience wrapper to the Salient
    [API](https://api.salientpredictions.com/v2/documentation/api/#/Historical/get_data_timeseries).

    Args:
        loc (Location): The location to query.
            If using a `shapefile` or `location_file`, may input a vector of file names which
            will trigger multiple calls to `data_timeseries`.
        variable (str | list[str]): The variable to query, defaults to `temp`
            To request multiple variables, separate them with a comma `temp,precip`
            This will download one file per variable
            See the
            [Data Fields](https://salientpredictions.notion.site/Variables-d88463032846402e80c9c0972412fe60)
            documentation for a full list of available historical variables.
        field (str): The field to query, defaults to "anom"
        debias (bool): If True, debias the data to local observations.
            Disabled for `shapefile` locations.
            [detail](https://salientpredictions.notion.site/Debiasing-2888d5759eef4fe89a5ba3e40cd72c8f)
        start (str): The start date of the time series
        end (str): The end date of the time series
        format (str): The format of the response
        frequency (str): The frequency of the time series
        weights (str): Aggregation mechanism if using a `shapefile` or `location_file`. Currently
            supported options are 'population' for a population-weighed mean and 'equal' for an arithmetic mean.
            Defaults to None, which will not perform any weighting or aggregation.
        destination (str): The directory to download the data to
        force (bool): If False (default), don't download the data if it already exists
        session (requests.Session): The session object to use for the request.
            If `None` (default) uses `get_current_session()`.
        apikey (str | None): The API key to use for the request.
            In most cases, this is not needed if a `session` is provided.
        verify (bool): If True (default), verify the SSL certificate
        verbose (bool): If True (default False) print status messages
        **kwargs: Additional arguments to pass to the API

    Keyword Arguments:
        units (str): `SI` or `US`

    Returns:
        str | pd.DataFrame:
            the file name of the downloaded data.  File names are a hash of the query parameters.
            When `force=False` and the file already exists, the function will return the file name
            almost instantaneously without querying the API.
            If multiple variables are requested, returns a `pd.DataFrame` with columns `file_name`
            and additional columns documenting the vectorized input arguments such as `location_file`
            or `variable`
    """
    field = _expand_comma(
        field,
        valid=[
            "anom",
            "anom_d",
            "anom_ds",
            "anom_qnt",
            "anom_s",
            "clim",
            "stdv",
            "trend",
            "vals",
            "all",
        ],
        name="field",
    )
    assert format in ["nc", "csv"], f"Invalid format {format}"
    assert frequency in [
        "hourly",
        "daily",
        "weekly",
        "monthly",
        "3-monthly",
    ], f"Invalid frequency {frequency}"

    if field != "vals" and frequency == "hourly":
        raise ValueError("Only field `vals` is available for hourly frequency")

    variable = _expand_comma(
        variable, HOURLY_VARIABLES if frequency == "hourly" else None, "variable"
    )

    endpoint = "data_timeseries"
    args = loc.asdict(
        start=start,
        end=end,
        debias=debias,
        field=field,
        format=format,
        frequency=frequency,
        variable=variable,
        weights=weights,
        apikey=apikey,
        **kwargs,
    )

    queries = _build_urls(endpoint, args, destination)

    download_queries(
        query=queries["query"].values,
        file_name=queries["file_name"].values,
        force=force,
        session=session,
        verify=verify,
        verbose=verbose,
        format=format,
    )

    if len(queries) == 1:
        return queries["file_name"].values[0]
    else:
        # Now that we've executed the queries, we don't need it anymore:
        queries = queries.drop(columns="query")

        # we vectorized on something other than variable, but we still need it
        # in load_multihistory to rename the fields since we don't have short_name
        if not "variable" in queries:
            queries["variable"] = variable

        return queries


def _load_history_row(row: pd.DataFrame, fields: list[str] = ["vals"]) -> xr.Dataset:
    """Load a single history file and prepare for merging with others."""
    variable = row["variable"] if "variable" in row else "variable"

    hst = xr.load_dataset(row["file_name"])
    hst = hst[fields]
    fields_new = [variable if field == "vals" else variable + "_" + field for field in fields]
    hst = hst.rename({field: field_new for field, field_new in zip(fields, fields_new)})
    for fld in fields_new:
        hst[fld].attrs = hst.attrs
    hst.attrs = {}

    if "location_file" in row:
        # Preserve the provenance of the source location_file
        location_files = np.repeat(row["location_file"], len(hst.location))
        hst = hst.assign_coords(location_file=("location", location_files))

    hst.close()

    return hst


def load_multihistory(files: pd.DataFrame, fields: list[str] = ["vals"]) -> xr.Dataset:
    """Load multiple .nc history files and merge them into a single dataset.

    Args:
        files (pd.DataFramme): Table of the type returned by
            `data_timeseries` when multiple `variable`s, `location_file`s
            or `shapefile`s are requested
            e.g. `data_timeseries(..., variable = "temp,precip")`

        fields (list[str]): List of fields to extract from the history files.
            Useful if when calling `data_timeseries(..., field = "all")`

    Returns:
        xr.Dataset: The merged dataset, where each field and variable is renamed
            to `<variable>_<field>` or simply `variable` if field = "vals".
            This will cause the format of a multi-variable file to match the data
            variable names of `downscale`, which natively supports multi-variable queries.
    """
    hst = [_load_history_row(row, fields) for _, row in files.iterrows()]
    hst = xr.merge(hst)
    return hst


def extrapolate_trend(
    # data_timeseries inputs -------
    loc: Location,
    variable: str | list[str] = "temp",
    # climo-specific inputs -------
    start: str | datetime | pd.Timestamp = "-today",
    end: str
    | datetime
    | pd.Timestamp
    | pd.tseries.offsets.BaseOffset
    | pd.DateOffset = pd.DateOffset(years=5),
    # Other args passed to data_timeseries ----
    verbose: bool = False,
    **kwargs,
) -> str | pd.DataFrame:
    """Use Salient's 30-year linear trend to generate a per-day timeseries on for any date range.

    Args:
        loc (Location): The location to query.
            If using a `shapefile` or `location_file`, may input a vector of file names which
            will trigger multiple calls to `data_timeseries`.
        variable (str | list[str]): The variable to query, defaults to `temp`
            To request multiple variables, separate them with a comma `temp,precip`
            This will download one file per variable
            See the
            [Data Fields](https://salientpredictions.notion.site/Variables-d88463032846402e80c9c0972412fe60)
            documentation for a full list of available historical variables.
        start (str | datetime | pd.Timestamp, optional):
            The start date for the projection.
            Default is "-today", which uses the current date.
        end (str | datetime | pd.Timestamp | pd.tseries.offsets.BaseOffset | pd.DateOffset, optional):
            The end date for the projection.
            Can be a specific date or an offset from the start date.
            Supports python offset aliases such as "5YE" for "5 year end" from now.
            Default is 5 years from the start date.
        verbose (bool): If True (default False) print status messages
        **kwargs: Additional arguments passed to `data_timeseries`.

    Keyword Arguments:
        units (str): `SI` or `US`
        destination (str): The directory to download the data to
        force (bool): If False (default), don't download the data if it already exists
        session (requests.Session): The session object to use for the request.
            If `None` (default) uses `get_current_session()`.
        apikey (str | None): The API key to use for the request.
            In most cases, this is not needed if a `session` is provided.
        verify (bool): If True (default), verify the SSL certificate
    """
    field = ["clim", "trend"]
    clim_files = data_timeseries(
        loc=loc,
        variable=variable,
        field=field,
        debias=False,  # climo doesn't support debias
        start="2020-01-01",  # unused - set for caching purposes
        end="2020-01-01",  # unused  - set for caching purposes
        format="nc",
        frequency="daily",  # future enhancement - hourly
        verbose=verbose,
        **kwargs,
    )

    # Reshape the list of downloaded files so that "clim" and "trend" get their own columns
    clim_files = clim_files.pivot(
        index=["variable"]
        + [col for col in clim_files.columns if col not in ["field", "file_name", "variable"]],
        columns="field",
        values="file_name",
    ).reset_index()
    if verbose:
        print(clim_files)

    date_range = _get_date_range(start, end)

    clim_timeseries = _compute_trend(
        clim_files.clim,
        clim_files.trend,
        name=clim_files.variable,
        date_range=date_range,
    )

    return clim_timeseries


def _get_date_range(start="-today", end=pd.DateOffset(years=1)) -> pd.DatetimeIndex:
    """Turn a start and end date into a vector of dates."""
    start = (
        datetime.today() if isinstance(start, str) and start == "-today" else pd.to_datetime(start)
    )
    try:
        end = start + pd.tseries.frequencies.to_offset(end)
    except ValueError:
        end = pd.to_datetime(end)
    return pd.date_range(start.date(), end.date(), freq="D")


def _compute_trend(
    clim: xr.Dataset | str | list[str] | pd.Series,
    trend: xr.Dataset | str | list[str] | pd.Series,
    name: str | list[str] | pd.Series = "value",
    date_range: pd.DatetimeIndex = _get_date_range(),
) -> xr.Dataset:
    """Extrapolates climatology and trend over a specified date range.

    This is the "worker" function for `extrapolate_trend` once all of the necessary
    inputs have been corralled.

    Args:
        clim (xr.Dataset | str | list[str] | pd.Series):
            The climatology dataset or path to the dataset, of the type returned by
            `data_timeseries(field="clim",...).
            Can also be a list or series of datasets/paths.
        trend (xr.Dataset | str | list[str] | pd.Series):
            The trend dataset or path to the dataset, of the type returned by
            `data_timeseries(field="trend",...).
            Can also be a list or series of datasets/paths.
        name (str | list[str] | pd.Series, optional):
            The name for the output variable in the resulting dataset.
            Default is "value".
        date_range (pd.DatetimeIndex): the dates to project clim & trend onto.

    Returns:
        xr.Dataset: A dataset containing the projected climate data over the specified date range.
            Each named variable will be a separate `DataArray`.

    Raises:
        AssertionError: If `clim`, `trend`, and `name` are lists or series,
            they must all be of the same length.
    """
    vec_type = (list, pd.Series)
    if isinstance(clim, vec_type):
        assert isinstance(trend, vec_type) and isinstance(name, vec_type)
        assert len(clim) == len(trend) == len(name)
        return xr.merge(
            [_compute_trend(c, t, n, date_range) for c, t, n in zip(clim, trend, name)]
        )

    clim = xr.load_dataset(clim) if isinstance(clim, str) else clim
    trend = xr.load_dataset(trend) if isinstance(trend, str) else trend

    year = date_range.year.values[:, None]
    dayofyear = date_range.dayofyear.values

    # select corresponding days, in order, from the dataset
    clim_days = clim["clim"].sel(dayofyear=dayofyear)
    trend_days = trend["trend"].sel(dayofyear=dayofyear)

    # Find the center of the climatology from the attributes:
    clim_start = int(clim.attrs["clim_start"][0:4])  # 2019
    clim_end = int(clim.attrs["clim_end"][0:4])  # 1990
    clim_length = clim_end - clim_start + 1  # 30
    clim_center = clim_start + clim_length / 2  # 2005

    climo_with_trend = clim_days + trend_days * (year - clim_center) / clim_length
    climo_with_trend["time"] = (("dayofyear"), date_range)

    ds_future = climo_with_trend.to_dataset(name=name).swap_dims({"dayofyear": "time"})
    ds_future[name].attrs = clim.attrs
    return ds_future
