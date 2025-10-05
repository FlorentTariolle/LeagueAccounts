#!/usr/bin/env python3
"""
Installer creation script for LeagueAccounts
Creates a Windows installer using Inno Setup
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import json

def check_inno_setup():
    """Check if Inno Setup is installed"""
    print("Checking for Inno Setup...")
    
    # Common Inno Setup installation paths
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup\ISCC.exe",
        r"C:\Program Files\Inno Setup\ISCC.exe"
    ]
    
    for path in inno_paths:
        if os.path.exists(path):
            print(f"SUCCESS: Found Inno Setup: {path}")
            return path
    
    print("ERROR: Inno Setup not found!")
    print("\nPlease install Inno Setup from: https://jrsoftware.org/isdl.php")
    print("Or check if it's installed in a non-standard location.")
    return None

def check_executable():
    """Check if the executable exists"""
    print("Checking for executable...")
    
    exe_path = Path("config/dist/leagueaccounts.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"SUCCESS: Found executable: {exe_path} ({size_mb:.1f} MB)")
        return True
    else:
        print("ERROR: Executable not found!")
        print("Please run scripts/build_exe.py first to create the executable.")
        return False

def update_installer_version():
    """Check the installer version (no longer auto-increments)"""
    print("Checking installer version...")
    
    iss_file = Path("config/installer.iss")
    if not iss_file.exists():
        print("ERROR: Installer script not found!")
        return False
    
    # Read current version
    with open(iss_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract current version
    import re
    version_match = re.search(r'AppVersion=([\d\.]+)', content)
    if version_match:
        current_version = version_match.group(1)
        print(f"   Current version: {current_version}")
    else:
        print("   Could not determine current version")
    
    return True

def create_installer():
    """Create the installer using Inno Setup"""
    print("Creating installer...")
    
    # Get Inno Setup path
    inno_path = check_inno_setup()
    if not inno_path:
        return False
    
    # Check for executable
    if not check_executable():
        return False
    
    # Check version
    update_installer_version()
    
    # Path to the installer script
    iss_file = Path("config/installer.iss").absolute()
    
    try:
        # Run Inno Setup compiler
        cmd = [inno_path, str(iss_file)]
        
        print(f"Running: {' '.join(cmd)}")
        print("This may take a few minutes...")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("SUCCESS: Installer created successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Installer creation failed!")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False
    
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False

def verify_installer():
    """Verify the installer was created successfully"""
    print("Verifying installer...")
    
    # Look for installer files in config/dist directory
    dist_dir = Path("config/dist")
    installer_files = list(dist_dir.glob("LeagueAccountsSetup*.exe"))
    
    if installer_files:
        installer_path = installer_files[0]  # Get the first (should be only one)
        size_mb = installer_path.stat().st_size / (1024 * 1024)
        print(f"SUCCESS: Installer created: {installer_path.name} ({size_mb:.1f} MB)")
        
        # Show full path
        print(f"Full path: {installer_path.absolute()}")
        return True
    else:
        print("ERROR: Installer not found!")
        print("Expected file pattern: LeagueAccountsSetup*.exe in config/dist/ directory")
        return False

def cleanup_temp_files():
    """Clean up temporary files created during build"""
    print("Cleaning up temporary files...")
    
    # Remove any temporary files that might have been created
    temp_patterns = [
        "config/output",
        "config/__pycache__",
        "*.tmp"
    ]
    
    for pattern in temp_patterns:
        if "*" in pattern:
            # Handle glob patterns
            for file_path in Path(".").rglob(pattern):
                if file_path.is_file():
                    file_path.unlink()
                    print(f"   Removed: {file_path}")
        else:
            # Handle directory patterns
            path = Path(pattern)
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"   Removed directory: {path}")
                else:
                    path.unlink()
                    print(f"   Removed file: {path}")

def show_build_info():
    """Show build information and next steps"""
    print("\nBuild Information:")
    print("-" * 30)
    
    # Get installer info
    dist_dir = Path("config/dist")
    installer_files = list(dist_dir.glob("LeagueAccountsSetup*.exe"))
    exe_files = list(dist_dir.glob("leagueaccounts.exe"))
    
    if installer_files:
        installer = installer_files[0]
        installer_size = installer.stat().st_size / (1024 * 1024)
        print(f"Installer: {installer.name} ({installer_size:.1f} MB)")
    
    if exe_files:
        exe = exe_files[0]
        exe_size = exe.stat().st_size / (1024 * 1024)
        print(f"Executable: {exe.name} ({exe_size:.1f} MB)")
    
    print("\nNext Steps:")
    print("1. Test the installer on a clean system")
    print("2. Verify all features work correctly")
    print("3. Upload to your distribution platform")
    print("4. Update your README with new download link")

def main():
    """Main installer creation process"""
    print("LeagueAccounts Installer Creation Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("config") or not os.path.exists("config/installer.iss"):
        print("ERROR: Please run this script from the LeagueAccounts root directory!")
        print("   Expected structure:")
        print("   LeagueAccounts/")
        print("   ├── config/")
        print("   │   └── installer.iss")
        print("   ├── config/dist/")
        print("   │   └── leagueaccounts.exe")
        print("   └── scripts/")
        print("       └── create_installer.py")
        sys.exit(1)
    
    # Step 1: Create installer
    if not create_installer():
        sys.exit(1)
    
    # Step 2: Verify installer
    if not verify_installer():
        sys.exit(1)
    
    # Step 3: Cleanup
    cleanup_temp_files()
    
    # Step 4: Show build info
    show_build_info()
    
    print("\nSUCCESS: Installer creation completed successfully!")

if __name__ == "__main__":
    main()
