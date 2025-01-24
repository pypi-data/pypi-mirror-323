import concurrent
import datetime
import fnmatch
import functools
import glob
import re
import time
import uuid
from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable, Sequence
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from copy import copy, deepcopy
from functools import cached_property
from pathlib import Path
from typing import Any, ClassVar, Generic, Literal, TypeVar, Union, cast

import contextily as ctx
import ee
import fsspec
import networkx as nx
import numpy as np
import odc.geo.xr
import odc.stac
import pandas as pd
import rasterio
import requests
import xarray as xr
from affine import Affine
from loguru import logger
from networkx import is_directed_acyclic_graph
from odc.geo import Geometry, Resolution
from odc.geo.geobox import GeoBox
from odc.geo.xr import xr_coords
from odc.stac import output_geobox, parse_items
from pydantic import BaseModel
from pyproj import CRS, Transformer
from pyproj.enums import TransformDirection
from pystac import Item
from rasterio.errors import RasterioIOError
from rasterio.io import DatasetReader
from rasterio.transform import from_bounds
from rio_stac import create_stac_item
from rio_stac.stac import RASTER_EXT_VERSION
from rio_tiler.constants import WGS84_CRS
from rioxarray.exceptions import OneDimensionalRaster
from shapely import MultiPolygon, Polygon, box
from stac_pydantic import Item as PydanticItem  # type: ignore

from earthscale.auth import (
    get_fsspec_storage_options,
    get_gdal_options_for_url,
)
from earthscale.constants import (
    DEFAULT_CHUNKSIZES,
    MAX_NUM_EO_ASSET_BANDS,
    METERS_PER_DEGREE,
    XARRAY_CACHE_LEN,
)
from earthscale.datasets._earthengine import parse_earth_engine_stac_to_earthscale
from earthscale.datasets.dataset import (
    BandDimensions,
    Dataset,
    DatasetDefinition,
    DatasetMetadata,
    DatasetStatus,
    DatasetType,
    DefinitionType,
    Dimension,
    DimensionInfo,
    DimensionType,
    registry,
)
from earthscale.datasets.graph import (
    JoinNode,
    create_source_graph,
    get_dset_for_node,
    get_final_node_name,
    validate_graph,
)
from earthscale.exceptions import (
    EarthscaleError,
    UnsupportedRasterFormatError,
    convert_rasterio_to_earthscale,
)
from earthscale.google_cloud_utils import get_region_from_gcs_url
from earthscale.proj_utils import crs_from_str
from earthscale.raster_utils import (
    detect_crs_from_cf_convention_tags,
    detect_datetime_from_cf_convention_tags,
    find_latitude_dimension,
    find_longitude_dimension,
    find_x_dimension,
    find_y_dimension,
)
from earthscale.types import BBOX, Chunksizes
from earthscale.utils import (
    create_valid_url,
    generate_filter_date_range,
    is_gcs_url,
    is_google_drive_url,
    parse_dimension_placeholder_path,
)


def _patched_geo_box_from_rio(rdr: rasterio.DatasetReader) -> GeoBox:
    """
    This overrides the GeoBox.from_rio method to use the CF tags to detect the CRS
    """
    crs = rdr.crs
    if crs is None:
        crs = detect_crs_from_cf_convention_tags(rdr.tags())
    return GeoBox(
        shape=rdr.shape,
        affine=rdr.transform,
        crs=crs,
    )


GeoBox.from_rio = _patched_geo_box_from_rio  # type: ignore

Groupby = (
    Literal["one_plane"] | Literal["time"] | Literal["solar_day"] | Literal["id"] | str
)


class NoFilesForGlobError(EarthscaleError):
    """Raised when no files are found for a given glob pattern"""

    pass


class NoGeoboxError(EarthscaleError):
    """Raised when a dataset does not have a geobox set"""

    pass


class CannotConvertEarthEngineToXarrayError(EarthscaleError):
    """Raised when a user tries to call `.to_xarray()` for an earth engine dataset"""

    pass


class CacheEntry:
    def __init__(
        self,
        dset: xr.Dataset,
        bbox: BBOX | None,
        bands: Iterable[str] | None,
        chunksizes: Chunksizes,
    ):
        self.dset = dset
        self.bbox = bbox
        self.bands: tuple[str, ...] | None = tuple(bands) if bands is not None else None
        self.chunksizes = chunksizes


class DatasetCache:
    """Geo-aware cache for datasets, checking to see if we already
    have a dataset with the same bounding box and bands.

    Evicts the oldest entries first
    """

    def __init__(self, cache_len: int = 10):
        assert cache_len > 0
        self.cache_len = cache_len
        self.cache: dict[uuid.UUID, list[CacheEntry]] = defaultdict(list)
        self.most_recent_keys: list[uuid.UUID] = []

    def _total_length(self) -> int:
        return sum(len(v) for v in self.cache.values())

    def add(
        self,
        dataset_version_id: uuid.UUID,
        chunksizes: Chunksizes,
        bbox: BBOX | None,
        bands: Iterable[str] | None,
        dset: xr.Dataset,
    ) -> None:
        entry = CacheEntry(dset, bbox, bands, chunksizes)
        if dataset_version_id not in self.cache:
            self.cache[dataset_version_id] = []
        self.cache[dataset_version_id].append(entry)
        self.most_recent_keys.append(dataset_version_id)
        if self._total_length() > self.cache_len:
            oldest_key = self.most_recent_keys.pop(0)
            if len(self.cache[oldest_key]) > 0:
                self.cache[oldest_key].pop(0)
            else:
                # if the key no longer has any entries, remove it from the cache
                self.most_recent_keys = [
                    k for k in self.most_recent_keys if k != oldest_key
                ]

    def get(
        self,
        dataset_version_id: uuid.UUID,
        chunksizes: Chunksizes,
        bbox: BBOX | None,
        bands: Iterable[str] | None,
    ) -> xr.Dataset | None:
        entries = self.cache[dataset_version_id]
        self.most_recent_keys.append(dataset_version_id)
        for entry in entries:
            if entry.bands is None:
                is_bands_subset = True
            else:
                is_bands_subset = (bands is not None) and all(
                    band in entry.bands for band in bands
                )

            if entry.bbox is None:
                bbox_is_subset = True
            elif bbox is None and entry.bbox is not None:
                bbox_is_subset = False
            else:
                query_bbox = box(*bbox)
                cached_bbox = box(*entry.bbox)
                # We need a small buffer to account for floating point precision issues
                bbox_is_subset = cached_bbox.contains(
                    query_bbox.buffer(-1e-14)
                ) or cached_bbox.equals(query_bbox)
            if is_bands_subset and bbox_is_subset:
                return entry.dset
        return None


# Cache to avoid duplicate computations of `.to_xarray()` as that's expensive for large
# datasets
_XARRAY_CACHE = DatasetCache(cache_len=XARRAY_CACHE_LEN)
_DEFAULT_DATETIME = datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)

# Arguments other than `geobox` that `odc.stac.load` uses for georeferencing
_GEOREFERENCING_ARGS = (
    "x",
    "y",
    "lon",
    "lat",
    "crs",
    "resolution",
    "align",
    "anchor",
    "like",
    "geopolygon",
    "bbox",
)


def _crs_from_attrs(xr_attrs: dict[Hashable, Any]) -> CRS | None:
    # Logic as described here:
    # https://gdal.org/en/latest/drivers/raster/zarr.html#srs-encoding
    # https://gdal.org/en/latest/drivers/raster/netcdf.html#georeference
    # https://corteva.github.io/rioxarray/latest/getting_started/crs_management.html
    with suppress(KeyError, TypeError):
        return CRS.from_user_input(xr_attrs["_CRS"]["url"])

    with suppress(KeyError, TypeError):
        return CRS.from_wkt(xr_attrs["_CRS"]["wkt"])

    with suppress(KeyError, TypeError):
        return CRS.from_json_dict(xr_attrs["_CRS"]["projjson"])

    with suppress(KeyError, TypeError):
        return CRS.from_wkt(xr_attrs["spatial_ref"]["crs_wkt"])

    with suppress(KeyError, TypeError):
        return CRS.from_wkt(xr_attrs["spatial_ref"])

    return None


def _detect_zarr_crs(dset: xr.Dataset) -> CRS | None:
    crs = _crs_from_attrs(dset.attrs)
    if crs is not None:
        return crs
    with suppress(KeyError, TypeError):
        crs = _crs_from_attrs(dset["spatial_ref"].attrs)
        if crs is not None:
            return crs

    array_crs: dict[Hashable, CRS] = {}
    for array_name in dset:
        array = dset[array_name]
        current_crs = _crs_from_attrs(array.attrs)
        if current_crs is not None:
            array_crs[array_name] = current_crs

    unique_crs = set(array_crs.values())
    if unique_crs:
        first_crs = unique_crs.pop()
        if len(unique_crs) > 0:
            logger.warning(
                "Found multiple CRS values in the Zarr dataset, "
                "using the first one: %s",
                first_crs,
            )
        return first_crs

    lat_dim_name = find_latitude_dimension(dset)
    lon_dim_name = find_longitude_dimension(dset)
    if lat_dim_name is not None and lon_dim_name is not None:
        return CRS.from_epsg(4326)

    return None


def _coordinates_are_top_left(dset: xr.Dataset) -> bool:
    """Tries to figure out whether coordinates are top left

    Except for the case where the top-left coordinate is (-180, 90) we can't be sure
    though. So this only captures the simple case
    """
    if dset.rio.crs != WGS84_CRS:
        return False

    lon = dset["x"]
    lat = dset["y"]
    return bool(lat[0] == 90 and lon[0] == -180)


def _shift_coordinates_from_top_left_to_pixel_center(dset: xr.Dataset) -> xr.Dataset:
    """Shifts the coordinates from the top left to the pixel center"""
    lon = dset["x"]
    lat = dset["y"]

    res_x, res_y = dset.rio.resolution()

    lon_center = lon + res_x / 2
    lat_center = lat + res_y / 2
    dset["x"] = lon_center
    dset["y"] = lat_center

    return dset


def _validate_dset(dset: xr.Dataset) -> None:
    assert isinstance(dset, xr.Dataset)
    assert "x" in dset.coords
    assert "y" in dset.coords
    assert dset.rio.crs is not None
    # assert dset.rio.crs == CRS.from_epsg(4326)


