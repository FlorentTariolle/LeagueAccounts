#!/usr/bin/env python3
"""
Build script for LeagueAccounts executable
Builds the executable using PyInstaller with optimized settings
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_directories():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous build artifacts...")
    
    # Directories to clean
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    # Clean directories
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Clean Python cache files in src directory
    for root, dirs, files in os.walk('src'):
        for dir_name in dirs[:]:  # Copy list to avoid modification during iteration
            if dir_name == '__pycache__':
                shutil.rmtree(os.path.join(root, dir_name))
                print(f"   Removed {os.path.join(root, dir_name)}/")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'pyinstaller',
        'tkinter',  # Usually comes with Python
        'pillow',
        'requests',
        'beautifulsoup4',
        'pyautogui',
        'keyring',
        'pyperclip'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'beautifulsoup4':
                import bs4
            elif package == 'pillow':
                import PIL
            else:
                __import__(package)
            print(f"   ✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ✗ {package} (missing)")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies are installed!")
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    # Change to config directory
    config_dir = Path("config")
    if not config_dir.exists():
        print("❌ config/ directory not found!")
        return False
    
    os.chdir(config_dir)
    
    try:
        # Run PyInstaller with the spec file
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",  # Clean cache and remove temp files
            "--noconfirm",  # Replace output directory without asking
            "leagueaccounts.spec"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Executable built successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed!")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    finally:
        # Change back to root directory
        os.chdir("..")

def verify_build():
    """Verify the build was successful"""
    print("🔍 Verifying build...")
    
    exe_path = Path("build/dist/leagueaccounts.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ Executable created: {exe_path} ({size_mb:.1f} MB)")
        return True
    else:
        print("❌ Executable not found!")
        return False

def main():
    """Main build process"""
    print("🚀 LeagueAccounts Build Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("config") or not os.path.exists("config/leagueaccounts.spec"):
        print("❌ Please run this script from the LeagueAccounts root directory!")
        print("   Expected structure:")
        print("   LeagueAccounts/")
        print("   ├── config/")
        print("   │   └── leagueaccounts.spec")
        print("   └── scripts/")
        print("       └── build_exe.py")
        sys.exit(1)
    
    # Step 1: Clean previous builds
    clean_build_directories()
    
    # Step 2: Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Step 3: Build executable
    if not build_executable():
        sys.exit(1)
    
    # Step 4: Verify build
    if not verify_build():
        sys.exit(1)
    
    print("\n🎉 Build completed successfully!")
    print(f"📁 Executable location: {Path('build/dist/leagueaccounts.exe').absolute()}")
    print("\nNext steps:")
    print("1. Test the executable")
    print("2. Run scripts/create_installer.py to create the installer")

if __name__ == "__main__":
    main()
