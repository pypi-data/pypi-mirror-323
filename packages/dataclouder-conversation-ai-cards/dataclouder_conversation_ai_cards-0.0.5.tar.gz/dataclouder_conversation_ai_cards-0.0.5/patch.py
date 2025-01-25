#!/usr/bin/env python3
import sys
import re
from pathlib import Path

def bump_version(version_type):
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    content = pyproject_path.read_text()
    
    # Find current version
    version_match = re.search(r'version\s*=\s*"(\d+\.\d+\.\d+)"', content)
    if not version_match:
        raise ValueError("Could not find version in pyproject.toml")
    
    current_version = version_match.group(1)
    major, minor, patch = map(int, current_version.split('.'))
    
    # Update version based on type
    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    elif version_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid version type: {version_type}")
    
    new_version = f"{major}.{minor}.{patch}"
    
    # Replace version in file
    new_content = re.sub(
        r'(version\s*=\s*)"(\d+\.\d+\.\d+)"',
        f'\\1"{new_version}"',
        content
    )
    
    pyproject_path.write_text(new_content)
    print(f"Version bumped from {current_version} to {new_version}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python patch.py <major|minor|patch>")
        sys.exit(1)
    
    bump_version(sys.argv[1].lower())