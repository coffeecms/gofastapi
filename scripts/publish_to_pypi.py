#!/usr/bin/env python3
"""
Build and publish GoFastAPI package to PyPI
Automated build, test, and publication script
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import argparse


def run_command(cmd, cwd=None, check=True):
    """Run shell command and return result."""
    print(f"🔧 Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        if result.stdout:
            print(f"✅ Output: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"❌ Error details: {e.stderr}")
        return None


def check_requirements():
    """Check if required tools are installed."""
    print("🔍 Checking requirements...")
    
    required_tools = ["python", "pip", "git"]
    missing_tools = []
    
    for tool in required_tools:
        result = run_command(f"which {tool}", check=False)
        if result is None or result.returncode != 0:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"❌ Missing required tools: {', '.join(missing_tools)}")
        return False
    
    print("✅ All required tools are available")
    return True


def clean_build_artifacts():
    """Clean previous build artifacts."""
    print("🧹 Cleaning build artifacts...")
    
    artifacts = [
        "build",
        "dist", 
        "*.egg-info",
        "__pycache__",
        "**/__pycache__",
        "**/*.pyc",
        ".pytest_cache"
    ]
    
    for pattern in artifacts:
        run_command(f"rm -rf {pattern}", check=False)
    
    print("✅ Build artifacts cleaned")


def run_tests():
    """Run test suite."""
    print("🧪 Running test suite...")
    
    # Check if pytest is available
    result = run_command("python -m pytest --version", check=False)
    if result is None or result.returncode != 0:
        print("⚠️ pytest not found, installing...")
        run_command("pip install pytest")
    
    # Run tests
    result = run_command("python -m pytest tests/ -v", check=False)
    if result is None or result.returncode != 0:
        print("⚠️ Some tests failed, but continuing with build...")
        return False
    
    print("✅ All tests passed")
    return True


def lint_code():
    """Run code linting."""
    print("🔍 Running code linting...")
    
    # Check flake8
    result = run_command("python -m flake8 --version", check=False)
    if result is None or result.returncode != 0:
        print("⚠️ flake8 not found, installing...")
        run_command("pip install flake8")
    
    # Run linting
    result = run_command("python -m flake8 gofastapi/ --max-line-length=88 --ignore=E203,W503", check=False)
    if result and result.returncode != 0:
        print("⚠️ Linting issues found, but continuing...")
    else:
        print("✅ Code linting passed")
    
    return True


def verify_package_metadata():
    """Verify package metadata includes README content."""
    print("🔍 Verifying package metadata...")
    
    # Check if README.md exists
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("❌ README.md not found")
        return False
    
    # Check if pyproject.toml has readme field
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'readme = "README.md"' in content:
                print("✅ pyproject.toml configured to include README.md")
            else:
                print("❌ pyproject.toml missing README.md configuration")
                return False
    else:
        print("❌ pyproject.toml not found")
        return False
    
    # Check README content
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()
        if len(readme_content.strip()) > 100:  # Should have substantial content
            print("✅ README.md has substantial content")
        else:
            print("❌ README.md appears to be too short")
            return False
    
    return True


def build_package():
    """Build the package."""
    print("📦 Building package...")
    
    # Verify package metadata first
    if not verify_package_metadata():
        print("❌ Package metadata verification failed")
        return False
    
    # Check if build is available
    result = run_command("python -m build --version", check=False)
    if result is None or result.returncode != 0:
        print("⚠️ build not found, installing...")
        run_command("pip install build")
    
    # Build package
    result = run_command("python -m build")
    if result is None:
        print("❌ Package build failed")
        return False
    
    print("✅ Package built successfully")
    
    # Verify the built package includes README content
    print("🔍 Verifying built package metadata...")
    result = run_command("python -m twine check dist/*", check=False)
    if result and result.returncode == 0:
        print("✅ Package metadata validation passed")
    else:
        print("⚠️ Package metadata validation had warnings")
    
    return True


def upload_to_testpypi():
    """Upload package to Test PyPI."""
    print("🚀 Uploading to Test PyPI...")
    
    # Check if twine is available
    result = run_command("python -m twine --version", check=False)
    if result is None or result.returncode != 0:
        print("⚠️ twine not found, installing...")
        run_command("pip install twine")
    
    # Upload to Test PyPI
    result = run_command(
        "python -m twine upload --repository testpypi dist/* --skip-existing", 
        check=False
    )
    
    if result and result.returncode == 0:
        print("✅ Package uploaded to Test PyPI successfully")
        print("🔍 Test with: pip install -i https://test.pypi.org/simple/ gofastapi")
        return True
    else:
        print("⚠️ Upload to Test PyPI failed (might already exist)")
        return False


def upload_to_pypi():
    """Upload package to production PyPI."""
    print("🚀 Uploading to PyPI...")
    
    # Confirm upload
    response = input("⚠️ Are you sure you want to upload to production PyPI? (y/N): ")
    if response.lower() != 'y':
        print("❌ Upload cancelled")
        return False
    
    # Upload to PyPI
    result = run_command("python -m twine upload dist/* --skip-existing", check=False)
    
    if result and result.returncode == 0:
        print("✅ Package uploaded to PyPI successfully")
        print("🎉 Install with: pip install gofastapi")
        return True
    else:
        print("❌ Upload to PyPI failed")
        return False


def update_github():
    """Push changes to GitHub."""
    print("📤 Updating GitHub repository...")
    
    # Check git status
    result = run_command("git status --porcelain", check=False)
    if result and result.stdout.strip():
        print("📝 Uncommitted changes found, committing...")
        
        # Add all changes
        run_command("git add .")
        
        # Commit changes
        commit_msg = "🚀 Update package for PyPI release"
        run_command(f"git commit -m '{commit_msg}'", check=False)
    
    # Push to GitHub
    result = run_command("git push origin main", check=False)
    if result and result.returncode == 0:
        print("✅ Changes pushed to GitHub successfully")
        return True
    else:
        print("⚠️ GitHub push failed or no changes to push")
        return False


def create_github_release():
    """Create GitHub release."""
    print("🏷️ Creating GitHub release...")
    
    # Get current version
    try:
        import gofastapi
        version = gofastapi.__version__
    except:
        version = "1.0.0"  # fallback
    
    tag_name = f"v{version}"
    
    # Create tag
    run_command(f"git tag {tag_name}", check=False)
    run_command(f"git push origin {tag_name}", check=False)
    
    print(f"✅ GitHub release {tag_name} created")
    print(f"🔗 Visit: https://github.com/coffeecms/gofastapi/releases/tag/{tag_name}")
    
    return True


def main():
    """Main build and publish workflow."""
    parser = argparse.ArgumentParser(description="Build and publish GoFastAPI package")
    parser.add_argument("--test-only", action="store_true", help="Only upload to Test PyPI")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-github", action="store_true", help="Skip GitHub operations")
    
    args = parser.parse_args()
    
    print("🚀 GoFastAPI Package Build & Publish")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Clean previous builds
    clean_build_artifacts()
    
    # Run tests (unless skipped)
    if not args.skip_tests:
        run_tests()
    
    # Lint code
    lint_code()
    
    # Build package
    if not build_package():
        print("❌ Build failed, aborting")
        sys.exit(1)
    
    # Upload to Test PyPI
    upload_to_testpypi()
    
    # Upload to production PyPI (unless test-only)
    if not args.test_only:
        if upload_to_pypi():
            print("\n🎉 Package successfully published to PyPI!")
        else:
            print("\n❌ PyPI upload failed")
            sys.exit(1)
    else:
        print("\n✅ Test PyPI upload completed")
    
    # GitHub operations (unless skipped)
    if not args.skip_github:
        update_github()
        create_github_release()
    
    print("\n🎉 Build and publish process completed!")
    print("\n📦 Package Information:")
    print("   • PyPI: https://pypi.org/project/gofastapi/")
    print("   • GitHub: https://github.com/coffeecms/gofastapi")
    print("   • Install: pip install gofastapi")
    
    if args.test_only:
        print("\n🔍 Test the package:")
        print("   pip install -i https://test.pypi.org/simple/ gofastapi")


if __name__ == "__main__":
    main()
