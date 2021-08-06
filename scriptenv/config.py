"""configuration for scriptenv"""

import os
from dataclasses import dataclass, field
from pathlib import Path

import appdirs


@dataclass(frozen=True)
class Config:
    """Configures a ScriptEnv"""

    cache_path: Path = field(
        default_factory=lambda: Path(
            os.environ.get("SCRIPTENV_CACHE_PATH")
            or appdirs.user_cache_dir("scriptenv")
        )
    )
