"""
LeagueAccounts Main Entry Point
"""

# Lazy import to reduce startup time
def main():
    from .gui import LeagueAccountApp
    LeagueAccountApp().run()

if __name__ == '__main__':
    main()