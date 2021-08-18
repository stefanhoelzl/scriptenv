"""configuration for scriptenv"""

import os
from dataclasses import dataclass, field
from pathlib import Path

import appdirs


@dataclass(frozen=True)
class Config:
    """Holds scriptenv config values."""

    cache_path: Path = field(
        default_factory=lambda: Path(
            os.environ.get("SCRIPTENV_CACHE_PATH")
            or appdirs.user_cache_dir("scriptenv")
        )
    )
    use_lockfile: bool = field(
        default_factory=lambda: os.environ.get("SCRIPTENV_USE_LOCKFILE") != "false"
    )