class RasterDataset(Generic[DefinitionType], Dataset[DefinitionType]):
    def __init__(
        self,
        name: str,
        explicit_name: bool,
        attributes: dict[str, str] | None,
        graph: nx.DiGraph,
        metadata: DatasetMetadata,
        definition: DefinitionType,
        geobox_callback: Callable[[], GeoBox],
        dataset_id: uuid.UUID | None,
        dataset_version_id: uuid.UUID | None,
    ):
        self._graph = graph
        self._geobox_callback = geobox_callback
        validate_graph(self._graph)

        super().__init__(
            name,
            explicit_name,
            attributes,
            metadata,
            type_=DatasetType.RASTER,
            # Raster datasets are ready by default
            status=DatasetStatus.READY,
            definition=definition,
            dataset_id=dataset_id,
            dataset_version_id=dataset_version_id,
        )

    @property
    def geobox(self) -> GeoBox:
        return self._geobox_callback()

    def get_bounds(self) -> tuple[float, float, float, float]:
        # Always returns the bounds in EPSG:4326
        return cast(
            tuple[float, float, float, float],
            tuple(self._geobox_callback().boundingbox.to_crs(4326)),
        )

    def get_dimension_info(self) -> DimensionInfo:
        raise NotImplementedError

    def join(
        self,
        # Union is required here instead of `|` as that won't work with a string
        others: Union[Sequence["RasterDataset[Any]"], "RasterDataset[Any]"],
        match: "RasterDataset[Any]",
        name: str | None = None,
        metadata: DatasetMetadata | None = None,
    ) -> "RasterDataset[Any]":
        if isinstance(others, RasterDataset):
            others = [others]
        explicit_name = name is not None
        name = name or str(uuid.uuid4())
        new_graph = self._graph.copy()
        join_node_name = f"join_{name}"
        node = JoinNode(
            match_name=match.name,
            output_name=name,
            output_metadata=metadata,
        )
        new_graph.add_node(
            join_node_name,
            node=node,
        )
        # Connect this dataset to the join node
        new_graph.add_edge(
            get_final_node_name(self._graph),
            join_node_name,
        )
        # Connect all other datasets to the join node
        geobox = self.geobox
        for other in others:
            new_graph = nx.union(new_graph, other._graph)
            new_graph.add_edge(
                get_final_node_name(other._graph),
                join_node_name,
            )
            geobox = geobox & other.geobox

        new_attributes = metadata.attributes if metadata is not None else []
        attributes = {
            attr.name: attr.value for attr in self.metadata.attributes + new_attributes
        }
        return RasterDataset(
            name,
            explicit_name,
            attributes,
            new_graph,
            metadata or DatasetMetadata(),
            definition=DatasetDefinition(),
            geobox_callback=lambda: geobox,
            dataset_id=None,
            dataset_version_id=None,
        )

    def to_xarray(
        self,
        # The bounding box is assumed to be in EPSG:4326. Might lead to speedups for
        # certain dataset types (e.g. STAC and ImageDataset)
        bbox: BBOX | None = None,
        # Subset of bands to return. Might lead to speedup for certain dataset types
        # (e.g. STAC and ImageDataset)
        bands: Iterable[str] | None = None,
        chunksizes: Chunksizes | None = None,
    ) -> xr.Dataset:
        if chunksizes is None:
            chunksizes = DEFAULT_CHUNKSIZES

        start_time = time.time()
        cached_dset: xr.Dataset | None = None
        if self.dataset_version_id is not None:
            cached_dset = _XARRAY_CACHE.get(
                self.dataset_version_id,
                chunksizes,
                bbox,
                bands,
            )
        if cached_dset is not None:
            logger.debug(
                f"Found xr.Dataset for dataset_version_id '{self.dataset_version_id}', "
                f"bounds '{bbox}', bands '{bands}' and chunksizes '{chunksizes}' in "
                f"the cache, using that"
            )
            dset = cached_dset
        else:
            assert is_directed_acyclic_graph(self._graph)
            final_node_name = get_final_node_name(self._graph)
            dset = get_dset_for_node(
                self._graph, final_node_name, bbox, bands, chunksizes
            )

        # While the datasets already have information about the `bbox` and `bands`
        # arguments, cropping them again here just to be certain as it should not lead
        # to a performance hit
        if bbox is not None:
            try:
                # We try clipping with clip_box first, as that should be more performant
                dset = dset.rio.clip_box(*bbox, crs=CRS.from_epsg(4326))
            except OneDimensionalRaster:
                # We try with more exact clipping if the above fails because the area
                # is smaller than a pixel
                dset = dset.rio.clip(
                    [box(*bbox)],
                    crs=CRS.from_epsg(4326),
                    # All touched is important here to get at leas one pixel
                    all_touched=True,
                )
        if bands is not None:
            dset = dset[bands]

        # Make sure that all "time" values are datetime objects with only dates set
        if "time" in dset.sizes:
            dset["time"] = dset["time"].dt.date.astype(np.datetime64)

        _validate_dset(dset)
        if self.dataset_version_id is not None:
            _XARRAY_CACHE.add(
                self.dataset_version_id,
                chunksizes,
                bbox,
                bands,
                dset,
            )
        logger.debug(
            f".to_xarray() for name '{self.name}', dataset_version_id "
            f"'{self.dataset_version_id}', bounds '{bbox}', bands '{bands}' and "
            f"chunksizes '{chunksizes}' took {time.time() - start_time} seconds"
        )
        return dset

    def get_polygon(self, polygon: Polygon | MultiPolygon) -> xr.Dataset:
        dset = self.to_xarray()
        clipped_to_bounds = dset.rio.clip_box(*polygon.bounds)
        clipped = clipped_to_bounds.rio.clip([polygon])
        return cast(xr.Dataset, clipped)


def _get_dimensions_from_dataset(dataset: RasterDataset[Any]) -> DimensionInfo:
    dset = dataset.to_xarray()

    dimension_dict: dict[str, DimensionType] = {}
    band_dimensions: list[BandDimensions] = []
    for band in dset.data_vars:
        dims: list[str] = []

        non_spatial_dims = [
            str(dim) for dim in dset[band].dims if dim not in ["y", "x"]
        ]
        dims.extend(non_spatial_dims)
        new_dims = [dim for dim in non_spatial_dims if dim not in dimension_dict]
        for dim in new_dims:
            # Handle dimensions with no coordinates (just indices)
            dim_values: DimensionType
            if dim not in dset[band].coords:
                dim_values = list(range(dset[band].sizes[dim]))
            else:
                values = dset[band][dim].values
                # Convert datetime64 values to milliseconds since epoch,
                # which is a more portable format
                if np.issubdtype(values.dtype, np.datetime64):
                    dim_values = cast(
                        list[float],
                        (
                            values.astype("datetime64[ns]").astype("int64") / 1_000_000
                        ).tolist(),
                    )
                else:
                    dim_values = cast(list[str], values.tolist())
                # convert to string if inconsistent types
                valid_types = (str, int, float, datetime.datetime)
                if not any(
                    all(isinstance(v, t) for v in dim_values) for t in valid_types
                ):
                    try:
                        dim_values = [str(v) for v in dim_values]
                    except Exception as e:
                        raise ValueError(
                            f"Could not convert dimension values for band '{band}' and "
                            f"dimension '{dim}' to strings"
                        ) from e
            dimension_dict[dim] = dim_values
        band_dimensions.append(BandDimensions(band_name=band, dimension_names=dims))
    dimensions = [
        Dimension(name=dim, values=values) for dim, values in dimension_dict.items()
    ]
    return DimensionInfo(dimensions=dimensions, band_dimensions=band_dimensions)


class ZarrDatasetDefinition(DatasetDefinition):
    store: str
    rename: dict[str, str] | None
    kw_args: dict[str, Any] | None


class ZarrDataset(RasterDataset[ZarrDatasetDefinition]):
    """Dataset based on a Zarr store.

    When loading into xarray, this dataset type will automatically standardize the
    dimensions of the dataset to 'y', 'x' and 'time' if present. It will try to infer
    spatial dimensions, so if 'lon' or 'longitude' is present, it will be renamed to
    'x'.

    This only supports datasets with 2 or 3 dimensions. If an additional dimension like
    'band' is present, it will be renamed to 'band_1', 'band_2' etc. If more than one
    additional dimension is present, a `ValueError` will be raised.

    Args:
        store:
            The Zarr store to load the dataset from. Can contain a single placeholder
            with a dimension name, e.g. `gs://data/{time}.zarr`. If specified, this
            concatenates multiple Zarrs along either an existing or new dimension as
            named in the pattern. In the above example, all Zarrs found for the glob
            `gs://data/*.zarr` are concatenated along the `time` dimension. If the time
            dimension does not already exist, it is created.
        name:
            The name of the dataset. Defaults to a random UUID. If explicitly given, the
            dataset will be visible in the Earthscale platform.
        rename:
            A dictionary mapping the original dimension names to the desired dimension
            names.
        kwargs:
            Additional keyword arguments to pass to `xarray.open_zarr`.

    """

    def __init__(
        self,
        store: str | Path,
        name: str | None = None,
        attributes: dict[str, str] | None = None,
        metadata: DatasetMetadata | None = None,
        rename: dict[str, str] | None = None,
        dataset_id: uuid.UUID | None = None,
        dataset_version_id: uuid.UUID | None = None,
        **kwargs: Any | None,
    ):
        # run parsing now to validate early for the user
        parse_dimension_placeholder_path(store)
        explicit_name = name is not None
        name = name or str(uuid.uuid4())

        self._store = store
        self._rename = rename
        self._kwargs = kwargs

        definition = ZarrDatasetDefinition(
            store=str(store),
            rename=rename,
            kw_args=kwargs,
        )

        # There's no use for bbox or bands here as the performance is the same whether
        # the whole dataset metadata is loaded or not
        def load(
            bbox: BBOX | None,
            bands: Iterable[str] | None,
            chunksizes: Chunksizes | None,
        ) -> xr.Dataset:
            logger.debug("Calling load function for ZarrDataset")
            return _load_zarr_dataset(
                store=store,
                rename=rename or {},
                **kwargs,
            )

        graph = create_source_graph(
            f"load_zarr_dataset_{name}",
            name,
            metadata,
            load,
        )

        super().__init__(
            name=name,
            explicit_name=explicit_name,
            attributes=attributes,
            graph=graph,
            metadata=metadata or DatasetMetadata(),
            # We want the geobox of the full dataset as well as all bands here, so not
            # passing a bounding box here
            geobox_callback=lambda: load(
                bbox=None,
                bands=None,
                chunksizes=None,
            ).odc.geobox,
            definition=definition,
            dataset_id=dataset_id,
            dataset_version_id=dataset_version_id,
        )

    @property
    def data_region(self) -> str | None:
        if isinstance(self._store, str) and is_gcs_url(self._store):
            return get_region_from_gcs_url(self._store)
        return None

    def get_dimension_info(self) -> DimensionInfo:
        return _get_dimensions_from_dataset(self)


