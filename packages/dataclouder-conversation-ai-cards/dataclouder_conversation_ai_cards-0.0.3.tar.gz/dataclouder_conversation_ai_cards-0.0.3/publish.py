#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
import re
import shutil

def run_command(command, check=True):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def clean():
    """Clean build directories."""
    print("🧹 Cleaning build directories...")
    dirs_to_clean = ['dist', 'build', '*.egg-info']
    for pattern in dirs_to_clean:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

def get_current_version():
    """Get current version from pyproject.toml."""
    with open('pyproject.toml', 'r') as f:
        content = f.read()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    return match.group(1) if match else None

def update_version(new_version):
    """Update version in pyproject.toml."""
    with open('pyproject.toml', 'r') as f:
        content = f.read()
    
    updated_content = re.sub(
        r'(version\s*=\s*)"([^"]+)"',
        f'\\1"{new_version}"',
        content
    )
    
    with open('pyproject.toml', 'w') as f:
        f.write(updated_content)

def build_and_publish():
    """Main function to handle the publishing process."""
    # Check if we're in a clean git state
    if run_command("git status --porcelain", check=False):
        print("❌ Working directory is not clean. Please commit all changes first.")
        sys.exit(1)

    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    # Ask for new version
    new_version = input(f"Enter new version (current is {current_version}): ").strip()
    if not new_version:
        print("❌ Version cannot be empty")
        sys.exit(1)

    try:
        # Clean previous builds
        clean()
        
        # Update version
        update_version(new_version)
        print(f"✅ Updated version to {new_version}")

        # Build package
        print("🔨 Building package...")
        run_command("python -m build")
        
        # Create git tag
        tag_name = f"v{new_version}"
        run_command(f'git add pyproject.toml')
        run_command(f'git commit -m "Bump version to {new_version}"')
        run_command(f'git tag -a {tag_name} -m "Release version {new_version}"')
        
        # Confirm before publishing
        if input("Ready to publish? (y/N): ").lower() == 'y':
            print("📦 Publishing to PyPI...")
            run_command("twine upload dist/*")
            run_command("git push origin main --tags")
            print(f"✨ Successfully published version {new_version}")
        else:
            print("📦 Publishing cancelled")
            # Revert changes
            run_command("git reset --hard HEAD^")
            run_command(f"git tag -d {tag_name}")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_and_publish()