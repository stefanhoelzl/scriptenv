"""configuration for scriptenv"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, TypeVar

import appdirs

EnvPrefix = "SCRIPTENV"
DV = TypeVar("DV")


def _default_factory(
    env_name: str,
    cast: Callable[[str], DV],
    factory: Callable[[], DV],
) -> Callable[[], DV]:
    def _factory() -> DV:
        from_env = os.environ.get(f"{EnvPrefix}_{env_name}")
        if from_env:
            return cast(from_env)
        return factory()

    return _factory


def _bool_from_env(value: str) -> bool:
    return value.lower() not in ["false", "off", "no"]


@dataclass(frozen=True)
class Config:
    """Holds scriptenv config values."""

    cache_path: Path = field(
        default_factory=_default_factory(
            factory=lambda: Path(appdirs.user_cache_dir("scriptenv")),
            env_name="CACHE_PATH",
            cast=Path,
        )
    )
    use_lockfile: bool = field(
        default_factory=_default_factory(
            factory=lambda: True,
            env_name="USE_LOCKFILE",
            cast=_bool_from_env,
        )
    )