# Using a lower `maxsize` as the images are potentially quite large
@functools.lru_cache(maxsize=10)
def _convert_stac_items_to_geobox(
    items: tuple[Item, ...],
    bands: tuple[str, ...] | None,
    **kwargs: Any,
) -> GeoBox:
    logger.debug("Converting STAC items to geobox")
    geobox = output_geobox(
        items=list(parse_items(items)),
        bands=bands,
        crs=kwargs.get("crs"),
        resolution=kwargs.get("resolution"),
        anchor=kwargs.get("anchor"),
        align=kwargs.get("align"),
        geobox=kwargs.get("geobox"),
        like=kwargs.get("like"),
        geopolygon=kwargs.get("geopolygon"),
        bbox=kwargs.get("bbox"),
        lon=kwargs.get("lon"),
        lat=kwargs.get("lat"),
        x=kwargs.get("x"),
        y=kwargs.get("y"),
    )
    if geobox is None:
        raise ValueError(
            "Could not determine geobox for dataset. "
            "Ensure that the items have the proj STAC extension or pass "
            "in a geobox or crs, resulution, and bbox explicitly."
        )
    return geobox


class STACDatasetDefinition(DatasetDefinition):
    items: list[PydanticItem]
    bands: list[str] | None
    groupby: Groupby | None
    kw_args: dict[str, Any] | None


class STACDataset(RasterDataset[STACDatasetDefinition]):
    """Spatio-Temporal Asset Catalog (STAC) based dataset

    Args:
        items:
            Items to build the dataset from. We allow passing in serialized stac items
            (dicts) as well.
            If no explicit geobox is passed in, the geobox will be determined from the
            items. In this case, the proj extension to the STAC item is required. When
            using rio-stac's `create_stac_item` function, this can be achieved by
            passing in the `with_proj=True` argument.

        bands:
            List of bands to load. Defaults to all bands

        groupby:
            Controls what items get placed in to the same pixel plane.

            The following have special meaning:

               * "one_plane": All images are loaded into a single plane
               * "time" items with exactly the same timestamp are grouped together
               * "solar_day" items captured on the same day adjusted for solar time
               * "id" every item is loaded separately
               * `None`: No grouping is done, each image is loaded onto an extra plane

            Any other string is assumed to be a key in Item's properties dictionary.
            Please note that contrary to `odc.stac.load` we do not support callables as
            we need to be able to serialize the dataset. Defaults to "one_plane".

        name:
            Name of the dataset. Defaults to a random UUID. If explicitly given,
            The dataset will be visible in the Earthscale platform

        metadata:
            Dataset Metadata. Defaults to None.

        kwargs:
            Additional keyword arguments to pass to
            [`odc.stac.load`](https://odc-stac.readthedocs.io/en/latest/_api/odc.stac.load.html)
            Only serializable arguments can be passed to STAC.
    """

    def __init__(
        self,
        items: list[Item | dict[str, Any]],
        bands: list[str] | None = None,
        groupby: Groupby | None = "one_plane",
        name: str | None = None,
        attributes: dict[str, str] | None = None,
        metadata: DatasetMetadata | None = None,
        dataset_id: uuid.UUID | None = None,
        dataset_version_id: uuid.UUID | None = None,
        **kwargs: Any | None,
    ):
        parsed_items = [
            Item.from_dict(item) if not isinstance(item, Item) else item
            for item in items
        ]

        metadata = metadata or DatasetMetadata()
        explicit_name = name is not None
        name = name or str(uuid.uuid4())
        geobox = _convert_stac_items_to_geobox(
            tuple(parsed_items),
            tuple(bands) if bands else None,
            **kwargs,
        )

        definition = STACDatasetDefinition(
            items=[PydanticItem(**item.to_dict()) for item in parsed_items],
            bands=bands,
            groupby=groupby,
            kw_args=kwargs,
        )

        def _load_stac_dataset_wrapper(
            bbox: BBOX | None,
            bands_selection: Iterable[str] | None,
            chunksizes: Chunksizes | None,
        ) -> xr.Dataset:
            # If a particular `to_xarray` call requests all bands, but
            # the dataset was created with a subset of bands, we need
            # to respect that and not load all bands from the STAC
            # items.
            if bands and not bands_selection:
                bands_selection = bands
            return _load_stac_dataset(
                items=parsed_items,
                bands=bands_selection,
                groupby=groupby,
                full_geobox=geobox,
                bbox=bbox,
                chunksizes=chunksizes,
                **kwargs,
            )

        super().__init__(
            name=name or str(uuid.uuid4()),
            explicit_name=explicit_name,
            attributes=attributes,
            graph=create_source_graph(
                f"load_file_dataset_{name}", name, metadata, _load_stac_dataset_wrapper
            ),
            metadata=metadata,
            geobox_callback=lambda: geobox,
            definition=definition,
            dataset_id=dataset_id,
            dataset_version_id=dataset_version_id,
        )

    def get_dimension_info(self) -> DimensionInfo:
        return _get_dimensions_from_dataset(self)


class BandInfoRow(BaseModel):
    index: int
    """
    0-based band index
    """
    name: str
    datetime: str | None = None
    min: float | None = None
    max: float | None = None

    # TODO: add validation for datetime


class FilenameBandPattern(BaseModel):
    pattern: str
    band: str


def _band_info_df_to_list(df: pd.DataFrame) -> list[BandInfoRow]:
    # convert any datetimes to isoformat
    if "datetime" in df.columns:
        df["datetime"] = df["datetime"].apply(lambda x: x.isoformat())
    return [BandInfoRow(index=idx, **row.to_dict()) for idx, row in df.iterrows()]


def _band_info_list_to_df(
    band_info: Sequence[BandInfoRow | dict[str, Any]],
) -> pd.DataFrame:
    def _row_to_dict(row: BandInfoRow | dict[str, Any]) -> dict[str, Any]:
        if isinstance(row, BandInfoRow):
            return row.model_dump()
        return row

    df = pd.DataFrame([_row_to_dict(row) for row in band_info])
    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"])

    # Drop datetime, min or max column if all values are NaN
    df = df.dropna(axis=1, how="all")
    if "index" in df.columns:
        df = df.set_index("index")
    return df


class ImageDatasetDefinition(DatasetDefinition):
    glob_url: str | list[str]
    bands: list[str] | None
    band_info: list[BandInfoRow] | None
    groupby: Groupby | None
    datetime_: datetime.datetime | tuple[datetime.datetime, datetime.datetime] | None
    filename_date_pattern: str | None
    filename_band_pattern: list[FilenameBandPattern] | None
    kw_args: dict[str, Any]


GetStacItemsCallback = Callable[["ImageDataset"], list[Item] | None]


