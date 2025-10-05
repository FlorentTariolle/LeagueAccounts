# LeagueAccounts Project Structure

This document describes the reorganized project structure for LeagueAccounts.

## Overview

The project has been restructured to follow Python best practices and provide clear separation of concerns.

## Directory Structure

```
LeagueAccounts/
├── src/                          # Source code
│   ├── leagueaccounts/           # Main package
│   │   ├── __init__.py          # Package initialization
│   │   ├── main.py              # Application entry point
│   │   ├── gui.py               # GUI components
│   │   ├── models.py            # Data models
│   │   ├── account_manager.py   # Account management logic
│   │   ├── rank_fetcher.py      # Rank fetching functionality
│   │   └── utils.py             # Utility functions
│   └── tests/                   # Test files (future)
├── assets/                      # Static assets
│   ├── icons/
│   │   └── icon.ico            # Application icon
│   └── images/                 # Additional images (future)
├── config/                      # Configuration files
│   ├── leagueaccounts.spec     # PyInstaller specification
│   └── installer.iss           # Inno Setup installer script
├── scripts/                     # Build and utility scripts
│   ├── build_exe.py            # Executable builder
│   ├── create_installer.py     # Installer creator
│   └── build_all.py            # Complete build pipeline
├── data/                        # Runtime data
│   └── league_accounts.json    # User account data
├── docs/                        # Documentation
│   ├── BUILD.md                # Build instructions
│   └── PROJECT_STRUCTURE.md    # This file
├── requirements.txt             # Python dependencies
├── README.md                    # Project overview
├── run_dev.py                   # Development runner
└── .gitignore                   # Git ignore rules
```

## Key Changes

### 1. **Source Code Organization**
- **Before**: All source files mixed in `src/` with config files
- **After**: Clean package structure in `src/leagueaccounts/` with proper `__init__.py`

### 2. **Asset Management**
- **Before**: Icon file in source directory
- **After**: Dedicated `assets/` directory with organized subdirectories

### 3. **Configuration Files**
- **Before**: Build files scattered in `src/`
- **After**: All configuration in dedicated `config/` directory

### 4. **Build Scripts**
- **Before**: Build scripts in root directory
- **After**: Organized in `scripts/` directory

### 5. **Documentation**
- **Before**: Mixed with other files
- **After**: Dedicated `docs/` directory

### 6. **Runtime Data**
- **Before**: Data files in source directory
- **After**: Dedicated `data/` directory

## Benefits

### ✅ **Separation of Concerns**
- Source code, assets, config, and scripts are clearly separated
- Each directory has a specific purpose

### ✅ **Professional Structure**
- Follows Python packaging best practices
- Easy to navigate and understand

### ✅ **Maintainability**
- Clear organization makes maintenance easier
- New developers can quickly understand the structure

### ✅ **Scalability**
- Easy to add new features without cluttering
- Test directory ready for future testing

### ✅ **Build Process**
- Build scripts work with new structure
- Configuration files properly organized

## Usage

### Development
```bash
# Run in development mode
python run_dev.py

# Or run directly
python -m src.leagueaccounts.main
```

### Building
```bash
# Build executable and installer
python scripts/build_all.py

# Or step by step
python scripts/build_exe.py
python scripts/create_installer.py
```

### Package Structure
The main package (`src/leagueaccounts/`) can be imported as:
```python
from leagueaccounts import LeagueAccountApp, Account, AccountManager
```

## File Locations

| Component | Old Location | New Location |
|-----------|-------------|--------------|
| Main source | `src/main.py` | `src/leagueaccounts/main.py` |
| GUI code | `src/gui.py` | `src/leagueaccounts/gui.py` |
| Models | `src/models.py` | `src/leagueaccounts/models.py` |
| Account manager | `src/account_manager.py` | `src/leagueaccounts/account_manager.py` |
| Rank fetcher | `src/rank_fetcher.py` | `src/leagueaccounts/rank_fetcher.py` |
| Utils | `src/utils.py` | `src/leagueaccounts/utils.py` |
| Icon | `src/icon.ico` | `assets/icons/icon.ico` |
| PyInstaller spec | `src/leagueaccounts.spec` | `config/leagueaccounts.spec` |
| Installer script | `src/leagueaccounts_installer.iss` | `config/installer.iss` |
| Build scripts | `build_*.py` | `scripts/build_*.py` |
| User data | `src/league_accounts.json` | `data/league_accounts.json` |
| Documentation | `BUILD.md` | `docs/BUILD.md` |

## Migration Notes

- All import statements have been updated to use relative imports
- Build scripts have been updated to work with new paths
- Configuration files point to correct asset locations
- Documentation reflects the new structure

This reorganization provides a solid foundation for future development and maintenance.
