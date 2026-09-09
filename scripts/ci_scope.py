"""Classify the full PR diff for runtime tests and Desktop builds.

Desktop bundles the Python App Server, so its CI scope includes both ``desktop``
and the Python runtime imported by the sidecar. Release-only scripts, tests, and
documentation intentionally stay outside this list.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterable


DESKTOP_IMPACT_PREFIXES = (
    ".github/actions/",
    "app_server/",
    "cli/",
    "core/",
    "desktop/",
    "prompts/",
    "protocol/",
    "schema/",
    "tools/",
    "utils/",
    "workflows/",
)

DESKTOP_IMPACT_FILES = frozenset(
    {
        ".github/workflows/desktop-ci.yml",
        "__init__.py",
        "deepcode.py",
        "requirements.txt",
        "rust-toolchain.toml",
        "scripts/ci_scope.py",
    }
)


def affects_desktop(paths: Iterable[str]) -> bool:
    """Return whether any repository-relative path affects Desktop artifacts."""

    return any(
        path in DESKTOP_IMPACT_FILES or path.startswith(DESKTOP_IMPACT_PREFIXES)
        for path in paths
    )


def affects_runtime(paths: Iterable[str]) -> bool:
    """Only known documentation paths may bypass runtime tests."""
    return any(
        path not in {"README.md", "README_ZH.md", "CONTRIBUTORS.md"}
        and not path.startswith(("docs/", "assets/readme/"))
        for path in paths
    )


def _read_null_delimited_paths() -> list[str]:
    return [
        os.fsdecode(raw_path)
        for raw_path in sys.stdin.buffer.read().split(b"\0")
        if raw_path
    ]


def main() -> int:
    paths = _read_null_delimited_paths()
    # Empty/unknown input must never silently turn off validation.
    for name, changed in (
        ("runtime_changed", not paths or affects_runtime(paths)),
        ("desktop_changed", not paths or affects_desktop(paths)),
    ):
        print(f"{name}={'true' if changed else 'false'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