class ImageDataset(RasterDataset[ImageDatasetDefinition]):
    """Dataset based on single images.

     Images must be in a format that can be read by `rasterio`. Under the hood, an
     `ImageDataset` creates a list of STAC items and then uses `odc.stac.load` to load
     the dataset.

     An important concept here is how the time dimension of the `Dataset` is set and
     which images account for which time.

     To group images by time (and thus create a time dimension), you can use the
     `groupby` argument. For more information on the options, please refer to the
     documentation of `odc.stac.load`
     ([here](https://odc-stac.readthedocs.io/en/latest/_api/odc.stac.load.html)). Note
     that as we need to serialize the class, we do not allow callables to be passed in.

     As images generally don't have time information, we provide several ways to set the
     time interval for an image. Only one of the following options can be set:

     1. `band_info`: A pandas DataFrame with band information. This is used to parse
        TIFF band indices into band name and datetime information.
     2. `datetime_`: Either a single `datetime.datetime` or a tuple of two
        `datetime.datetime` objects. If a single `datetime.datetime` is provided, all
        images will have the same timestamp. If a tuple is provided, the first element
        will be the start time and the second element will be the end time. This
        interval will be used for all images. This will result in all images having the
        same time interval.

    Args:
       glob_url:
           URL pattern to find images with. E.g. `gs://bucket/path/to/images/*.tif`.
           Can either be a single string or a list of strings. If a list is given, the
           ordering of the URLs is kept. E.g. images from the first URL will overwrite
           later ones.
       bands:
           List of bands to load. Defaults to all bands.
       band_info:
           DataFrame with band information. Defaults to None. This is used to provide
           metadata about bands in the images. It maps the band index to the band name
           and optionally time, min and max values. The index of the dataframe should be
           the band index (0-indexed). The following columns can be present:
             - name (str; required): The name of the band
             - datetime (datetime.datetime; optional): The datetime of the band
             - min (float; optional): The minimum value of the band
             - max (float; optional): The maximum value of the band
           We also allow this to be passed in as a dictionary of
           {column -> {index -> value}}.
           Can only be used if `datetime_` is not set.
       filename_date_pattern:
            A string pattern representing how dates are formatted in the filenames.
            This pattern uses strftime-style format codes to extract date information.

            Common format codes:
            %Y - Year with century as a decimal number (e.g., 2023)
            %m - Month as a zero-padded decimal number (01-12)
            %d - Day of the month as a zero-padded decimal number (01-31)

            Example:
            - For files named like "brasil_coverage_2011.tif":
              filename_date_pattern="%Y"

            If None (default), no date information will be extracted from filenames.
       filename_band_pattern:
            A dictionary mapping wildcard band name patterns to actual band names.
            E.g. {"*_B[0-9]": "band_1"} would map all bands starting with "B" and
            ending with a number to "band_1". Uses Unix filename pattern rules.
       groupby:
            Controls what items get placed in to the same pixel plane.

            The following have special meaning:

               * "one_plane": All images are loaded into a single plane
               * "time" items with exactly the same timestamp are grouped together
               * "solar_day" items captured on the same day adjusted for solar time
               * "id" every item is loaded separately
               * `None`: No grouping is done, each image is loaded onto an extra plane

            Any other string is assumed to be a key in Item's properties dictionary.
            Please note that contrary to `odc.stac.load` we do not support callables as
            we need to be able to serialize the dataset. Defaults to "one_plane".

       datetime_:
           Either a single `datetime.datetime` or a tuple of two `datetime.datetime`
           objects. If a single `datetime.datetime` is provided, all images will have
           the same time. If a tuple is provided, the first element will be the start
           time and the second element will be the end time. This interval will be
           valid for all images.
           Can only be set if `band_info` is not set.
       name:
           Name of the dataset. Defaults to a random UUID. If explicitly given, the
           dataset will visible in the Earthscale platform
       metadata:
           Dataset Metadata. Defaults to None.
       kwargs:
           Additional keyword arguments to pass to `odc.stac.load`
           (more information in
           [their docs](https://odc-stac.readthedocs.io/en/latest/_api/odc.stac.load.html))

    """

    _GET_ITEMS_CALLBACK: ClassVar[GetStacItemsCallback | None] = None

    @classmethod
    def register_get_items_callback(cls, callback: GetStacItemsCallback) -> None:
        cls._GET_ITEMS_CALLBACK = callback

    def __init__(
        self,
        glob_url: str | list[str],
        bands: list[str] | None = None,
        band_info: pd.DataFrame | Sequence[BandInfoRow | dict[str, Any]] | None = None,
        filename_date_pattern: str | None = None,
        filename_band_pattern: dict[str, str] | list[FilenameBandPattern] | None = None,
        groupby: Groupby | None = "one_plane",
        datetime_: datetime.datetime
        | tuple[datetime.datetime, datetime.datetime]
        | None = None,
        name: str | None = None,
        attributes: dict[str, str] | None = None,
        metadata: DatasetMetadata | None = None,
        dataset_id: uuid.UUID | None = None,
        dataset_version_id: uuid.UUID | None = None,
        **kwargs: Any | None,
    ):
        metadata = metadata or DatasetMetadata()
        explicit_name = name is not None
        name = name or str(uuid.uuid4())
        glob_urls = [glob_url] if isinstance(glob_url, str) else glob_url
        glob_urls = [create_valid_url(url) for url in glob_urls]

        if band_info is not None and datetime_ is not None:
            raise ValueError(
                "Only one of band_info or datetime_ can be used. Both are set."
            )

        if band_info is not None:
            if not isinstance(band_info, pd.DataFrame):
                band_info = _band_info_list_to_df(band_info)
            _validate_band_info_dataframe(band_info)
            has_min = "min" in band_info.columns
            has_max = "max" in band_info.columns
            has_only_one_of_min_max = has_min != has_max
            if has_only_one_of_min_max:
                raise ValueError(
                    "If specifying min and max values for a band, both must be provided"
                )
            if has_min and has_max:
                _update_min_max_metadata(metadata, band_info)

        if isinstance(filename_band_pattern, dict):
            filename_band_pattern = [
                FilenameBandPattern(pattern=pattern, band=band)
                for pattern, band in filename_band_pattern.items()
            ]

        definition = ImageDatasetDefinition(
            glob_url=glob_urls,
            bands=bands,
            band_info=_band_info_df_to_list(band_info)
            if band_info is not None
            else None,
            groupby=groupby,
            datetime_=datetime_,
            filename_date_pattern=filename_date_pattern,
            filename_band_pattern=filename_band_pattern,
            kw_args=kwargs,
        )

        super().__init__(
            name=name,
            explicit_name=explicit_name,
            attributes=attributes,
            graph=create_source_graph(
                f"load_file_dataset_{name}",
                name,
                metadata,
                lambda bbox, bands_selection, chunksizes: _load_stac_dataset(
                    items=self._items,
                    bands=bands_selection,
                    groupby=groupby,
                    full_geobox=self.geobox,
                    bbox=bbox,
                    chunksizes=chunksizes,
                    band_info=band_info,
                    **kwargs,
                ),
            ),
            metadata=metadata,
            definition=definition,
            geobox_callback=lambda: _convert_stac_items_to_geobox(
                tuple(self._items),
                tuple(self.definition.bands) if self.definition.bands else None,
                **self.definition.kw_args,
            ),
            dataset_id=dataset_id,
            dataset_version_id=dataset_version_id,
        )

    @cached_property
    def _items(self) -> list[Item]:
        return self.get_items()

    @property
    def data_region(self) -> str | None:
        regions_count: dict[str, int] = defaultdict(int)
        for glob_url in self.definition.glob_url:
            if is_gcs_url(glob_url):
                region = get_region_from_gcs_url(glob_url)
                if region is not None:
                    regions_count[region] += 1
        if not regions_count:
            return None
        if len(regions_count) == 1:
            return next(iter(regions_count.keys()))
        # return the region with the most items
        return max(regions_count.items(), key=lambda x: x[1])[0]

    def get_items(self) -> list[Item]:
        if ImageDataset._GET_ITEMS_CALLBACK is not None:
            items = ImageDataset._GET_ITEMS_CALLBACK(self)
            if items:
                return items

        logger.debug("Computing items for ImageDataset")
        if self.definition.band_info is not None:
            band_info = _band_info_list_to_df(self.definition.band_info)
        else:
            band_info = None

        # There is no (tested) implementation of fsspec for Google Drive. There is
        # https://github.com/fsspec/gdrivefs but it isn't tested and has no support for
        # shared drives (which we definitely need).
        # As Google Drive does not have globs anyway, we can just return the original
        # URL
        image_urls = []
        glob_urls = (
            [self.definition.glob_url]
            if isinstance(self.definition.glob_url, str)
            else self.definition.glob_url
        )
        for glob_url in glob_urls:
            if is_google_drive_url(glob_url):
                image_urls.append(glob_url)
            else:
                fs, _ = fsspec.url_to_fs(
                    glob_url,
                    **get_fsspec_storage_options(glob_url),
                )
                image_urls.extend(
                    fs.unstrip_protocol(path) for path in fs.glob(glob_url)
                )

        if len(image_urls) == 0:
            raise NoFilesForGlobError(f"No files found for glob urls: {glob_urls}")

        items = _create_stac_items_from_urls(
            urls=image_urls,
            datetime_=self.definition.datetime_,
            band_info=band_info,
            filename_date_pattern=self.definition.filename_date_pattern,
            filename_band_pattern=self.definition.filename_band_pattern,
        )
        return items

    def get_dimension_info(self) -> DimensionInfo:
        return _get_dimensions_from_dataset(self)


def _update_min_max_metadata(
    metadata: DatasetMetadata, band_info: pd.DataFrame
) -> None:
    """Updates min/max values if both are present in the band info"""
    bands = list(band_info["name"].unique())
    metadata.bands = bands

    rows_with_min_max = band_info[band_info["min"].notna() & band_info["max"].notna()]
    bands_with_min_max = list(rows_with_min_max["name"].unique())

    # Add validation if they only provide min or max, but not both for one band.
    rows_with_only_min = band_info[band_info["min"].notna() & band_info["max"].isna()]
    rows_with_only_max = band_info[band_info["min"].isna() & band_info["max"].notna()]
    if len(rows_with_only_min) > 0 or len(rows_with_only_max) > 0:
        raise ValueError(
            "If specifying min and max values for a band, both must always be provided."
        )

    min_max_values: dict[str, tuple[float | None, float | None]] = {}
    for band in bands_with_min_max:
        orig_band_min = band_info[band_info["name"] == band]["min"].min()
        orig_band_max = band_info[band_info["name"] == band]["max"].max()
        try:
            band_min = float(orig_band_min)
            band_max = float(orig_band_max)
        except Exception as e:
            raise ValueError(
                f"Could not convert min or max values ({orig_band_min}, {orig_band_max}"
                f") for band {band} to float: {e}"
            ) from e
        min_max_values[band] = (band_min, band_max)
    metadata.min_maxes_per_band = min_max_values


def _fix_0_to_360_lon(dset: xr.Dataset, degree_tolerance: float = 10) -> xr.Dataset:
    # Consider the dataset 0-360 if min is 0°+-10° and max is 360°+-10°
    if "x" not in dset:
        logger.error("Cannot fix lon values for dataset without x dimension")
        return dset
    x_dim = dset["x"]
    x_range = x_dim.min(), x_dim.max()
    if abs(x_range[0]) > degree_tolerance or abs(360 - x_range[1]) > degree_tolerance:
        return dset
    logger.debug("Fixing lon values for dataset with 0-360 lon range")
    resolution = dset.odc.geobox.resolution.x
    if resolution is None or resolution < 1e-6:
        logger.error("Cannot fix lon values for dataset without x resolution")
        return dset
    roll_distance = int(round(-180 / resolution))
    dset = dset.roll({"x": roll_distance}, roll_coords=False)
    dset["x"] = dset["x"] - 180
    dset = dset.assign_coords(xr_coords(dset.odc.geobox, dims=dset.odc.spatial_dims))
    return dset


def _fix_0_to_180_lat(dset: xr.Dataset, degree_tolerance: float = 10) -> xr.Dataset:
    # Consider the dataset 0-180 if min is 0°+-10° and max is 180°+-10°
    if "y" not in dset:
        logger.error("Cannot fix lat values for dataset without y dimension")
        return dset
    y_dim = dset["y"]
    y_range = y_dim.min(), y_dim.max()
    if abs(y_range[0]) > degree_tolerance or abs(180 - y_range[1]) > degree_tolerance:
        return dset
    logger.debug("Fixing lat values for dataset with 0-180 lat range")
    resolution = dset.odc.geobox.resolution.y
    if resolution is None or resolution < 1e-6:
        logger.error("Cannot fix lat values for dataset without y resolution")
        return dset
    roll_distance = int(round(-90 / resolution))
    dset = dset.roll({"y": roll_distance}, roll_coords=False)
    dset["y"] = dset["y"] - 90
    dset = dset.assign_coords(xr_coords(dset.odc.geobox, dims=dset.odc.spatial_dims))
    return dset


def _repr_fsmap(self: fsspec.FSMap) -> str:
    return cast(str, self.root)


fsspec.FSMap.__repr__ = _repr_fsmap


def _open_single_zarr(
    mapper: fsspec.FSMap,
    rename: dict[str, str] | None = None,
    **kwargs: Any | None,
) -> xr.Dataset:
    # .get_mapper inspired by: https://github.com/fsspec/filesystem_spec/issues/386
    # Try to decode coordinates first, then fall back to default.
    kwargs = copy(kwargs) or {}
    kwargs["decode_coords"] = kwargs.get("decode_coords", "all")

    used_coords_fallback = False
    used_time_fallback = False
    while not all([used_time_fallback, used_coords_fallback]):
        try:
            dset = xr.decode_cf(xr.open_zarr(mapper, **kwargs))
            if rename:
                dset = dset.rename(rename)
            return dset
        except ValueError as e:
            if used_time_fallback or "decode_times=False" not in str(e.args[0]):
                raise
            logger.debug(
                "Failed to decode time coordinates for dataset. "
                "Trying to fallback to decode_times=False"
            )
            kwargs["decode_times"] = False
            used_time_fallback = True
        except AttributeError as e:
            if used_coords_fallback:
                raise
            logger.debug(
                f"Failed to load Zarr dataset with decode_coords=all: {e}. Falling back"
                f" to default."
            )
            kwargs["decode_coords"] = True
            used_coords_fallback = True
    raise RuntimeError(
        f"Failed to open Zarr datasets from {mapper} after using multiple fallbacks. "
    )


