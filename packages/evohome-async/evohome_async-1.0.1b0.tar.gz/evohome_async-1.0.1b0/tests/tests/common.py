"""Tests for evohome-async - helper functions."""

from __future__ import annotations

import inspect
import json
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    import voluptuous as vol


def assert_schema(folder: Path, schema: vol.Schema, file_name: str) -> None:
    if not Path(folder).joinpath(file_name).is_file():
        pytest.skip(f"No {file_name} in: {folder.name}")

    with Path(folder).joinpath(file_name).open() as f:
        data: dict[str, Any] = json.load(f)  # is camelCase, as per vendor's schema

    _ = schema(data)


def get_property_methods(obj: object) -> list[str]:
    """Return a list of property methods of an object."""
    return [
        name
        for name, value in inspect.getmembers(obj.__class__)
        if isinstance(value, property | cached_property)
    ]
