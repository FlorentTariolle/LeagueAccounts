"""
LeagueAccounts - League of Legends Account Manager

A tool for managing multiple League of Legends accounts with features like:
- Quick account switching
- Secure password storage
- Automatic rank fetching
- Auto credential entry
"""

__version__ = "1.1"
__author__ = "LeagueAccounts Team"
__description__ = "League of Legends Account Manager"

# Import main components for easy access
from .gui import LeagueAccountApp
from .models import Account
from .account_manager import AccountManager
from .rank_fetcher import RankFetcher
from .main import main

__all__ = [
    'LeagueAccountApp',
    'Account', 
    'AccountManager',
    'RankFetcher',
    'main',
    '__version__',
    '__author__',
    '__description__'
]