def _load_zarr_dataset(
    store: str | Path,
    rename: dict[str, str],
    **kwargs: Any | None,
) -> xr.Dataset:
    kwargs = kwargs or {}

    store, concat_dim_name = parse_dimension_placeholder_path(store)
    storage_options = get_fsspec_storage_options(str(store))

    if concat_dim_name is not None:
        # fsspec glob does not work as documented with paths ending in slashes
        # (supposedly returns only directories, but that seems to be broken in gcs)
        if isinstance(store, str):
            store = store.rstrip("/")
        dsets: list[tuple[str, xr.Dataset]] = []
        errors: list[tuple[str, Exception]] = []
        fs: fsspec.AbstractFileSystem
        fs, _ = fsspec.url_to_fs(store, **storage_options)
        paths = fs.glob(store, maxdepth=1)
        logger.info(
            "Opening {num} Zarrs from {store}",
            num=len(paths),
            store=store,
        )
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for path in paths:
                futures.append(
                    executor.submit(
                        _try_to_open_globbed_zarr,
                        path=path,
                        fs=fs,
                        store=store,
                        rename=rename,
                        kwargs=kwargs,
                        dsets=dsets,
                        errors=errors,
                    )
                )
            concurrent.futures.wait(futures, timeout=120)
        logger.info(
            "Opened {num_ds} Zarrs from {store}",
            num_ds=len(dsets),
            store=store,
        )

        if not dsets:
            if not errors:
                raise NoFilesForGlobError(f"No Zarrs found for glob path {store}")
            errors_str = "\n".join(": ".join(map(str, i)) for i in errors)
            raise NoFilesForGlobError(
                f"Could not open any Zarrs found by glob path {store}. Some failed "
                f"with errors: \n{errors_str}"
            )
        dset = xr.concat((d[1] for d in dsets), dim=concat_dim_name)
        dset = dset.sortby(concat_dim_name)
    else:
        mapper = fsspec.get_mapper(
            glob.escape(str(store)),
            **storage_options,
        )
        dset = _open_single_zarr(mapper, rename=rename, **kwargs)
        dset = _fixup_zarr(dset)

    return dset


def _fixup_zarr(dset: xr.Dataset) -> xr.Dataset:
    crs: CRS | None = CRS(dset.odc.crs) if dset.odc.crs else None
    if crs is None:
        crs = _detect_zarr_crs(dset)

    # Search for common y dimension name among dim names and normalize to y if found
    y_dim_name = find_latitude_dimension(dset) or find_y_dimension(dset)
    if y_dim_name and y_dim_name != "y":
        dset = dset.rename({y_dim_name: "y"})

    # Search among common x dimension name among dim names and normalize to x if found
    x_dim_name = find_longitude_dimension(dset) or find_x_dimension(dset)
    if x_dim_name and x_dim_name != "x":
        dset = dset.rename({x_dim_name: "x"})

    if crs is None:
        logger.warning(
            "No CRS found in Zarr dataset. Guessing based on coordinate ranges."
        )
        crs = _guess_crs_from_coords(dset.x, dset.y)
    dset = dset.odc.assign_crs(crs=crs)

    # detect 0-360 longitude or 0-180 latitude (VIDA)
    if crs.is_geographic:
        dset = _fix_0_to_360_lon(dset)
        dset = _fix_0_to_180_lat(dset)

    if _coordinates_are_top_left(dset):
        dset = _shift_coordinates_from_top_left_to_pixel_center(dset)

    # detect time encoded as small integers (years) and convert to regular time
    if "time" in dset.coords:
        time_coord = dset.coords["time"]
        if np.issubdtype(time_coord.dtype, np.integer):
            max_time: int = time_coord.max().item()
            if max_time < 10_000:
                # These are year numbers, as integers
                time_coord = time_coord.astype(np.uint64)
                time_coord.data[:] = pd.to_datetime(time_coord.data, format="%Y")
                time_coord = time_coord.astype("datetime64[ns]")

                dset.coords["time"] = time_coord
    return dset


def _try_to_open_globbed_zarr(
    path: str | Path,
    fs: fsspec.AbstractFileSystem,
    store: str | Path,
    rename: dict[str, str],
    kwargs: dict[str, Any],
    dsets: list[tuple[str, xr.Dataset]],
    errors: list[tuple[str, Exception]],
) -> None:
    try:
        dsets.append(
            (
                str(path),
                _fixup_zarr(
                    _open_single_zarr(fs.get_mapper(path), rename=rename, **kwargs)
                ),
            )
        )
    except Exception as e:
        errors.append((str(path), e))
        logger.error(
            "Could not open dataset {path} found by glob path "
            "{store} with error: {e}",
            path=path,
            store=store,
            e=e,
        )


def _guess_crs_from_coords(x: np.ndarray[Any, Any], y: np.ndarray[Any, Any]) -> CRS:
    """Guess the CRS based on x/y coordinate ranges.

    VERY rough guess based on coordinate ranges.

    Args:
        x: Array of x coordinates
        y: Array of y coordinates

    Returns:
        Guessed CRS (defaults to EPSG:4326 if unable to determine)

    Common cases:
        - EPSG:4326 (WGS84): x: [-180, 180], y: [-90, 90]
        - EPSG:3857 (Web Mercator): x/y: [-20037508.34, 20037508.34]
    """
    x_min, x_max = float(x.min()), float(x.max())
    y_min, y_max = float(y.min()), float(y.max())

    # Check for WGS84 range first
    if -180 <= x_min <= x_max <= 180 and -90 <= y_min <= y_max <= 90:
        return CRS.from_epsg(4326)

    # Only guess Web Mercator if coordinates are clearly in that range
    # (significantly larger than WGS84 bounds)
    WEB_MERCATOR_BOUND = 20037508.34
    if (
        abs(x_min) > 180
        and abs(x_max) > 180
        and abs(y_min) > 90
        and abs(y_max) > 90
        and abs(x_min) <= WEB_MERCATOR_BOUND
        and abs(x_max) <= WEB_MERCATOR_BOUND
        and abs(y_min) <= WEB_MERCATOR_BOUND
        and abs(y_max) <= WEB_MERCATOR_BOUND
    ):
        return CRS.from_epsg(3857)

    # Default to WGS84 if unable to determine
    logger.warning(
        f"Unable to definitively determine CRS from coordinate ranges: "
        f"x: [{x_min}, {x_max}], y: [{y_min}, {y_max}]. Defaulting to EPSG:4326"
    )
    return CRS.from_epsg(4326)


def _parse_datetime_from_string(
    date_string: str, date_format: str
) -> datetime.datetime:
    # Convert strptime format codes to regex patterns
    format_to_pattern = {
        "%Y": r"\d{4}",
        "%m": r"\d{2}",
        "%d": r"\d{2}",
        "%H": r"\d{2}",
        "%M": r"\d{2}",
        "%S": r"\d{2}",
    }

    # Build regex pattern from date format
    pattern = date_format
    for format_code, regex in format_to_pattern.items():
        pattern = pattern.replace(format_code, f"({regex})")

    # Find matching substring using regex

    match = re.search(pattern, date_string)
    if not match:
        raise ValueError(
            f"Could not find date matching format {date_format} in {date_string}"
        )

    # Extract the matching substring
    date_substring = match.group(0)

    # Parse the date
    date = datetime.datetime.strptime(date_substring, date_format)
    return date


