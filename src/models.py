from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Account:
    account_id: str
    name: str
    region: str
    region_display: str
    password: str = ''
    description: str = ''
    tier: str = 'Unranked'
    division: str = ''
    lp: str = ''
    level: str = ''
    reached_last_season: str = 'N/A'
    finished_last_season: str = 'N/A' 