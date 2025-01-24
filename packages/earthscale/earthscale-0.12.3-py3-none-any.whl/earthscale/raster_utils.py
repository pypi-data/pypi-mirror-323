import datetime
from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass
from typing import Any, cast

import numpy as np
import xarray as xr
from affine import Affine
from loguru import logger
from pyproj import CRS, Transformer
from pyproj.enums import TransformDirection

_LATITUDE_NAMES = (
    "lat",
    "latitude",
    "lat_degrees",
    "latitude_degrees",
)
_LONGITUDE_NAMES = (
    "lon",
    "long",
    "longitude",
    "lon_degrees",
    "long_degrees",
    "longitude_degrees",
)

_LATITUDE_UNIT_NAMES = (
    "degrees_north",
    "degree_north",
    "degree_N",
    "degrees_N",
    "degreeN",
    "degreesN",
)
_LONGITUDE_UNIT_NAMES = (
    "degrees_east",
    "degree_east",
    "degree_E",
    "degrees_E",
    "degreeE",
    "degreesE",
)
_X_COORD_NAMES = (
    "x",
    "xc",
)
_Y_COORD_NAMES = (
    "y",
    "yc",
)
_TIME_NAMES = (
    "time",
    "datetime",
    "date",
)
_TIME_AXIS_NAMES = (
    "T",
    "t",
)


def find_x_dimension(dset: xr.Dataset) -> str | None:
    for dim_name in dset.dims:
        dim_name = str(dim_name)
        if dim_name.lower() in _X_COORD_NAMES:
            return dim_name
    return None


def find_y_dimension(dset: xr.Dataset) -> str | None:
    for dim_name in dset.dims:
        dim_name = str(dim_name)
        if dim_name.lower() in _Y_COORD_NAMES:
            return dim_name
    return None


def find_latitude_dimension(dset: xr.Dataset) -> str | None:
    # See https://cfconventions.org/cf-conventions/cf-conventions.html#latitude-coordinate
    for current_dim in dset.dims:
        current_dim = str(current_dim)
        if current_dim.lower() in _LATITUDE_NAMES:
            return current_dim

        dim_var = dset[current_dim]
        with suppress(KeyError):
            units = dim_var["units"]
            if units.lower() in _LATITUDE_UNIT_NAMES:
                return current_dim
        with suppress(KeyError):
            standard_name = dim_var["standard_name"]
            if standard_name.lower() == "latitude":
                return current_dim
        with suppress(KeyError):
            long_name = dim_var["long_name"]
            if long_name.lower() == "latitude":
                return current_dim
    return None


def find_longitude_dimension(dset: xr.Dataset) -> str | None:
    # See https://cfconventions.org/cf-conventions/cf-conventions.html#longitude-coordinate
    for current_dim in dset.dims:
        current_dim = str(current_dim)
        if current_dim.lower() in _LONGITUDE_NAMES:
            return current_dim

        dim_var = dset[current_dim]
        with suppress(KeyError):
            units = dim_var["units"]
            if units.lower() in _LONGITUDE_UNIT_NAMES:
                return current_dim
        with suppress(KeyError):
            standard_name = dim_var["standard_name"]
            if standard_name.lower() == "longitude":
                return current_dim
        with suppress(KeyError):
            long_name = dim_var["long_name"]
            if long_name.lower() == "longitude":
                return current_dim
    return None


