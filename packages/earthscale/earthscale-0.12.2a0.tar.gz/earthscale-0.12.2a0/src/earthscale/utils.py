import datetime
import os
import re
from collections.abc import Generator
from contextlib import contextmanager
from enum import Enum, auto
from pathlib import Path
from typing import cast
from urllib.parse import parse_qs, urlparse

import pandas as pd


@contextmanager
def disabled_registration_callbacks() -> Generator[None, None, None]:
    """Context manager that temporarily disables dataset registration callbacks.

    This is useful when you want to prevent automatic registration of datasets,
    for example during dataset loading or copying operations.

    Example:
        ```python
        with disabled_registration_callbacks():
            dataset = Dataset.load(name="my_dataset")
        ```
    """
    from earthscale.datasets.dataset import Dataset

    original_callbacks = Dataset._DATASET_CREATION_CALLBACKS
    Dataset._DATASET_CREATION_CALLBACKS = []
    try:
        yield
    finally:
        Dataset._DATASET_CREATION_CALLBACKS = original_callbacks


def running_in_notebook() -> bool:
    try:
        from IPython import get_ipython  # type: ignore

        if get_ipython() is None:  # type: ignore
            return False
        return True
    except ImportError:
        return False


def create_valid_url(url: str) -> str:
    if is_google_drive_url(url):
        parsed = urlparse(url)
        query = parsed.query
        query_parameters = parse_qs(query)
        query_parameters["supportsAllDrives"] = ["true"]
        query_parameters["alt"] = ["media"]
        query = "&".join(f"{key}={value[0]}" for key, value in query_parameters.items())
        url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query}"
    return url


def running_on_cloud_run() -> bool:
    return "K_SERVICE" in os.environ


def running_on_gke() -> bool:
    return "KUBERNETES_SERVICE_HOST" in os.environ


def running_on_gce() -> bool:
    try:
        import requests

        response = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/instance",
            headers={"Metadata-Flavor": "Google"},
            timeout=1,
        )
        return response.status_code == 200
    except Exception:
        return False


class HostingEnvironment(Enum):
    GOOGLE_CLOUD_RUN = auto()
    GOOGLE_COMPUTE_ENGINE = auto()
    GOOGLE_KUBERNETES = auto()
    UNKNOWN = auto()


def detect_hosting_environment() -> HostingEnvironment:
    if running_on_gke():
        return HostingEnvironment.GOOGLE_KUBERNETES
    if running_on_cloud_run():
        return HostingEnvironment.GOOGLE_CLOUD_RUN
    if running_on_gce():
        return HostingEnvironment.GOOGLE_COMPUTE_ENGINE

    return HostingEnvironment.UNKNOWN


def in_test_run() -> bool:
    return "PYTEST_VERSION" in os.environ


def is_google_drive_url(url: str) -> bool:
    return "googleapis.com/drive" in url


def is_gcs_url(url: str) -> bool:
    return url.startswith("gs://")


def generate_filter_date_range(
    start: datetime.datetime, end: datetime.datetime
) -> list[datetime.datetime]:
    """
    Generate a list of dates between start and end, with a frequency that depends on the
    length of the date range such that the dates are not too dense or too sparse.
    """
    delta = end - start
    if delta.days > 365:
        dates = (
            pd.date_range(
                start=pd.Timestamp(start) - pd.DateOffset(years=1),
                end=pd.Timestamp(end) + pd.DateOffset(years=1),
                freq="YS",
                inclusive="right",
            )
            .to_pydatetime()
            .tolist()
        )
    elif delta.days >= 365:
        dates = (
            pd.date_range(
                start=pd.Timestamp(start) - pd.DateOffset(months=1),
                end=pd.Timestamp(end) + pd.DateOffset(months=1),
                freq="MS",
                inclusive="right",
            )
            .to_pydatetime()
            .tolist()
        )
    elif delta.days >= 30:
        dates = (
            pd.date_range(
                start=pd.Timestamp(start) - pd.DateOffset(weeks=1),
                end=pd.Timestamp(end) + pd.DateOffset(weeks=1),
                freq="W-MON",
                inclusive="right",
            )
            .to_pydatetime()
            .tolist()
        )
    else:
        dates = (
            pd.date_range(
                start=pd.Timestamp(start) - pd.DateOffset(days=1),
                end=pd.Timestamp(end) + pd.DateOffset(days=1),
                freq="D",
                inclusive="right",
            )
            .to_pydatetime()
            .tolist()
        )
    return cast(list[datetime.datetime], dates)


def parse_dimension_placeholder_path(
    path_with_placeholder: str | Path,
) -> tuple[str | Path, str | None]:
    """
    Parses the dimension placeholder in the given path and replaces it with a * glob
    if valid.

    Validates that:
    - There is at most one {name} placeholder.
    - Closing and opening curly braces match.
    - The name is [A-Za-z0-9_-].

    Exceptions:
        ValueError: If the placeholder format is invalid.
    """
    was_path = isinstance(path_with_placeholder, Path)
    path_with_placeholder = str(path_with_placeholder)

    opening_count = path_with_placeholder.count("{")
    if opening_count > 1:
        raise ValueError(
            f"Only one {{dimension_name}} placeholder is allowed in the store "
            f"path, got {opening_count}"
        )
    closing_count = path_with_placeholder.count("}")
    if opening_count != closing_count:
        raise ValueError(
            f"Closing and opening curly braces do not match in the store path: "
            f"{path_with_placeholder}"
        )
    if opening_count == 0:
        return path_with_placeholder, None

    opening_pos = path_with_placeholder.find("{")
    closing_pos = path_with_placeholder.find("}")

    if closing_pos < opening_pos:
        raise ValueError(
            "Closing curly braces must be after opening curly brace in the store path: "
            f"{path_with_placeholder}"
        )

    dimension_name = path_with_placeholder[opening_pos + 1 : closing_pos]
    if not re.match(r"^[A-Za-z0-9_-]+$", dimension_name):
        raise ValueError(
            f"Dimension name must be [A-Za-z0-9_-], got '{dimension_name}' in the store"
            f" path: {path_with_placeholder}"
        )

    replaced_path = (
        path_with_placeholder[:opening_pos]
        + "*"
        + path_with_placeholder[closing_pos + 1 :]
    )
    return Path(replaced_path) if was_path else replaced_path, dimension_name
