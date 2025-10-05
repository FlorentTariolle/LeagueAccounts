#!/usr/bin/env python3
"""
Complete build script for LeagueAccounts
Builds executable and creates installer in one go
"""

import os
import sys
import subprocess
from pathlib import Path

def run_script(script_name):
    """Run a Python script and return success status"""
    print(f"\n{'='*60}")
    print(f"Running {script_name}...")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ {script_name} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ {script_name} not found!")
        return False

def main():
    """Main build process"""
    print("🚀 LeagueAccounts Complete Build Script")
    print("=" * 60)
    print("This script will:")
    print("1. Build the executable (build_exe.py)")
    print("2. Create the installer (create_installer.py)")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("src"):
        print("❌ Please run this script from the LeagueAccounts root directory!")
        sys.exit(1)
    
    # Step 1: Build executable
    if not run_script("build_exe.py"):
        print("\n❌ Build process failed at executable creation step!")
        sys.exit(1)
    
    # Step 2: Create installer
    if not run_script("create_installer.py"):
        print("\n❌ Build process failed at installer creation step!")
        sys.exit(1)
    
    print("\n🎉 Complete build process finished successfully!")
    print("\n📁 Output files:")
    
    # List output files
    dist_dir = Path("dist")
    if dist_dir.exists():
        for file_path in dist_dir.iterdir():
            if file_path.is_file():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"   {file_path.name} ({size_mb:.1f} MB)")
    
    print("\n✅ Ready for distribution!")

if __name__ == "__main__":
    main()
