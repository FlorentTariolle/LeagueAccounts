"""
LeagueAccounts Main Entry Point
"""
import sys

# Lazy import to reduce startup time
def main():
    # Fix DPI awareness on Windows to prevent blur
    if sys.platform == 'win32':
        try:
            from ctypes import windll
            # Set DPI awareness to prevent blurry UI on high-DPI displays
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            # Fall back to older method if available
            try:
                windll.user32.SetProcessDPIAware()
            except Exception:
                pass  # If neither works, proceed without DPI awareness
    
    from leagueaccounts.gui import LeagueAccountApp
    LeagueAccountApp().run()

if __name__ == '__main__':
    main()