from typing import cast

import numpy as np
from affine import Affine
from pyproj import CRS, Transformer
from pyproj.enums import TransformDirection


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
