#!/usr/bin/env python3
"""
Build script for splurge-tools source distributions only.

This script ensures only source distributions are built, not wheels.
"""

import subprocess
import sys
import shutil
from pathlib import Path


def clean_build_artifacts():
    """Clean up build artifacts."""
    artifacts = ["dist", "build", "splurge_tools.egg-info"]
    for artifact in artifacts:
        if Path(artifact).exists():
            shutil.rmtree(artifact)
            print(f"Cleaned {artifact}")


def build_sdist():
    """Build source distribution only."""
    print("Building source distribution...")
    result = subprocess.run([sys.executable, "-m", "build", "--sdist"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Source distribution built successfully!")
        # List the created files
        dist_dir = Path("dist")
        if dist_dir.exists():
            for file in dist_dir.glob("*.tar.gz"):
                print(f"📦 Created: {file}")
    else:
        print("❌ Build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    return True


def main():
    """Main build process."""
    print("🚀 Building splurge-tools source distribution...")
    
    # Clean previous builds
    clean_build_artifacts()
    
    # Build sdist
    if build_sdist():
        print("\n🎉 Build completed successfully!")
        print("📁 Source distribution is in the 'dist' directory")
    else:
        print("\n💥 Build failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
