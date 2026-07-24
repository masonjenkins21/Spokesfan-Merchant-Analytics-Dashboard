"""Validation helpers for pipeline inputs and generated dashboard files."""

from pathlib import Path
from collections.abc import Iterable

import pandas as pd


class PipelineValidationError(ValueError):
    """Raised when a required pipeline file or column is missing."""


def require_file(path: Path) -> Path:
    """Return *path* when it exists, otherwise raise a clear error."""
    if not path.is_file():
        raise PipelineValidationError(f"Required file not found: {path}")
    return path


def require_columns(df: pd.DataFrame, columns: Iterable[str], source: str) -> None:
    """Validate that a DataFrame contains all required columns."""
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise PipelineValidationError(
            f"{source} is missing required columns: {', '.join(missing)}"
        )
