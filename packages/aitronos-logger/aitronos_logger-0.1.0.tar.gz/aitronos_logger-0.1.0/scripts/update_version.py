#!/usr/bin/env python3
import os
import re
import shutil
import subprocess
import argparse
from typing import Optional

SETUP_FILE = "setup.py"
DIST_DIR = "dist"
BUILD_DIR = "build"
EGG_INFO_DIR = "*.egg-info"


def get_current_version(setup_file: str) -> str:
    """Extract the current version number from setup.py."""
    with open(setup_file, "r") as file:
        content = file.read()

    version_match = re.search(r'version=["\'](\d+\.\d+\.\d+)["\']', content)
    if version_match:
        return version_match.group(1)
    raise ValueError("Version number not found in setup.py")


def run_tests() -> None:
    """Run the tests to ensure everything is working before updating the version."""
    print("Running tests...")
    try:
        subprocess.run(["pytest", "tests/", "-v"], check=True)
        print("✅ All tests passed.")
    except subprocess.CalledProcessError:
        print("❌ Tests failed! Aborting version update.")
        raise


def bump_version(version: str, part: str) -> str:
    """Bump the version number."""
    major, minor, patch = map(int, version.split("."))

    if part == "major":
        major += 1
        minor = patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        raise ValueError("Invalid part to bump. Choose 'major', 'minor', or 'patch'.")

    return f"{major}.{minor}.{patch}"


def update_setup_file(setup_file: str, new_version: str) -> None:
    """Update the version in setup.py."""
    with open(setup_file, "r") as file:
        content = file.read()

    updated_content = re.sub(
        r'version=["\'](\d+\.\d+\.\d+)["\']',
        f'version="{new_version}"',
        content
    )

    with open(setup_file, "w") as file:
        file.write(updated_content)


def clean_build_directories() -> None:
    """Remove all build-related directories."""
    print("Cleaning build directories...")
    for directory in [DIST_DIR, BUILD_DIR]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"✓ Cleaned {directory}/")
    
    # Clean egg-info directories
    import glob
    for egg_info in glob.glob(EGG_INFO_DIR):
        shutil.rmtree(egg_info)
        print(f"✓ Cleaned {egg_info}/")


def build_package() -> None:
    """Build the source distribution and wheel."""
    print("\nBuilding package...")
    try:
        subprocess.run(["python", "-m", "build"], check=True)
        print("✅ Package built successfully.")
    except subprocess.CalledProcessError:
        print("❌ Package build failed!")
        raise


def upload_package(test: bool = False) -> None:
    """Upload the package to PyPI using twine."""
    cmd = ["twine", "upload"]
    if test:
        cmd.extend(["--repository", "testpypi"])
    cmd.extend([f"{DIST_DIR}/*"])

    print(f"\nUploading package to {'TestPyPI' if test else 'PyPI'}...")
    try:
        subprocess.run(cmd, check=True)
        print("✅ Package uploaded successfully.")
    except subprocess.CalledProcessError:
        print("❌ Package upload failed!")
        raise


def commit_changes(version: str) -> None:
    """Commit version changes to git."""
    try:
        subprocess.run(["git", "add", SETUP_FILE], check=True)
        subprocess.run(["git", "commit", "-m", f"Bump version to {version}"], check=True)
        print("✅ Changes committed to git.")
    except subprocess.CalledProcessError:
        print("❌ Failed to commit changes!")
        raise


def tag_version(version: str) -> None:
    """Tag the new version in Git and push the tag."""
    tag = f"v{version}"
    try:
        subprocess.run(["git", "tag", "-a", tag, "-m", f"Version {version}"], check=True)
        subprocess.run(["git", "push", "origin", tag], check=True)
        print(f"✅ Version {version} tagged and pushed to git.")
    except subprocess.CalledProcessError:
        print("❌ Failed to create or push git tag!")
        raise


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update version, build, and upload package to PyPI."
    )
    parser.add_argument(
        "part",
        choices=["major", "minor", "patch"],
        help="Which part of the version to bump"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Upload to TestPyPI instead of PyPI"
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Skip git operations (commit and tag)"
    )
    args = parser.parse_args()

    try:
        # Step 1: Run tests
        run_tests()

        # Step 2: Get and bump version
        current_version = get_current_version(SETUP_FILE)
        new_version = bump_version(current_version, args.part)
        print(f"\nVersion: {current_version} → {new_version}")

        # Step 3: Update setup.py
        update_setup_file(SETUP_FILE, new_version)
        print(f"✓ Updated {SETUP_FILE}")

        # Step 4: Clean build directories
        clean_build_directories()

        # Step 5: Build package
        build_package()

        # Step 6: Git operations (optional)
        if not args.no_git:
            commit_changes(new_version)
            tag_version(new_version)

        # Step 7: Upload to PyPI
        upload_package(test=args.test)

        print("\n✨ Version update complete! ✨")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main() 