def _load_stac_dataset(  # noqa: C901
    items: list[Item],
    bands: Iterable[str] | None,
    groupby: Groupby | None,
    # Geobox of the full dataset, enabling a subselection of bbox in the same pixel grid
    full_geobox: GeoBox | None = None,
    # BBOX is assumed to be in EPSG:4326
    bbox: BBOX | None = None,
    chunksizes: Chunksizes | None = None,
    band_info: pd.DataFrame | None = None,
    **kwargs: Any | None,
) -> xr.Dataset:
    if chunksizes is None:
        chunksizes = DEFAULT_CHUNKSIZES

    bbox_geobox = None
    if bbox is not None:
        original_items = items
        if full_geobox is None:
            raise ValueError(
                "Cannot provide a bounding box without a full geobox of the dataset"
            )

        # Not 100% sure whether this filtering is strictly necessary, but the time to
        # filter the elements is negligible
        bbox_geometry = box(*bbox)
        original_number_of_items = len(items)
        items = [item for item in items if box(*item.bbox).intersects(bbox_geometry)]

        if len(items) == 0:
            logger.info(
                "After filtering by date and bounding box, no STAC items remain. This"
                "can happen if the underlying items don't fully cover the whole "
                "spatio-temporal extent. We're resetting to using all items to make "
                "sure downstream code works as expected."
            )
            items = original_items
        else:
            logger.debug(
                f"Bounding box filtering reduced the number of items from "
                f"{original_number_of_items} to {len(items)}"
            )

        bbox_geometry = Geometry(box(*bbox), "EPSG:4326")
        bbox_geobox = full_geobox.enclosing(bbox_geometry)
        # When geobox is provided kwargs must not include any other georeferencing
        # arguments
        for arg in _GEOREFERENCING_ARGS:
            if arg in kwargs:
                del kwargs[arg]

    if kwargs is None:
        kwargs = {}

    selected_bands: list[str] | None = None

    # We've had some trouble with datetime serialization, so we're making sure the
    # datetime column is always of the correct type
    if band_info is not None and "datetime" in band_info.columns:
        band_info["datetime"] = pd.to_datetime(band_info["datetime"])

    # The bands will be named `asset.<band_index>` (with 1-indexed band index)
    if band_info is not None and bands is not None:
        rows_for_name = band_info[band_info["name"].isin(bands)]
        selected_bands = [f"asset.{index + 1}" for index in rows_for_name.index]
    elif bands is not None:
        selected_bands = list(bands)

    # We only support TIFF files for now. Some STAC catalogs of interest have
    # non-raster assets such as J2 files so we exclude those.
    filtered_items = []
    for item in items:
        filtered_assets = {
            key: asset
            for key, asset in item.assets.items()
            if asset.media_type and "image/tiff" in asset.media_type.lower()
        }
        if filtered_assets:
            filtered_item = item.clone()
            filtered_item.assets = filtered_assets
            filtered_items.append(filtered_item)

    items = filtered_items
    logger.debug(f"Filtered to {len(items)} items with 'image/tiff' assets")

    # Clearing the `eo:bands.name` property if there are too many bands.
    # We're clearing that to have deterministic band names (`asset.<i>`) in the output
    # dset.
    # Generally, this is not great as we're loosing information present in the STAC
    # items, so we'll need to find a better solution there in the future.
    # Having the eo:bands.name property present does incur a significant performance hit
    # if the dataset has many bands though
    use_asset_based_naming = False
    for item in items:
        new_assets = {}
        for asset_key, asset in item.assets.items():
            if "eo:bands" in asset.extra_fields:
                num_bands = len(asset.extra_fields["eo:bands"])
                use_asset_based_naming = num_bands > MAX_NUM_EO_ASSET_BANDS
                if not use_asset_based_naming:
                    # Use band name as key if available
                    for band in asset.extra_fields["eo:bands"]:
                        if "name" in band:
                            new_assets[band["name"]] = asset
                            break
                    else:
                        # If no band name found, keep original asset key
                        new_assets[asset_key] = asset
                else:
                    new_assets[asset_key] = asset
            else:
                new_assets[asset_key] = asset
        item.assets = new_assets
    if use_asset_based_naming and band_info is not None:
        logger.warning(
            "Using asset-based naming for dataset because it either lacks eo:bands "
            f"metadata or has more than {MAX_NUM_EO_ASSET_BANDS} bands. "
            "Assets will be named `asset.<i>` (1-indexed) instead of `band_name`. "
            "To specify band names, use the `band_info` argument."
        )

    start_time = time.time()

    # Using the first item here to determine the GDAL options, assumes the whole
    # collection is homogeneous
    first_url = next(iter(items[0].assets.values())).href
    gdal_options = get_gdal_options_for_url(first_url)
    odc.stac.configure_rio(**gdal_options)  # type: ignore

    logger.debug(f"odc.stac.load called with {len(items)} items")

    # To make sure all images are put onto the same plane we're using a random string
    # which is guaranteed to not exist in the item's property. The lookup of the string
    # will return None, resulting in all image to be put onto the same plane.
    if groupby == "one_plane":
        groupby = str(uuid.uuid4())
    try:
        dset = odc.stac.load(
            items=items,
            bands=selected_bands,
            groupby=groupby,
            # This will overwrite any other georeferencing settings such as CRS, x/y,
            # etc. Given that we're only doing this for a bounding box of the "original"
            # dataset this should be ok.
            geobox=bbox_geobox,
            chunks=chunksizes,  # type: ignore
            **kwargs,  # type: ignore
        )
    except RasterioIOError as e:
        raise convert_rasterio_to_earthscale(e) from e
    logger.debug(f"odc.stac.load took {time.time() - start_time} seconds")

    # In the case there's only one band, the band name is sometimes "asset" instead of
    # "asset.1". Fixing that here to make sure downstream code works as expected
    if len(dset.data_vars) == 1 and "asset" in dset.data_vars:
        dset = dset.rename_vars({"asset": "asset.1"})

    # At the moment, the downstream code is assuming no band names are present (e.g.
    # through the `eo:bands.name` STAC extension, just making sure that's the case.
    # Without the band names, we're expecting the data vars to be called `asset.<i>`
    # where `i` is the 1-indexed band index.
    if use_asset_based_naming:
        expected_band_name = re.compile(r"asset\.\d")
        for data_var in dset.data_vars:
            data_var = cast(str, data_var)
            if not expected_band_name.match(data_var):
                raise ValueError(
                    f"Found a data variable {data_var} that does not match the"
                    f"expected pattern 'asset.<i>'"
                )

    # If CRS is WGS84, odc will rename to lat/lng but we require x/y
    rename = {}
    if "longitude" in dset.sizes or "longitude" in dset.coords:
        rename["longitude"] = "x"
    if "latitude" in dset.sizes or "latitude" in dset.coords:
        rename["latitude"] = "y"
    dset = dset.rename(rename)

    if band_info is not None:
        dset = reshape_dset_to_band_info(dset, bands, band_info)

    if groupby is not None and "time" in dset.sizes:
        # Making sure time is always a date and not a datetime as we only support
        # dates for now
        times = dset["time"].compute()
        dates = times.dt.date.values
        dset["time"] = [
            datetime.datetime(date.year, date.month, date.day) for date in dates
        ]

    # Transpose back to rioxarray conventions
    if "time" in dset.sizes:
        dset = dset.transpose("time", "y", "x", ...)
    else:
        dset = dset.transpose("y", "x", ...)

    # If all dates are equal to _DEFAULT_TIMESTAMP, we assume no time information
    # has been passed in
    if "time" in dset.sizes:
        dset_times = dset["time"].values
        if len(dset_times) == 1 and dset_times[0] == np.datetime64(_DEFAULT_DATETIME):
            dset = dset.isel(time=0)

    return dset


# Copied from rio-stac
# https://github.com/developmentseed/rio-stac/blob/52a13eec0c8ad19dee904b2bc0cd529b73b95899/rio_stac/stac.py#
# but removed stats creation for performance reasons as it takes too long for rasters
# with a lot of bands and we don't use it yet
def _get_raster_info(src_dst: DatasetReader) -> list[dict[str, Any]]:
    """Get raster metadata.

    see: https://github.com/stac-extensions/raster#raster-band-object

    """
    meta: list[dict[str, Any]] = []

    area_or_point = src_dst.tags().get("AREA_OR_POINT", "").lower()

    # Missing `bits_per_sample` and `spatial_resolution`
    for band in src_dst.indexes:
        value = {
            "data_type": src_dst.dtypes[band - 1],
            "scale": src_dst.scales[band - 1],
            "offset": src_dst.offsets[band - 1],
        }
        if area_or_point:
            value["sampling"] = area_or_point

        # If the Nodata is not set we don't forward it.
        if src_dst.nodata is not None:
            if np.isnan(src_dst.nodata):
                value["nodata"] = "nan"
            elif np.isposinf(src_dst.nodata):
                value["nodata"] = "inf"
            elif np.isneginf(src_dst.nodata):
                value["nodata"] = "-inf"
            else:
                value["nodata"] = src_dst.nodata

        if src_dst.units[band - 1] is not None:
            value["unit"] = src_dst.units[band - 1]

        meta.append(value)

    return meta


def get_band_key(name: str, datetime_: datetime.datetime) -> str:
    return f"{name}-{datetime_.isoformat()}"


def reshape_dset_to_band_info(
    dset: xr.Dataset,
    bands: Iterable[str] | None,
    band_info: pd.DataFrame,
) -> xr.Dataset:
    """
    ODC STAC output dataset originally has one data variable per datetime+band.
    This function reshapes it to have one data variable per band, with
    datetimes as coordinates.
    """
    dataarrays_per_band = defaultdict(list)

    relevant_band_info = band_info
    if bands is not None:
        relevant_band_info = band_info[band_info["name"].isin(bands)]

    if "datetime" in relevant_band_info.columns:
        for row_index, row in relevant_band_info.iterrows():
            if not isinstance(row_index, int):
                raise ValueError(
                    "The index of the band info dataframe must be an integer"
                )
            # Band names will be `asset.<i>` (1-indexed)
            current_band_name = f"asset.{row_index + 1}"
            new_band_name = row["name"]
            dataarray = (
                dset[current_band_name]
                .squeeze()
                .expand_dims({"time": [row["datetime"]]})
            )
            dataarrays_per_band[new_band_name].append(dataarray)
        # Concatenate all DataArrays along the time dimension
        concatenated_dataarrays = {
            band_name: xr.concat(dataarrays, dim="time")
            for band_name, dataarrays in dataarrays_per_band.items()
        }
        # convert back to Dataset
        new_dset = xr.Dataset(concatenated_dataarrays)
    else:
        rename_dict = {
            f"asset.{cast(int, i) + 1}": row["name"]
            for i, row in relevant_band_info.iterrows()
        }
        new_dset = dset.rename_vars(rename_dict)

    return new_dset


def _create_stac_item_from_one_url(
    ds: DatasetReader,
    datetime_: datetime.datetime | None,
    properties: dict[str, Any] | None,
) -> Item:
    raster_bands = _get_raster_info(ds)

    item: Item = create_stac_item(
        ds,
        input_datetime=datetime_,
        with_proj=True,
        # We are not adding the `eo` extension as that adds a significant overhead to
        # `odc.stac.load`
        with_eo=False,
        properties=properties,
    )
    item.stac_extensions.append(
        f"https://stac-extensions.github.io/raster/{RASTER_EXT_VERSION}/schema.json",
    )
    assert len(item.assets) == 1
    first_asset = next(iter(item.assets.values()))
    first_asset.extra_fields["raster:bands"] = raster_bands
    first_asset.media_type = "image/tiff"
    props = item.properties
    if (
        props.get("proj:epsg") is None
        and props.get("proj:wkt2") is None
        and props.get("projjson") is None
    ):
        detected_crs = detect_crs_from_cf_convention_tags(ds.tags())
        if detected_crs is None:
            raise ValueError(
                "Could not detect the CRS of the dataset. Please make sure that "
                "gdalinfo outputs a valid CRS for this dataset or contact us if you "
                "think we should be able to detect it automatically."
            )
        props["proj:wkt2"] = detected_crs.to_wkt()
    if item.datetime is None or item.datetime == datetime.datetime(
        1970, 1, 1, tzinfo=datetime.timezone.utc
    ):
        detected_datetime = detect_datetime_from_cf_convention_tags(ds.tags())
        if detected_datetime is not None:
            item.datetime = detected_datetime
    return item


def _get_datetime_and_properties_for_url(
    url: str,
    datetime_: datetime.datetime | tuple[datetime.datetime, datetime.datetime] | None,
    filename_date_pattern: str | None,
    band_info: pd.DataFrame | None,
) -> tuple[datetime.datetime | None, dict[str, Any]]:
    """
    Get the datetime and start/end datetime Item properties for a given URL.
    """
    final_datetime = None
    datetime_props = {}

    if isinstance(datetime_, datetime.datetime):
        final_datetime = datetime_
    elif isinstance(datetime_, tuple):
        datetime_props["start_datetime"] = datetime_[0].isoformat()
        datetime_props["end_datetime"] = datetime_[1].isoformat()
        final_datetime = None
    elif filename_date_pattern is not None:
        try:
            final_datetime = _parse_datetime_from_string(url, filename_date_pattern)
        except ValueError as e:
            logger.error(f"Failed to parse datetime from asset {url}: {e}")
            raise e
    elif band_info is not None and "datetime" in band_info.columns:
        min_datetime = band_info["datetime"].min()
        max_datetime = band_info["datetime"].max()
        datetime_props["start_datetime"] = min_datetime.isoformat()
        datetime_props["end_datetime"] = max_datetime.isoformat()
        final_datetime = None
    else:
        final_datetime = _DEFAULT_DATETIME

    return final_datetime, datetime_props


