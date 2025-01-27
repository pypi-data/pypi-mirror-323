import os
import subprocess
import sys
from bump_version import main as bump_version


def run_command(command, error_message):
    """Run a shell command and handle errors"""
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {error_message}")
        print(f"Command output: {e.output if e.output else 'No output'}")
        sys.exit(1)


def clean_builds():
    """Clean previous build artifacts"""
    print("\n🧹 Cleaning previous builds...")
    paths_to_remove = ["build/", "dist/", "*.egg-info"]
    for path in paths_to_remove:
        run_command(f"rm -rf {path}", f"Failed to remove {path}")


def build_package():
    """Build the package"""
    print("\n📦 Building package...")
    run_command("python -m build", "Failed to build package")


def upload_to_pypi():
    """Upload to PyPI using twine"""
    print("\n🚀 Uploading to PyPI...")
    run_command("python -m twine upload dist/*", "Failed to upload to PyPI")


def main():
    try:
        # 1. Bump version
        print("🔼 Bumping version...")
        bump_version()

        # 2. Clean previous builds
        clean_builds()

        # 3. Build package
        build_package()

        # 4. Upload to PyPI
        upload_to_pypi()

        print("\n✨ Release completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during release process: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