def get_approx_m_per_pixel_at_point(
    crs: CRS, crs_transform: Affine, point_4326: tuple[float, float]
) -> float:
    """
    Get the approximate resolution in meters per pixel at a point in a CRS.

    Args:
        crs: The CRS of the raster.
        crs_transform: The affine transformation of the raster (in the given crs).
        point_4326: The point in WGS84 coordinates.
    """
    to_4326 = Transformer.from_crs(crs, CRS.from_epsg(4326), always_xy=True)
    c_local = to_4326.transform(
        *point_4326,
        direction=TransformDirection.INVERSE,
    )
    points_local = np.array(
        [
            [c_local[0], c_local[0] + crs_transform.a, c_local[0]],
            [c_local[1], c_local[1], c_local[1] + crs_transform.e],
        ],
        np.float64,
    )
    points_4326 = np.vstack(to_4326.transform(points_local[0], points_local[1]))

    local_aeqd = CRS(proj="aeqd", lon_0=points_4326[0][0], lat_0=points_4326[1][0])
    to_local_aeqd = Transformer.from_crs(
        CRS.from_epsg(4326), local_aeqd, always_xy=True
    )
    points_local_aeqd = np.vstack(
        to_local_aeqd.transform(points_4326[0], points_4326[1])
    ).T

    res_x = np.linalg.norm(points_local_aeqd[0] - points_local_aeqd[1])
    res_y = np.linalg.norm(points_local_aeqd[0] - points_local_aeqd[2])
    return cast(float, (res_x + res_y) / 2)


@dataclass
class CFConventionCoordinate:
    name: str
    axis: str
    long_name: str | None = None
    standard_name: str | None = None
    units: str | None = None

    def is_lat_like(self) -> bool:
        return (
            self.name in _LATITUDE_NAMES
            or self.long_name in _LATITUDE_NAMES
            or self.standard_name in _LATITUDE_NAMES
            or self.units in _LATITUDE_UNIT_NAMES
        )

    def is_lon_like(self) -> bool:
        return (
            self.name in _LONGITUDE_NAMES
            or self.long_name in _LONGITUDE_NAMES
            or self.standard_name in _LONGITUDE_NAMES
            or self.units in _LONGITUDE_UNIT_NAMES
        )

    def is_time_like(self) -> bool:
        return (
            self.name in _TIME_NAMES
            or self.long_name in _TIME_NAMES
            or self.standard_name in _TIME_NAMES
        )


def _extract_cf_convention_coordinates(
    tags: dict[str, str],
) -> dict[str, CFConventionCoordinate]:
    hash_tags: dict[str, dict[str, str]] = defaultdict(dict)
    for tag, value in tags.items():
        tag = tag.lower()
        hash_pos = tag.find("#")
        if hash_pos != -1:
            hash_tags[tag[:hash_pos]][tag[hash_pos + 1 :]] = value

    coords = {}
    for coord_name, coord_tags in hash_tags.items():
        try:
            coord_axis = coord_tags["axis"]
        except KeyError:
            continue
        if not isinstance(coord_axis, str):
            continue
        coord_axis = coord_axis.lower()

        coord = CFConventionCoordinate(
            name=coord_name,
            axis=coord_axis,
            long_name=coord_tags.get("long_name"),
            standard_name=coord_tags.get("standard_name"),
            units=coord_tags.get("units"),
        )
        coords[coord_axis] = coord

    return coords


def detect_crs_from_cf_convention_tags(tags: dict[str, Any]) -> CRS | None:
    """
    Detects the CRS if it is set via CF conventions tags, like:

    'NC_GLOBAL#Conventions': 'CF-1.6',
    'NETCDF_DIM_EXTRA': '{time}',
    'NETCDF_DIM_time_DEF': '{1,6}',
    'NETCDF_DIM_time_VALUES': '18263',
    'inun#_FillValue': '-9999',
    'inun#comment': 'water_surface_reference_datum_altitude is given in file '
                    '/mnt/globalRuns/CopyOfData/NASADEM_90m.tif',
    'inun#coordinates': 'lat lon',
    'inun#long_name': 'Coastal flooding',
    'inun#standard_name': 'water_surface_height_above_reference_datum',
    'inun#units': 'm',
    'lat#axis': 'Y',
    'lat#long_name': 'latitude',
    'lat#standard_name': 'latitude',
    'lat#units': 'degrees_north',
    'lon#axis': 'X',
    'lon#long_name': 'longitude',
    'lon#standard_name': 'longitude',
    'lon#units': 'degrees_east',
    'time#axis': 'T',
    'time#calendar': 'gregorian',
    'time#long_name': 'time',
    'time#standard_name': 'time',
    'time#units': 'Days since 1960-01-01 00:00:00'
    """
    coords = _extract_cf_convention_coordinates(tags)

    x_coord = coords.get("x")
    y_coord = coords.get("y")

    if x_coord is not None and y_coord is not None:
        if x_coord.is_lat_like() and y_coord.is_lon_like():
            return CRS.from_authority("OGC", "CRS84")
        elif x_coord.is_lon_like() and y_coord.is_lat_like():
            return CRS.from_epsg(4326)

    return None