def _create_stac_items_from_urls(
    urls: list[str],
    datetime_: datetime.datetime | tuple[datetime.datetime, datetime.datetime] | None,
    filename_date_pattern: str | None,
    band_info: pd.DataFrame | None,
    filename_band_pattern: list[FilenameBandPattern] | None,
) -> list[Item]:
    # In the case no time information is provided, we default to the Unix epoch.
    # The time information will be set by the bands on the outside.
    if datetime_ is None and filename_date_pattern is None:
        datetime_ = _DEFAULT_DATETIME

    properties = {}
    if isinstance(datetime_, tuple):
        properties["start_datetime"] = datetime_[0].isoformat()
        properties["end_datetime"] = datetime_[1].isoformat()
        datetime_ = None

    def process_url(
        url: str,
    ) -> Item:
        url_properties = deepcopy(properties)
        url_datetime, datetime_props = _get_datetime_and_properties_for_url(
            url, datetime_, filename_date_pattern, band_info
        )
        url_properties.update(datetime_props)

        gdal_options = get_gdal_options_for_url(url)
        try:
            with rasterio.Env(**gdal_options), rasterio.open(url, "r") as ds:
                item = _create_stac_item_from_one_url(ds, url_datetime, properties)
                if filename_band_pattern is not None:
                    # We sort the patterns by length to ensure we match the most
                    # specific pattern first.
                    sorted_patterns = sorted(
                        filename_band_pattern,
                        key=lambda pattern_and_band: len(pattern_and_band.pattern),
                        reverse=True,
                    )
                    for band_pattern in sorted_patterns:
                        pattern = band_pattern.pattern.lower()
                        band = band_pattern.band
                        if fnmatch.fnmatch(url.lower(), pattern):
                            # Get the first (and only) asset
                            asset = next(iter(item.assets.values()))

                            # Create new assets dict with band name as key
                            new_assets = {band: asset}

                            # Replace the assets dict
                            item.assets = new_assets
                            break
                return item
        except RasterioIOError as e:
            if "GS_SECRET_ACCESS_KEY" in e.args[0]:
                logger.error(
                    f"Error opening {url}. Do you have the correct credentials"
                    " to access this dataset?"
                )
            raise e

    logger.info(f"Processing {len(urls)} URLs")

    with ThreadPoolExecutor(max_workers=128) as executor:
        items = list(executor.map(lambda url: process_url(url), urls))
    return items


def _validate_band_info_dataframe(df: pd.DataFrame) -> None:
    """
    Validate the band info dataframe
    """
    required_columns = {"name"}
    optional_columns = {"min", "max", "datetime"}
    if not required_columns.issubset(df.columns.tolist()):
        raise ValueError(
            f"Band info dataframe must have the following columns: {required_columns}"
        )
    has_extra_columns = set(df.columns.tolist()) - required_columns - optional_columns
    if has_extra_columns:
        raise ValueError(
            f"Band info dataframe has the following extra columns: {has_extra_columns}"
        )

    if "datetime" in df.columns:
        # Check that across each band name, the set of datetimes is the same
        unique_datetimes_per_band = df.groupby("name")["datetime"].unique()
        unique_datetimes = unique_datetimes_per_band.iloc[0]
        for band, datetimes in unique_datetimes_per_band.items():
            if not np.array_equal(unique_datetimes, datetimes):
                raise ValueError(
                    f"Band {band} has different datetimes than the first band. "
                    f"All bands must have the same set of datetimes."
                )


def _get_crs_from_ee_image(image: ee.Image) -> CRS:
    projection = image.projection().getInfo()
    return _get_crs_from_ee_projection(projection)


def _get_crs_from_ee_projection(projection: dict[str, Any]) -> CRS:
    if "crs" in projection:
        crs = crs_from_str(projection["crs"])
    elif "wkt" in projection:
        crs = CRS.from_string(projection["wkt"])
    else:
        raise ValueError("Could not determine CRS from EE image")
    return crs


def _get_approx_m_per_pixel_at_point(
    crs: CRS, crs_transform: Affine, point_4326: tuple[float, float]
) -> float:
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


def _load_geobox_from_ee_image_collection(
    image_collection: ee.ImageCollection,
) -> GeoBox:
    error_margin_meters = 0.5
    error_margin = ee.ErrorMargin(error_margin_meters, "meters")
    limit = 10_000
    number_of_images = image_collection.limit(limit).size().getInfo()

    # We return all of our geoboxes as WGS84
    crs_4326 = CRS.from_string("EPSG:4326")
    first_image = image_collection.first()
    # In case we've got exactly one image, we can perfectly reconstruct the geobox
    if number_of_images == 1:
        bbox = Polygon(
            first_image.geometry(error_margin)
            .bounds(error_margin)
            .getInfo()["coordinates"][0]
        ).bounds
    # In case we've got <10_000 images in the collection, we can still compute the
    # bounds and the merged CRS will be WGS84. 10_000 here was determined empirically.
    # If the number is too high, `.geometry()` will fail due to a memory error on EE.
    # We'll get the resolution from the first image, assuming all other images have
    # the same
    elif number_of_images < limit:
        bbox = Polygon(
            image_collection.geometry(error_margin)
            .bounds(error_margin)
            .getInfo()["coordinates"][0]
        ).bounds
    # If both of the above fail, we fall back to a "whole world geobox" using the
    # resolution of the first image
    else:
        logger.warning(
            "The provided EE image collection is too large to compute the geobox. "
            "Falling back to a whole world bounding box"
        )
        bbox = (-180, -90, 180, 90)

    highest_res_band = find_ee_image_highest_resolution_from_bands(first_image, bbox)
    if highest_res_band is None:
        raise ValueError("First image has no bands, cannot determine geobox")
    resolution_m = highest_res_band[-1]
    resolution_4326 = resolution_m / METERS_PER_DEGREE
    geobox = GeoBox.from_bbox(
        bbox=bbox, crs=crs_4326, resolution=Resolution(resolution_4326)
    )
    return geobox


def find_ee_image_highest_resolution_from_bands(
    image: ee.Image,
    image_bbox_4326: tuple[float, float, float, float],
) -> tuple[str, CRS, Affine, float] | None:
    """
    Returns band_name, crs, affine, and meters_per_pixel of the band with the highest
    resolution.
    """
    image_center_4326 = (
        (image_bbox_4326[0] + image_bbox_4326[2]) / 2,
        (image_bbox_4326[1] + image_bbox_4326[3]) / 2,
    )
    band_metadata = image.getInfo()["bands"]
    if not band_metadata:
        return None

    bands_with_crs_and_res: list[tuple[str, CRS, Affine, float]] = []

    for band_meta in band_metadata:
        band_crs = _get_crs_from_ee_projection(band_meta)
        band_transform = Affine(*band_meta["crs_transform"])
        meters_per_pixel = _get_approx_m_per_pixel_at_point(
            band_crs, band_transform, image_center_4326
        )
        bands_with_crs_and_res.append(
            (band_meta["id"], band_crs, band_transform, meters_per_pixel)
        )
    return min(bands_with_crs_and_res, key=lambda x: x[-1])


# Separate function to help with debugging
def _fail_when_loading_ee() -> xr.Dataset:
    raise CannotConvertEarthEngineToXarrayError(
        "Due to limitations in the metadata that Earth Engine provides on "
        "ImageCollections, we cannot load this dataset as an xarray Dataset."
    )


class EarthEngineDatasetDefinition(DatasetDefinition):
    # JSON serialized version of the ee.ImageCollection object
    image_collection: dict[str, Any]
    quality_band: str | None
    viz_params: dict[str, Any] | None


CallableT = TypeVar("CallableT", bound=Callable[..., Any])


