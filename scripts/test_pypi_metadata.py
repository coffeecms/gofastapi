#!/usr/bin/env python3
"""
Test PyPI package metadata before publishing
Ensures README.md content will be displayed on PyPI
"""

import os
import sys
import subprocess
from pathlib import Path
import tempfile
import tarfile
import zipfile
import json


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


def test_package_metadata():
    """Test that package metadata includes README content."""
    print("🔍 Testing package metadata...")
    
    # Check pyproject.toml
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found")
        return False
    
    with open(pyproject_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check for required fields
    required_fields = [
        'readme = "README.md"',
        'description =',
        'name = "gofastapi"',
        'version =',
        'authors ='
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in content:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing fields in pyproject.toml: {missing_fields}")
        return False
    
    print("✅ pyproject.toml has all required metadata fields")
    
    # Check README.md
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("❌ README.md not found")
        return False
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    if len(readme_content.strip()) < 100:
        print("❌ README.md is too short")
        return False
    
    print(f"✅ README.md has {len(readme_content)} characters")
    
    # Check for essential README sections
    essential_sections = [
        "GoFastAPI",
        "installation",
        "usage",
        "performance"
    ]
    
    missing_sections = []
    readme_lower = readme_content.lower()
    for section in essential_sections:
        if section.lower() not in readme_lower:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"⚠️ README.md missing recommended sections: {missing_sections}")
    else:
        print("✅ README.md has all essential sections")
    
    return True


def build_test_package():
    """Build package for testing."""
    print("📦 Building test package...")
    
    # Clean previous builds
    run_command("rm -rf build dist *.egg-info", check=False)
    
    # Install build tools
    run_command("pip install build twine", check=False)
    
    # Build package
    result = run_command("python -m build")
    if result is None or result.returncode != 0:
        print("❌ Package build failed")
        return False
    
    print("✅ Package built successfully")
    return True


def check_built_package():
    """Check the built package for metadata."""
    print("🔍 Checking built package...")
    
    # Check with twine
    result = run_command("python -m twine check dist/*")
    if result is None or result.returncode != 0:
        print("❌ Package validation failed")
        return False
    
    print("✅ Package validation passed")
    
    # Extract and examine package contents
    dist_path = Path("dist")
    if not dist_path.exists():
        print("❌ dist/ directory not found")
        return False
    
    # Look for .tar.gz file (source distribution)
    tar_files = list(dist_path.glob("*.tar.gz"))
    if not tar_files:
        print("❌ No source distribution found")
        return False
    
    tar_file = tar_files[0]
    print(f"📦 Examining: {tar_file.name}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract package
        with tarfile.open(tar_file, 'r:gz') as tar:
            tar.extractall(temp_dir)
        
        # Find extracted directory
        extracted_dirs = [d for d in Path(temp_dir).iterdir() if d.is_dir()]
        if not extracted_dirs:
            print("❌ Could not find extracted package directory")
            return False
        
        package_dir = extracted_dirs[0]
        
        # Check for README.md in package
        readme_in_package = package_dir / "README.md"
        if readme_in_package.exists():
            print("✅ README.md included in package")
            with open(readme_in_package, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✅ README.md in package has {len(content)} characters")
        else:
            print("❌ README.md not found in package")
            return False
        
        # Check PKG-INFO
        pkg_info = package_dir / "PKG-INFO"
        if pkg_info.exists():
            with open(pkg_info, 'r', encoding='utf-8') as f:
                pkg_content = f.read()
                
            if "Description:" in pkg_content and len(pkg_content) > 1000:
                print("✅ PKG-INFO contains long description")
            else:
                print("❌ PKG-INFO missing or incomplete long description")
                return False
        else:
            print("⚠️ PKG-INFO not found (this is unusual)")
    
    return True


def simulate_pypi_upload():
    """Simulate what PyPI will see."""
    print("🔍 Simulating PyPI upload...")
    
    # Check package info
    result = run_command("python setup.py --long-description", check=False)
    if result and result.stdout and len(result.stdout.strip()) > 100:
        print("✅ Long description available via setup.py")
        print(f"📝 Description length: {len(result.stdout.strip())} characters")
    else:
        print("⚠️ Long description not available via setup.py")
    
    return True


def main():
    """Main test workflow."""
    print("🧪 GoFastAPI PyPI Metadata Test")
    print("=" * 50)
    
    success = True
    
    # Test metadata configuration
    if not test_package_metadata():
        success = False
    
    print("\n" + "=" * 50)
    
    # Build test package
    if not build_test_package():
        success = False
    
    print("\n" + "=" * 50)
    
    # Check built package
    if not check_built_package():
        success = False
    
    print("\n" + "=" * 50)
    
    # Simulate PyPI upload
    simulate_pypi_upload()
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 All tests passed! Package should display properly on PyPI.")
        print("\n📋 Summary:")
        print("   ✅ pyproject.toml configured correctly")
        print("   ✅ README.md has substantial content")
        print("   ✅ Package builds successfully")
        print("   ✅ Built package includes README.md")
        print("   ✅ PKG-INFO contains long description")
        print("\n🚀 Ready to publish to PyPI!")
    else:
        print("❌ Some tests failed. Please fix issues before publishing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
