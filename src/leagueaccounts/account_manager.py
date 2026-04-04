import keyring
from keyring.backends.Windows import WinVaultKeyring
keyring.set_keyring(WinVaultKeyring())
import json
import os
from dataclasses import asdict
from .utils import get_accounts_file, rank_sort_key
from .models import Account

KEYRING_SERVICE = 'LeagueAccounts'

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
                    try:
                        password = keyring.get_password(KEYRING_SERVICE, f'{region}:{account_id}') or ''
                    except Exception:
                        password = ''
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
                        level=acc.get('level', ''),
                        reached_last_season=acc.get('reached_last_season', 'N/A'),
                        finished_last_season=acc.get('finished_last_season', 'N/A')
                    )
                    self.accounts.append(acc_obj)
        self.accounts.sort(key=lambda a: rank_sort_key(a.tier, a.division, a.lp))

    def save_accounts(self):
        try:
            to_save = []
            for acc in self.accounts:
                acc_dict = acc.__dict__.copy()
                if 'password' in acc_dict:
                    del acc_dict['password']
                to_save.append(acc_dict)
            with open(self.accounts_file, "w", encoding="utf-8") as f:
                json.dump(to_save, f, indent=2)
        except PermissionError as e:
            import tkinter.messagebox as mb
            mb.showerror('Permission Error', 
                        f'Cannot save accounts file. Permission denied.\n\n'
                        f'File: {self.accounts_file}\n'
                        f'Error: {str(e)}\n\n'
                        f'Please check your user permissions or run as administrator.')
            raise
        except Exception as e:
            import tkinter.messagebox as mb
            mb.showerror('Save Error', 
                        f'Failed to save accounts file.\n\n'
                        f'File: {self.accounts_file}\n'
                        f'Error: {str(e)}')
            raise

    def add_account(self, account: Account):
        self.accounts.append(account)
        self.accounts.sort(key=lambda a: rank_sort_key(a.tier, a.division, a.lp))
        self.save_accounts()

    def delete_account(self, account_id, region):
        self.accounts = [acc for acc in self.accounts if not (acc.account_id == account_id and acc.region == region)]
        try:
            keyring.delete_password(KEYRING_SERVICE, f'{region}:{account_id}')
        except Exception:
            pass
        self.save_accounts()

    def refresh_ranks(self):
        for acc in self.accounts:
            rank_info = self.rank_fetcher.fetch_rank(acc)
            acc.tier = rank_info.get('tier', 'Unranked')
            acc.division = rank_info.get('division', '')
            acc.lp = rank_info.get('lp', '')
            acc.level = rank_info.get('level', '')
            acc.reached_last_season = rank_info.get('reached_last_season', 'N/A')
            acc.finished_last_season = rank_info.get('finished_last_season', 'N/A')
        self.accounts.sort(key=lambda a: rank_sort_key(a.tier, a.division, a.lp))
        self.save_accounts()

    def export_accounts(self):
        """Export all accounts including passwords as a JSON string."""
        export_data = []
        for acc in self.accounts:
            acc_dict = asdict(acc)
            # Use in-memory password; fall back to keyring if empty
            if not acc_dict.get('password'):
                try:
                    acc_dict['password'] = keyring.get_password(
                        KEYRING_SERVICE, f'{acc.region}:{acc.account_id}'
                    ) or ''
                except Exception:
                    acc_dict['password'] = ''
            # Also update in-memory account if we recovered the password
            if acc_dict['password'] and not acc.password:
                acc.password = acc_dict['password']
            export_data.append(acc_dict)
        return json.dumps(export_data, indent=2)

    def import_accounts(self, json_str):
        """Import accounts from a JSON string. Returns (added_count, skipped_count)."""
        data = json.loads(json_str)
        if not isinstance(data, list):
            raise ValueError("Expected a JSON array of accounts.")
        added = 0
        skipped = 0
        for acc_dict in data:
            account_id = acc_dict.get('account_id', '').strip()
            region = acc_dict.get('region', '').strip()
            if not account_id or not region:
                skipped += 1
                continue
            # Skip duplicates
            if any(a.account_id.lower() == account_id.lower() and a.region == region
                   for a in self.accounts):
                skipped += 1
                continue
            password = acc_dict.pop('password', '')
            acc = Account(
                account_id=account_id,
                name=acc_dict.get('name', ''),
                region=region,
                region_display=acc_dict.get('region_display', region),
                description=acc_dict.get('description', ''),
                tier=acc_dict.get('tier', 'Unranked'),
                division=acc_dict.get('division', ''),
                lp=acc_dict.get('lp', ''),
                level=acc_dict.get('level', ''),
                reached_last_season=acc_dict.get('reached_last_season', 'N/A'),
                finished_last_season=acc_dict.get('finished_last_season', 'N/A'),
                password=password
            )
            if password:
                try:
                    keyring.set_password(KEYRING_SERVICE, f'{region}:{account_id}', password)
                except Exception:
                    pass
            self.accounts.append(acc)
            added += 1
        self.accounts.sort(key=lambda a: rank_sort_key(a.tier, a.division, a.lp))
        if added > 0:
            self.save_accounts()
        return added, skipped