def wrap_known_earthengine_errors(func: CallableT) -> CallableT:
    @functools.wraps(func)
    def _wrap(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ee.EEException as e:
            if len(e.args) > 0 and "Image.projection" in e.args[0]:
                raise UnsupportedRasterFormatError(*e.args) from None
            raise e

    return cast(CallableT, _wrap)


def _convert_ee_viz_params(ee_viz: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for key, value in ee_viz.items():
        if isinstance(value, list):
            result[key] = ",".join(map(str, value))
        else:
            result[key] = str(value)
    return result


class EarthEngineDataset(RasterDataset[EarthEngineDatasetDefinition]):
    """
    Load data from Earth Engine.

    Args:
        image_collection:
            Either an ee.ImageCollection object or JSON dict of the image collection
        quality_band:
            The band used to determine the pixel ordering in the mosaic creation. Please
            refer to the [Earth-engine docs](https://developers.google.com/earth-engine/apidocs/ee-imagecollection-qualitymosaic)
            for an example.
        viz_params:
            Visualization parameters for the mosaic. Please refer to the docs on
            [Image Visualization](https://developers.google.com/earth-engine/guides/image_visualization)
            on what's possible here.

            An example here would be:
            ```python
            viz_params = {
                "bands": ["B4", "B3", "B2"],
                "min": [0, 0, 0],
                "max": [0.3, 0.3, 0.3]
            }
            ```

        name:
            The name of the dataset. Defaults to a random UUID. If explicitly given, the
            dataset will be visible in the Earthscale platform.
    """

    @staticmethod
    def fetch_earth_engine_catalog_stac(earth_engine_id: str) -> dict[str, Any] | None:
        base_url = "https://storage.googleapis.com/earthengine-stac/catalog/"
        if earth_engine_id.startswith("projects"):
            base_catalog = earth_engine_id.split("/")[1]
        else:
            base_catalog = earth_engine_id.split("/")[0]
        escaped_name = earth_engine_id.replace("/", "_")
        url = f"{base_url}{base_catalog}/{escaped_name}.json"

        with requests.get(url) as response:
            if response.status_code != 200:
                logger.warning(
                    "Failed to fetch Earth Engine catalog STAC for id "
                    "'{earth_engine_id}' from URL {url}. Status code: {status_code}",
                    earth_engine_id,
                    url,
                    response.status_code,
                )
                return None
            return cast(dict[str, Any], response.json())

    @staticmethod
    def from_earth_engine_catalog(
        earth_engine_id: str,
        custom_name: str | None = None,
        preprocessing_function: Callable[
            [ee.ImageCollection, DatasetMetadata], ee.ImageCollection
        ]
        | None = None,
    ) -> "EarthEngineDataset":
        """
        Load an Earth Engine dataset from the Earth Engine catalog.

        The id can be found in the "Collection Snippet" field.
        Example value: "COPERNICUS/DEM/GLO30"

        """
        ds_stac = EarthEngineDataset.fetch_earth_engine_catalog_stac(earth_engine_id)
        if ds_stac is None:
            raise ValueError(
                "Could not fetch Earth Engine catalog STAC, check if the "
                "given ID '{earth_engine_id}' exists"
            )

        ee_type = ds_stac.get("gee:type")
        if not ee_type:
            raise ValueError("Could not determine the type of the Earth Engine dataset")

        if ee_type == "image":
            ee_coll = ee.ImageCollection([ee.Image(earth_engine_id)])
        elif ee_type == "image_collection":
            ee_coll = ee.ImageCollection(earth_engine_id)
        else:
            raise ValueError(f"Dataset has unsupported type: {ee_type}")

        metadata = parse_earth_engine_stac_to_earthscale(ds_stac)
        if preprocessing_function is not None:
            ee_coll = preprocessing_function(ee_coll, metadata)

        return EarthEngineDataset(
            image_collection=ee_coll,
            name=earth_engine_id if custom_name is None else custom_name,
            metadata=metadata,
        )

    @wrap_known_earthengine_errors
    def __init__(
        self,
        image_collection: ee.ImageCollection | dict[str, Any],
        quality_band: str | None = None,
        viz_params: dict[str, Any] | None = None,
        attributes: dict[str, str] | None = None,
        name: str | None = None,
        metadata: DatasetMetadata | None = None,
        dataset_id: uuid.UUID | None = None,
        dataset_version_id: uuid.UUID | None = None,
    ):
        if isinstance(image_collection, dict):
            image_collection = ee.ImageCollection(
                ee.deserializer.decode(image_collection)
            )
        if image_collection.limit(1).size().getInfo() == 0:
            raise ValueError("The provided image collection is empty")
        explicit_name = name is not None
        name = name or str(uuid.uuid4())

        definition = EarthEngineDatasetDefinition(
            image_collection=ee.serializer.encode(image_collection),
            quality_band=quality_band,
            viz_params=viz_params,
        )

        self.quality_band = quality_band

        if quality_band is None:
            image = image_collection.mosaic()
        else:
            image = image_collection.qualityMosaic(quality_band)

        self.image = image
        self.image_collection = image_collection

        # TODO: remove these?
        if viz_params is None:
            viz_params = {}
        else:
            # Earthengine expects viz params to be a comma-separated string
            viz_params = {
                k: ",".join(map(str, v)) if isinstance(v, list) else str(v)
                for k, v in viz_params.items()
            }
        self.viz_params = viz_params

        if metadata is None:
            metadata = DatasetMetadata()
        metadata.supports_custom_viz = False

        @wrap_known_earthengine_errors
        def _load_geobox() -> GeoBox:
            logger.info(
                "Loading geobox from Earth Engine for dataset "
                "{dataset_id} ({dataset_name}) ee_id: {earth_engine_id}",
                dataset_id=dataset_id,
                dataset_name=name,
                earth_engine_id=metadata.source_id,
            )
            return _load_geobox_from_ee_image_collection(image_collection)

        super().__init__(
            name=name,
            explicit_name=explicit_name,
            attributes=attributes,
            graph=create_source_graph(
                f"load_earthengine_dataset_{name}",
                name,
                metadata,
                lambda bbox, bands_selection, chunksizes: _fail_when_loading_ee(),
            ),
            metadata=metadata,
            definition=definition,
            geobox_callback=_load_geobox,
            dataset_id=dataset_id,
            dataset_version_id=dataset_version_id,
        )

    def get_filtered_collection(
        self,
        start_time: datetime.datetime | None = None,
        end_time: datetime.datetime | None = None,
        geometry: ee.Geometry | None = None,
    ) -> ee.ImageCollection:
        coll = self.image_collection
        if start_time is not None or end_time is not None:
            if start_time is None and end_time is not None:
                start_time = end_time - datetime.timedelta(milliseconds=1)
            if end_time is None and start_time is not None:
                end_time = start_time + datetime.timedelta(milliseconds=1)
            coll = coll.filter(
                ee.Filter.date(
                    ee.Date(start_time),
                    ee.Date(end_time),
                )
            )
        if geometry is not None:
            coll = coll.filterBounds(geometry)
        return coll

    def get_mosaic(
        self,
        start_time: datetime.datetime | None = None,
        end_time: datetime.datetime | None = None,
    ) -> ee.Image | None:
        coll = self.get_filtered_collection(start_time, end_time)
        # check if the collection is empty after filtering
        # -> in this case we cannot create a map and have to return None
        if coll.limit(1).size().getInfo() == 0:
            return None

        if self.quality_band is None or self.quality_band not in self.metadata.bands:
            image = coll.mosaic()
        else:
            image = coll.qualityMosaic(self.quality_band)
        return image

    def get_tileserver_url(
        self,
        ee_viz_params: dict[str, Any] | None = None,
        start_time: datetime.datetime | None = None,
        end_time: datetime.datetime | None = None,
    ) -> str | None:
        image = self.get_mosaic(start_time, end_time)
        if image is None:
            return None

        get_map_id_params = {"image": image}
        if ee_viz_params is not None:
            get_map_id_params |= _convert_ee_viz_params(ee_viz_params)

        url = cast(
            str,
            ee.data.getMapId(get_map_id_params)["tile_fetcher"].url_format,
        )
        return url

    def get_dimension_info(self) -> DimensionInfo:
        """
        Auto-guesses useful dates from the time range of the metadata.

        Logic:
        if we have > 10 years, use years,
        if we just have one year, use months,
        if we have less than half a year use weeks
        if we have less than a month use days

        TODO: figure out how temporal_resolution should play into this
        """
        meta: DatasetMetadata = self.metadata
        if meta.temporal_extent is None:
            return DimensionInfo(dimensions=[], band_dimensions=[])
        start, end = meta.temporal_extent
        times = generate_filter_date_range(start, end)
        dim = Dimension(name="time", values=times)
        band_dimensions = [
            BandDimensions(band_name=band, dimension_names=["time"])
            for band in meta.bands
        ]
        return DimensionInfo(dimensions=[dim], band_dimensions=band_dimensions)

    @staticmethod
    def load_visualizations_from_stac(earth_engine_id: str) -> dict[str, Any]:
        ds_stac = EarthEngineDataset.fetch_earth_engine_catalog_stac(earth_engine_id)

        visualizations: dict[str, Any] = {}
        if ds_stac is None:
            logger.warning(
                "Could not fetch Earth Engine catalog STAC for dataset "
                f"with Earth Engine ID '{earth_engine_id}'"
            )
            return visualizations
        try:
            ee_visualizations = ds_stac["summaries"]["gee:visualizations"]
            for vis in ee_visualizations:
                # just skip the ones we cannot support for now
                with suppress(KeyError):
                    vis_name = vis["display_name"]
                    visualizations[vis_name] = vis["image_visualization"]["band_vis"]
        except KeyError:
            logger.warning(
                "Could not find visualizations in Earth Engine catalog for dataset "
                f"with Earth Engine ID '{earth_engine_id}'"
            )
        return visualizations


class TileServerDatasetDefinition(DatasetDefinition):
    url: str


class TileServerDataset(RasterDataset[TileServerDatasetDefinition]):
    """
    Load data from a tile server.

    Args:
        url (str): The URL of the tile server with x, y, z placeholders, e.g.
            `https://server.com/tiles/{z}/{x}/{y}.png`.
        name (str, optional): The name of the dataset. Defaults to a random UUID.
            If explicitly given, the dataset will be visible in the Earthscale platform.
    """

    def __init__(
        self,
        url: str,
        name: str | None = None,
        attributes: dict[str, str] | None = None,
        metadata: DatasetMetadata | None = None,
        definition: TileServerDatasetDefinition | None = None,
        dataset_id: uuid.UUID | None = None,
        dataset_version_id: uuid.UUID | None = None,
    ):
        explicit_name = name is not None
        name = name or str(uuid.uuid4())

        definition = definition or TileServerDatasetDefinition(url=url)

        if metadata is None:
            metadata = DatasetMetadata()
        metadata.tileserver_url = url
        metadata.supports_custom_viz = False

        super().__init__(
            name=name,
            explicit_name=explicit_name,
            attributes=attributes,
            graph=create_source_graph(
                f"load_tileserver_dataset_{name}",
                name,
                metadata,
                self._load,
            ),
            metadata=metadata,
            geobox_callback=self._geobox_callback,
            definition=definition,
            dataset_id=dataset_id,
            dataset_version_id=dataset_version_id,
        )

    def _load(
        self,
        bbox: BBOX | None,
        bands: Iterable[str] | None,
        chunksizes: Chunksizes | None,
    ) -> xr.Dataset:
        # Define the bounds, either from bbox or default to global extent
        if bbox is not None:
            # bbox is in (left, bottom, right, top) in WGS84
            left, bottom, right, top = bbox
        else:
            # Default to global extent in WGS84
            left, bottom, right, top = (-180, -85.0511, 180, 85.0511)

        # Fetch the image
        img, extent = ctx.bounds2img(
            left,
            bottom,
            right,
            top,
            ll=True,
            zoom="auto",
            source=self.definition.url,
        )

        # img is an array of shape (height, width, bands)
        # extent is (left, bottom, right, top) in Web Mercator (EPSG:3857)

        # Create coordinates
        x = np.linspace(extent[0], extent[1], img.shape[1])
        y = np.linspace(extent[3], extent[2], img.shape[0])

        # Create dataset with x and y coordinates
        dset = xr.Dataset(
            coords={
                "x": ("x", x),
                "y": ("y", y),
            }
        )

        # Set band names and create data variables
        num_bands = img.shape[2]
        if num_bands == 3:
            band_names = ["red", "green", "blue"]
        elif num_bands == 4:
            band_names = ["red", "green", "blue", "alpha"]
        else:
            band_names = [f"band_{i + 1}" for i in range(num_bands)]

        for i, band_name in enumerate(band_names):
            dset[band_name] = xr.DataArray(
                img[:, :, i],
                dims=("y", "x"),
                coords={"x": x, "y": y},
            )

        # Set CRS
        dset.rio.write_crs("EPSG:3857", inplace=True)

        if bands is not None:
            dset = dset[bands]

        return dset

    def _geobox_callback(self) -> GeoBox:
        # Default to global extent in Web Mercator (EPSG:3857)
        left, bottom, right, top = (
            -20037508.34,
            -20037508.34,
            20037508.34,
            20037508.34,
        )
        width, height = 256, 256  # Default tile size
        crs = "EPSG:3857"

        transform = from_bounds(
            west=left,
            south=bottom,
            east=right,
            north=top,
            width=width,
            height=height,
        )
        geobox = GeoBox((height, width), transform, crs)
        return geobox

    def get_dimension_info(self) -> DimensionInfo:
        return DimensionInfo(dimensions=[], band_dimensions=[])


registry.register_class("ZarrDataset", ZarrDataset)
registry.register_class("STACDataset", STACDataset)
registry.register_class("ImageDataset", ImageDataset)
registry.register_class("EarthEngineDataset", EarthEngineDataset)
registry.register_class("TileServerDataset", TileServerDataset)
