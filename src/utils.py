import os

REGION_MAP = {
    'EUW': 'euw',
    'EUNE': 'eune',
    'NA': 'na',
    'KR': 'kr',
    'BR': 'br',
    'JP': 'jp',
    'OCE': 'oce',
    'RU': 'ru',
    'TR': 'tr',
    'LAN': 'lan',
    'LAS': 'las',
}
REGION_DISPLAY_NAMES = list(REGION_MAP.keys())

TIER_ORDER = [
    'Challenger', 'Grandmaster', 'Master', 'Diamond', 'Emerald', 'Platinum', 'Gold', 'Silver', 'Bronze', 'Iron', 'Unranked', 'Error'
]
DIVISION_ORDER = ['1', '2', '3', '4', 'I', 'II', 'III', 'IV', '']

def rank_sort_key(tier, division, lp):
    try:
        tier_idx = TIER_ORDER.index(tier.capitalize())
    except ValueError:
        tier_idx = len(TIER_ORDER)
    division_str = str(division).upper()
    if division_str in ['I', 'II', 'III', 'IV']:
        division_idx = ['I', 'II', 'III', 'IV'].index(division_str)
    elif division_str in ['1', '2', '3', '4']:
        division_idx = int(division_str) - 1
    else:
        division_idx = len(DIVISION_ORDER)
    try:
        lp_val = int(lp)
    except Exception:
        lp_val = 0
    return (tier_idx, division_idx, -lp_val)

def get_accounts_file():
    appdata = os.environ.get('APPDATA') or os.path.expanduser('~')
    folder = os.path.join(appdata, 'LeagueAccounts')
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, 'league_accounts.json') 