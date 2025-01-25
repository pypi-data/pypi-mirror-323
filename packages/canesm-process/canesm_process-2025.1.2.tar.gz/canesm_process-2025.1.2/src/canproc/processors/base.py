import xarray as xr
import numpy as np
import logging
from canproc.processors.xarray_ops import to_array, to_dataset


def open_mfdataset(*args, **kwargs):

    return xr.open_mfdataset(*args, **kwargs)
    # return xr.open_dataset(*args)


def to_netcdf(
    data: xr.Dataset | xr.DataArray, filename: str, **kwargs
) -> xr.Dataset | xr.DataArray:
    """Implement xr.to_netcdf with CMIP-compliant options."""

    if "encoding" in kwargs:
        kwargs["encoding"] = {var: kwargs["encoding"] for var in data.data_vars}

    return data.to_netcdf(filename, **kwargs)


def select_region(
    data: xr.Dataset | xr.DataArray,
    region: dict[str, tuple[float, float]] = {"lat": (-90, 90), "lon": (-180, 180)},
) -> xr.Dataset | xr.DataArray:
    """
    Select a geopraphic region. Expects longitude cooridinates (-180 to 180).
    If longitude[1] > longitude[0] selection is wrapped from east to west.

    Parameters
    ----------
    data : xr.Dataset | xr.DataArray
        input data
    region : dict[str, tuple[float, float]], optional
        region to use for selection, by default {"lat": (-90, 90), "lon": (-180, 180)}

    Returns
    -------
    xr.Dataset | xr.DataArray
        subset of input data
    """

    latdim, londim = list(region.keys())

    min_longitude = region[londim][0]
    max_longitude = region[londim][1]
    min_latitude = region[latdim][0]
    max_latitude = region[latdim][1]

    if data[londim].max() > 180:
        if max_longitude < 0:
            max_longitude += 360
        if min_longitude < 0:
            min_longitude += 360
        # raise ValueError(f"only (-180 to 180) longitude values are supported {data[londim].max()}")

    if region:
        if min_longitude > max_longitude:
            d1 = data.sel({londim: slice(min_longitude, 360)})
            d2 = data.sel({londim: slice(-180, max_longitude)})
            data = xr.concat([d2, d1], dim=londim)
        else:
            data = data.sel(lon=slice(min_longitude, max_longitude))
        data = data.sel({latdim: slice(min_latitude, max_latitude)})

    return data


def area_weights(data: xr.DataArray | xr.Dataset, latdim: str = "lat") -> xr.DataArray:
    """
    Compute the relative weights for area weighting. Input data is expected to be on a regular grid.

    Parameters
    ----------
    data : xr.DataArray | xr.Dataset
        Input data
    latdim : str, optional
        name of latitude dimension, by default "lat"

    Returns
    -------
    xr.DataArray
        weights along the `latdim` dimension
    """
    lat_bnds = None
    if isinstance(data, xr.Dataset):
        try:
            lat_bnds = data[f"{latdim}_bnds"].squeeze().to_numpy()
        except KeyError:
            pass

    if lat_bnds is None:
        lats = data[latdim].to_numpy()
        lat_diff = np.diff(lats)
        lat_bnds = np.concatenate(
            [[lats[0] - lat_diff[0] / 2], lats[0:-1] + lat_diff / 2, [lats[-1] + lat_diff[1] / 2]]
        )

    if len(lat_bnds.shape) == 1:
        weights = np.sin(lat_bnds[1:] * np.pi / 180) - np.sin(lat_bnds[0:-1] * np.pi / 180)
    else:
        weights = np.sin(lat_bnds[:, 1] * np.pi / 180) - np.sin(lat_bnds[:, 0] * np.pi / 180)

    return xr.DataArray(weights, coords=[data[latdim].to_numpy()], dims=[latdim])


def area_mean(
    data: xr.DataArray | xr.Dataset,
    region: dict[str, tuple[float, float]] | None = {"lat": (-90, 90), "lon": (-180, 180)},
    weights: xr.DataArray | None = None,
) -> xr.DataArray | xr.Dataset:
    """
    Compute the area weighted mean of the data

    Parameters
    ----------
    data : xr.DataArray | xr.Dataset
        input dataset to be averaged
    region : dict[str, tuple[float, float]] | None, optional
        If set, a region is selected before averaging is performed. By default {"lat": (-90, 90), "lon": (-180, 180)}
        Latitude and longitude dimensions are read from the `region` parameter if provided.
    weights : xr.DataArray | None, optional
        User provided weights to used for the average. If not supplied weights are calculated using `area_weights`.

    Returns
    -------
    xr.DataArray | xr.Dataset
        input data after selection and averaging

    Raises
    ------
    ValueError
        If latitude and longitude coordinates cannot be found
    """

    if region is None:
        latdim = "lat"
        londim = "lon"
    else:
        latdim, londim = list(region.keys())

    if not (londim in data.coords and latdim in data.coords):
        raise ValueError("dataset should contain latitude and longitude coordinates")

    if region:
        data = select_region(data, region=region)

    if weights is None:
        weights = area_weights(data, latdim=latdim)

    return data.weighted(weights).mean(dim=[latdim, londim])


def zonal_mean(data: xr.Dataset | xr.DataArray, lon_dim: str = "lon") -> xr.Dataset | xr.DataArray:
    """Compute the zonal mean

    Parameters
    ----------
    data : xr.Dataset | xr.DataArray
        Data to be averaged.
    lon_dim : str, optional
        name of longitude dimension over which to average, by default "lon".

    Returns
    -------
    xr.Dataset | xr.DataArray
        Zonally averaged data
    """
    return data.mean(dim=lon_dim)


def monthly_mean(data: xr.Dataset | xr.DataArray) -> xr.Dataset | xr.DataArray:
    """resample data to monthly resolution

    Parameters
    ----------
    data : xr.Dataset | xr.DataArray
        input data to be resampled

    Returns
    -------
    xr.Dataset | xr.DataArray
        Monthly averaged data
    """

    return data.resample("time.month").mean(dim="time")


def mask_where(
    data: xr.Dataset | xr.DataArray, mask: xr.Dataset | xr.DataArray, **kwargs
) -> xr.Dataset | xr.DataArray:
    """Work around for the fact that dask does not properly parse kwargs in local mode

    https://github.com/dask/dask/issues/3741
    """

    return data.where(to_array(mask), **kwargs)


def rename(data: xr.DataArray | xr.Dataset, name: str):
    """rename an array or dataset that has a single array"""
    if isinstance(data, xr.Dataset):
        return to_dataset(to_array(data).rename(name))

    return data.rename(name)
