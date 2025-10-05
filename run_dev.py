#!/usr/bin/env python3
"""
Development runner for LeagueAccounts
Runs the application directly from source for development
"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    try:
        from leagueaccounts.main import main
        main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the LeagueAccounts root directory")
        print("and that all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)
