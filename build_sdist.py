#!/usr/bin/env python3
"""
Build script for splurge-tools source distributions only.

This script ensures only source distributions are built, not wheels.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def clean_build_artifacts():
    """Clean up build artifacts."""
    artifacts = ["dist", "build", "splurge_tools.egg-info"]
    for artifact in artifacts:
        if Path(artifact).exists():
            shutil.rmtree(artifact)


def build_sdist():
    """Build source distribution only."""
    result = subprocess.run([sys.executable, "-m", "build", "--sdist"], check=False, capture_output=True, text=True)

    if result.returncode == 0:
        # List the created files
        dist_dir = Path("dist")
        if dist_dir.exists():
            for _file in dist_dir.glob("*.tar.gz"):
                pass
    else:
        return False

    return True


def main():
    """Main build process."""

    # Clean previous builds
    clean_build_artifacts()

    # Build sdist
    if build_sdist():
        pass
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
