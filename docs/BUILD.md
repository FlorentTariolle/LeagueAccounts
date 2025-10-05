# Building LeagueAccounts

This document explains how to build the LeagueAccounts executable and installer.

## Prerequisites

### Required Software
1. **Python 3.8+** - Download from [python.org](https://python.org)
2. **Inno Setup** - Download from [jrsoftware.org](https://jrsoftware.org/isdl.php)
3. **Git** (optional) - For version control

### Python Dependencies
Install required Python packages:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install pyinstaller pillow requests beautifulsoup4 pyautogui keyring pyperclip
```

## Build Process

### Option 1: Complete Build (Recommended)
Build both executable and installer in one go:
```bash
python scripts/build_all.py
```

### Option 2: Step-by-Step Build

#### Step 1: Build Executable
```bash
python scripts/build_exe.py
```

This will:
- Clean previous build artifacts
- Check dependencies
- Build the executable using PyInstaller
- Verify the build

#### Step 2: Create Installer
```bash
python scripts/create_installer.py
```

This will:
- Check for Inno Setup installation
- Verify the executable exists
- Update version number
- Create Windows installer
- Clean up temporary files

## Output Files

After successful build, you'll find:

### Executable
- `build/dist/leagueaccounts.exe` - The main application

### Installer
- `build/dist/LeagueAccountsSetup.exe` - Windows installer package

## Build Scripts

### `scripts/build_exe.py`
- Builds the executable using PyInstaller
- Uses optimized settings from `config/leagueaccounts.spec`
- Includes dependency checking and cleanup

### `scripts/create_installer.py`
- Creates Windows installer using Inno Setup
- Automatically increments version number
- Handles error checking and verification

### `scripts/build_all.py`
- Runs both build scripts in sequence
- Provides complete build process
- Shows final output summary

## Troubleshooting

### Common Issues

#### "Inno Setup not found"
- Install Inno Setup from the official website
- Ensure it's installed in a standard location
- The script checks common installation paths

#### "Dependencies missing"
- Run `pip install -r requirements.txt`
- Ensure you're using Python 3.8 or higher
- Check that all packages installed correctly

#### "Executable not found"
- Run `scripts/build_exe.py` first before creating installer
- Check that the build completed successfully
- Verify `build/dist/leagueaccounts.exe` exists

#### Build fails with PyInstaller errors
- Clean build directories: Delete `build/` and `dist/` folders
- Update PyInstaller: `pip install --upgrade pyinstaller`
- Check for antivirus interference

### Performance Optimization

The build scripts include several optimizations:
- **UPX compression disabled** - Faster startup time
- **Python optimization level 2** - Better bytecode optimization
- **Lazy imports** - Heavy dependencies loaded only when needed
- **Deferred initialization** - GUI appears faster

## Version Management

The installer version is automatically incremented each time you run `scripts/create_installer.py`. The version is stored in `config/installer.iss`.

To manually set a version, edit the `AppVersion` line in the `.iss` file.

## Distribution

After building:
1. Test the installer on a clean system
2. Verify all features work correctly
3. Upload to your distribution platform
4. Update download links in documentation

## Development

For development builds:
- Use `python -m src.leagueaccounts.main` to run directly
- Modify `config/leagueaccounts.spec` for PyInstaller options
- Edit `config/installer.iss` for installer settings