def detect_datetime_from_cf_convention_tags(  # noqa: C901
    tags: dict[str, Any],
) -> datetime.datetime | None:
    """
    Detects the datetime from the CF convention tags.
    Example tags:
        "NC_GLOBAL#Conventions": "CF-1.6",
        "NETCDF_DIM_EXTRA": "{time}",
        "NETCDF_DIM_time_DEF": "{1,6}",
        "NETCDF_DIM_time_VALUES": "18263",
        "time#axis": "T",
        "time#calendar": "gregorian",
        "time#long_name": "time",
        "time#standard_name": "time",
        "time#units": "Days since 1960-01-01 00:00:00",
    """
    # Find a valid time coord
    coords = _extract_cf_convention_coordinates(tags)
    time_coords = [coord for coord in coords.values() if coord.is_time_like()]
    if not time_coords:
        return None
    time_coord = time_coords[0]
    # Look up the values from NETCDF_DIM_{name}_VALUES
    try:
        time_values = tags[f"NETCDF_DIM_{time_coord.name}_VALUES"]
    except KeyError:
        logger.warning(f"Could not find time values for coord {time_coord.name}")
        return None
    time_values = time_values.split(",")
    if not time_values:
        return None
    try:
        time_value = float(time_values[0])
    except ValueError:
        logger.warning(f"Could not parse time value {time_values[0]}")
        return None
    # What that value means depends on the units
    units = time_coord.units
    if units is None:
        if time_value < 100:  # probably years
            return datetime.datetime(1960 + int(round(time_value)), 1, 1)
        elif time_value < 100_000:  # probably days
            return datetime.datetime(1960, 1, 1) + datetime.timedelta(days=time_value)
        elif time_value < 10_000_000:  # probably months
            return datetime.datetime(1960, 1, 1) + datetime.timedelta(
                days=time_value * 30
            )
        else:
            return datetime.datetime(1960, 1, 1) + datetime.timedelta(days=time_value)

    units_parts = units.lower().split()
    if not units_parts:
        return None

    if len(units_parts) == 1 and units_parts[0] == "days":
        return datetime.datetime(1960, 1, 1) + datetime.timedelta(days=time_value)

    if len(units_parts) > 2 and units_parts[1] == "since":
        time_unit = units_parts[0]

        format = "%Y-%m-%d"
        str_to_parse = units_parts[2]
        if len(units_parts) > 3:
            str_to_parse += " " + units_parts[3]
            format += " %H:%M:%S.%f" if "." in str_to_parse else " %H:%M:%S"

        if len(units_parts) > 4:
            if ":" in str_to_parse:
                format += " %z"
                str_to_parse += " " + units_parts[4]
            else:
                # python 3.10 strptime cannot parse the utc offset without a colon
                with suppress(ValueError):
                    utc_offset = int(units_parts[4])
                    str_to_parse += f" {utc_offset:02d}:00"
                    format += " %z"

        try:
            base_datetime = datetime.datetime.strptime(str_to_parse, format)
        except ValueError:
            return None

        if time_unit == "days" or time_unit == "day" or time_unit == "d":
            return base_datetime + datetime.timedelta(days=time_value)
        elif time_unit == "hours" or time_unit == "hour" or time_unit == "h":
            return base_datetime + datetime.timedelta(hours=time_value)
        elif time_unit == "minutes" or time_unit == "minute" or time_unit == "m":
            return base_datetime + datetime.timedelta(minutes=time_value)
        elif (
            time_unit == "seconds"
            or time_unit == "second"
            or time_unit == "sec"
            or time_unit == "s"
        ):
            return base_datetime + datetime.timedelta(seconds=time_value)

    return None
