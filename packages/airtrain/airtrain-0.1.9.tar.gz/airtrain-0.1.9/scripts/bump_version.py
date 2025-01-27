import os
import re


def read_version():
    """Read current version from __init__.py"""
    init_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "airtrain", "__init__.py"
    )
    with open(init_path, "r", encoding="utf-8") as f:
        version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def bump_patch_version(version_str):
    """Increment the patch version"""
    major, minor, patch = map(int, version_str.split("."))
    return f"{major}.{minor}.{patch + 1}"


def update_version(new_version):
    """Update version in __init__.py"""
    init_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "airtrain", "__init__.py"
    )
    with open(init_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        f'__version__ = "{new_version}"',
        content,
        flags=re.M,
    )

    with open(init_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def main():
    try:
        current_version = read_version()
        new_version = bump_patch_version(current_version)
        update_version(new_version)
        print(f"Version bumped from {current_version} to {new_version}")
    except Exception as e:
        print(f"Error updating version: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
