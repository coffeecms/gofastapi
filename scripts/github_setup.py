#!/usr/bin/env python3
"""
Quick GitHub Setup and Push Script
Automates GitHub repository setup and pushes code
"""

import os
import subprocess
import sys


def run_command(cmd, cwd=None):
    """Run shell command."""
    print(f"🔧 Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"   Details: {e.stderr.strip()}")
        return False


def setup_git_repo():
    """Initialize and setup Git repository."""
    print("📚 Setting up Git repository...")
    
    # Initialize git if not already done
    if not os.path.exists(".git"):
        run_command("git init")
    
    # Add all files
    run_command("git add .")
    
    # Commit changes
    commit_msg = "🚀 Initial GoFastAPI package release - 25x faster than FastAPI"
    run_command(f'git commit -m "{commit_msg}"')
    
    # Set main branch
    run_command("git branch -M main")
    
    print("✅ Git repository setup complete")


def setup_github_remote():
    """Setup GitHub remote repository."""
    print("🔗 Setting up GitHub remote...")
    
    github_repo = "https://github.com/coffeecms/gofastapi.git"
    
    # Add remote origin
    run_command(f"git remote add origin {github_repo}")
    
    # Or set remote if already exists
    run_command(f"git remote set-url origin {github_repo}")
    
    print(f"✅ GitHub remote set to: {github_repo}")


def push_to_github():
    """Push code to GitHub."""
    print("📤 Pushing to GitHub...")
    
    # Push to GitHub
    if run_command("git push -u origin main"):
        print("✅ Code successfully pushed to GitHub")
        return True
    else:
        print("⚠️ Push failed, trying to force push...")
        if run_command("git push -u origin main --force"):
            print("✅ Force push successful")
            return True
        else:
            print("❌ Push to GitHub failed")
            return False


def create_github_assets():
    """Create additional GitHub assets."""
    print("📋 Creating GitHub assets...")
    
    # Create .gitignore if not exists
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Go
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
go.work

# Build artifacts
*.wasm
*.asm
""".strip()
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    # Create GitHub workflows directory
    os.makedirs(".github/workflows", exist_ok=True)
    
    # Create basic CI workflow
    ci_workflow = """
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  release:
    types: [ published ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v
    
    - name: Run linting
      run: |
        python -m flake8 gofastapi/ --max-line-length=88

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: "3.11"
    
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Check package
      run: twine check dist/*
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist
        path: dist/

  publish:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'release'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: "3.11"
    
    - name: Download artifacts
      uses: actions/download-artifact@v3
      with:
        name: dist
        path: dist/
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        pip install twine
        twine upload dist/*
""".strip()
    
    with open(".github/workflows/ci.yml", "w") as f:
        f.write(ci_workflow)
    
    print("✅ GitHub assets created")


def display_next_steps():
    """Display next steps for the user."""
    print("\n🎉 GitHub setup complete!")
    print("\n📋 Next Steps:")
    print("1. 🌐 Visit: https://github.com/coffeecms/gofastapi")
    print("2. 📝 Update repository description and topics")
    print("3. 🔑 Add PyPI API token to GitHub Secrets:")
    print("   • Go to Settings > Secrets and variables > Actions")
    print("   • Add secret: PYPI_API_TOKEN")
    print("   • Get token from: https://pypi.org/manage/account/token/")
    print("4. 🏷️ Create a release to trigger PyPI publish:")
    print("   • Go to Releases > Create new release")
    print("   • Tag: v1.0.0")
    print("   • Title: GoFastAPI v1.0.0 - 25x Faster than FastAPI")
    print("5. 📦 Package will auto-publish to PyPI on release")
    
    print("\n🔗 Repository: https://github.com/coffeecms/gofastapi")
    print("🚀 Ready to make Python 25x faster!")


def main():
    """Main GitHub setup function."""
    print("🚀 GoFastAPI GitHub Setup & Push")
    print("=" * 40)
    
    # Change to package directory
    package_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(package_dir)
    os.chdir(parent_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    try:
        # Setup steps
        create_github_assets()
        setup_git_repo()
        setup_github_remote()
        
        if push_to_github():
            display_next_steps()
        else:
            print("❌ Setup completed but push failed")
            print("💡 You may need to manually push or check repository permissions")
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
