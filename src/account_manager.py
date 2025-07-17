import keyring
import json
import os
from utils import get_accounts_file, rank_sort_key
from models import Account

class AccountManager:
    def __init__(self, root, rank_fetcher):
        self.root = root
        self.rank_fetcher = rank_fetcher
        self.accounts = []
        self.accounts_file = get_accounts_file()

    def load_accounts(self):
        self.accounts.clear()
        if os.path.exists(self.accounts_file):
            with open(self.accounts_file, "r", encoding="utf-8") as f:
                loaded_accounts = json.load(f)
                for acc in loaded_accounts:
                    region = acc.get('region')
                    account_id = acc.get('account_id')
                    password = keyring.get_password('LeagueAccounts', f'{region}:{account_id}') or ''
                    acc_obj = Account(
                        account_id=acc.get('account_id', ''),
                        name=acc.get('name', ''),
                        region=region,
                        region_display=acc.get('region_display', region),
                        password=password,
                        description=acc.get('description', ''),
                        tier=acc.get('tier', 'Unranked'),
                        division=acc.get('division', ''),
                        lp=acc.get('lp', ''),
                        reached_last_season=acc.get('reached_last_season', 'N/A'),
                        finished_last_season=acc.get('finished_last_season', 'N/A')
                    )
                    self.accounts.append(acc_obj)
        self.accounts.sort(key=lambda a: rank_sort_key(a.tier, a.division, a.lp))

    def save_accounts(self):
        to_save = []
        for acc in self.accounts:
            acc_dict = acc.__dict__.copy()
            if 'password' in acc_dict:
                del acc_dict['password']
            to_save.append(acc_dict)
        with open(self.accounts_file, "w", encoding="utf-8") as f:
            json.dump(to_save, f, indent=2)

    def add_account(self, account: Account):
        self.accounts.append(account)
        self.accounts.sort(key=lambda a: rank_sort_key(a.tier, a.division, a.lp))
        self.save_accounts()

    def delete_account(self, account_id, region):
        self.accounts = [acc for acc in self.accounts if not (acc.account_id == account_id and acc.region == region)]
        try:
            keyring.delete_password('LeagueAccounts', f'{region}:{account_id}')
        except Exception:
            pass
        self.save_accounts()

    def refresh_ranks(self):
        for acc in self.accounts:
            rank_info = self.rank_fetcher.fetch_rank(acc)
            acc.tier = rank_info.get('tier', 'Unranked')
            acc.division = rank_info.get('division', '')
            acc.lp = rank_info.get('lp', '')
            acc.reached_last_season = rank_info.get('reached_last_season', 'N/A')
            acc.finished_last_season = rank_info.get('finished_last_season', 'N/A')
        self.accounts.sort(key=lambda a: rank_sort_key(a.tier, a.division, a.lp))
        self.save_accounts() 