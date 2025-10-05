import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Lazy import to reduce startup time
def main():
    from gui import LeagueAccountApp
    LeagueAccountApp().run()

if __name__ == '__main__':
    main()