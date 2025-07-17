import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import pyperclip
import keyring
import pyautogui
import time
from PIL import Image, ImageTk
import io
from account_manager import AccountManager
from rank_fetcher import RankFetcher
from utils import REGION_DISPLAY_NAMES, TIER_ORDER
from models import Account
import requests
import threading

PNG_URL = "https://support-leagueoflegends.riotgames.com/hc/article_attachments/18710658817299"

class LeagueAccountApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('League Accounts')
        self.manager = AccountManager(self.root, RankFetcher())
        self.gui = LeagueAccountManagerGUI(self.root, self.manager)

    def run(self):
        self.root.mainloop()

class LeagueAccountManagerGUI:
    def __init__(self, root, manager):
        self.root = root
        self.manager = manager
        self._img_refs = []
        self._copy_counter = 0
        self._last_selected_item = None
        self.setup_gui()
        self.manager.load_accounts()
        self.display_accounts(self.manager.accounts)

    def setup_gui(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
        style.configure('TLabel', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10))
        style.configure('TLabelframe.Label', font=('Segoe UI', 11, 'bold'))
        style.map('TButton', foreground=[('active', '#222')], background=[('active', '#e0e0e0')])
        style.configure('Treeview', rowheight=26, font=('Segoe UI', 10))
        style.map('Treeview', background=[('selected', '#dbeafe')])
        style.configure('Treeview', background='#f8fafc', fieldbackground='#f8fafc', foreground='#222')
        self.root.option_add('*tearOff', False)
        self.root.configure(bg='#f3f4f6')
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.table_frame = ttk.Frame(self.root)
        self.table_frame.pack(padx=10, pady=10, fill='both', expand=True)

        self.search_var = tk.StringVar()
        search_frame = ttk.Frame(self.root)
        search_frame.pack(padx=10, pady=(0, 5), fill='x', expand=False)
        ttk.Label(search_frame, text='Search:').pack(side='left', padx=5)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.search_var.trace_add('write', lambda *_: self.on_search_change())

        columns = ('Account ID', 'Summoner Name', 'Region', 'Tier', 'Division', 'LP', 'Reached Last Season', 'Finished Last Season', 'Description')
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show='headings', height=8)
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'Description':
                self.tree.column(col, width=180, anchor='w', stretch=True)
            elif col in ['Reached Last Season', 'Finished Last Season']:
                self.tree.column(col, width=120, anchor='center', stretch=True)
            else:
                self.tree.column(col, width=100, anchor='center', stretch=True)
        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.bind('<Control-c>', self.on_tree_ctrl_c)
        self.tree.bind('<Control-Shift-V>', self.on_tree_ctrl_shift_v)

        scrollbar = ttk.Scrollbar(self.table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        self.form_frame = ttk.LabelFrame(self.root, text='Add New Account')
        self.form_frame.pack(padx=10, pady=10, fill='x', expand=False)
        for i in range(11):
            self.form_frame.columnconfigure(i, weight=1)
        ttk.Label(self.form_frame, text='Account ID:').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.account_id_entry = ttk.Entry(self.form_frame)
        self.account_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(self.form_frame, text='Summoner Name:').grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.name_entry = ttk.Entry(self.form_frame)
        self.name_entry.grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        ttk.Label(self.form_frame, text='Region:').grid(row=0, column=4, padx=5, pady=5, sticky='e')
        self.region_var = tk.StringVar(value='EUW')
        self.region_menu = ttk.OptionMenu(self.form_frame, self.region_var, 'EUW', *REGION_DISPLAY_NAMES)
        self.region_menu.grid(row=0, column=5, padx=5, pady=5, sticky='ew')
        ttk.Label(self.form_frame, text='Password:').grid(row=0, column=6, padx=5, pady=5, sticky='e')
        self.password_entry = ttk.Entry(self.form_frame, show='*')
        self.password_entry.grid(row=0, column=7, padx=5, pady=5, sticky='ew')
        ttk.Label(self.form_frame, text='Description:').grid(row=0, column=8, padx=5, pady=5, sticky='e')
        self.description_entry = ttk.Entry(self.form_frame)
        self.description_entry.grid(row=0, column=9, padx=5, pady=5, sticky='ew')
        self.add_button = ttk.Button(self.form_frame, text='Add Account', command=self.add_account)
        self.add_button.grid(row=0, column=10, padx=5, pady=5, sticky='ew')
        self.add_button.bind('<Return>', lambda event: self.add_account())

        self.multiadd_frame = ttk.Frame(self.root)
        self.multiadd_frame.pack(padx=10, pady=5, fill='x', expand=False)
        ttk.Label(self.multiadd_frame, text='Multi Add:').pack(side='left', padx=5)
        self.multiadd_text = tk.Text(self.multiadd_frame, height=3, width=60)
        self.multiadd_text.pack(side='left', padx=5, fill='x', expand=True)
        self.multiadd_placeholder = (
            "AccountID1---InGameName1#TAG---password1\n"
            "AccountID2---InGameName2#TAG---password2\n"
            "..."
        )
        def set_placeholder():
            self.multiadd_text.delete('1.0', tk.END)
            self.multiadd_text.insert('1.0', self.multiadd_placeholder)
            self.multiadd_text.config(fg='grey')
        def clear_placeholder(event=None):
            if self.multiadd_text.get('1.0', tk.END).strip() == self.multiadd_placeholder:
                self.multiadd_text.delete('1.0', tk.END)
                self.multiadd_text.config(fg='black')
        def restore_placeholder(event=None):
            if not self.multiadd_text.get('1.0', tk.END).strip():
                set_placeholder()
        set_placeholder()
        self.multiadd_text.bind('<FocusIn>', clear_placeholder)
        self.multiadd_text.bind('<FocusOut>', restore_placeholder)
        self.multiadd_button = ttk.Button(self.multiadd_frame, text='Multi Add', command=self.multi_add_accounts)
        self.multiadd_button.pack(side='left', padx=5)

        self.filter_frame = ttk.Frame(self.root)
        self.filter_frame.pack(padx=10, pady=(10,0), fill='x', expand=False)
        ttk.Label(self.filter_frame, text='Friend Elo:').pack(side='left', padx=5)
        self.friend_tier_var = tk.StringVar(value='Show All')
        self.friend_division_var = tk.StringVar(value='I')
        tier_options = ['Show All'] + TIER_ORDER[:-2]
        tier_options = [t for t in tier_options if t not in ['Grandmaster', 'Challenger']]
        self.tier_menu = ttk.OptionMenu(self.filter_frame, self.friend_tier_var, 'Show All', *tier_options, command=self.on_friend_elo_change)
        self.tier_menu.pack(side='left', padx=5)
        roman_divisions = ['I', 'II', 'III', 'IV']
        self.division_menu = ttk.OptionMenu(self.filter_frame, self.friend_division_var, 'I', *roman_divisions, command=self.on_friend_elo_change)
        self.division_menu.pack(side='left', padx=5)
        self.show_ranks_button = ttk.Button(self.filter_frame, text='Ranks Compatibilities', command=self.show_ranks_image)
        self.show_ranks_button.pack(side='right', padx=10)
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        self.tree.bind('<Delete>', lambda event: self.delete_selected_account())

        self.action_frame = ttk.Frame(self.root)
        self.action_frame.pack(in_=self.table_frame, after=self.tree, pady=(0, 10), fill='x', expand=False)
        self.copy_id_button = ttk.Button(self.action_frame, text='Copy Account ID', command=self.copy_selected_account_id)
        self.copy_id_button.pack(side='top', padx=5, pady=2, anchor='w', fill='x')
        self.copy_password_button = ttk.Button(self.action_frame, text='Copy Password', command=self.copy_selected_password)
        self.copy_password_button.pack(side='top', padx=5, pady=2, anchor='w', fill='x')
        self.refresh_button = ttk.Button(self.action_frame, text='Refresh Ranks', command=self.refresh_all_ranks)
        self.refresh_button.pack(side='top', padx=5, pady=2, anchor='w', fill='x')
        self.help_button = ttk.Button(self.action_frame, text='Shortcuts Help', command=self.show_shortcuts_help)
        self.help_button.pack(side='top', padx=5, pady=2, anchor='w', fill='x')

    def add_account(self):
        account_id = self.account_id_entry.get().strip()
        name = self.name_entry.get().strip()
        region_display = self.region_var.get().strip()
        password = self.password_entry.get().strip()
        description = self.description_entry.get().strip()
        if not account_id or not name or not region_display or not password:
            messagebox.showerror('Input Error', 'Please fill in all fields.')
            return
        from utils import REGION_MAP
        region = REGION_MAP.get(region_display)
        if not region:
            messagebox.showerror('Input Error', 'Invalid region selected.')
            return
        for acc in self.manager.accounts:
            if acc.account_id.lower() == account_id.lower() and acc.region == region:
                messagebox.showerror('Duplicate', 'This account is already added.')
                return
        keyring.set_password('LeagueAccounts', f'{region}:{account_id}', password)
        new_acc = Account(
            account_id=account_id,
            name=name,
            region=region,
            region_display=region_display,
            password=password,
            description=description
        )
        self.manager.add_account(new_acc)
        self.display_accounts(self.manager.accounts)
        self.account_id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

    def multi_add_accounts(self):
        def worker():
            region_display = self.region_var.get().strip()
            from utils import REGION_MAP
            region = REGION_MAP.get(region_display)
            while True:
                lines = self.multiadd_text.get('1.0', tk.END).strip().splitlines()
                if not lines:
                    break
                line = lines[0]
                parts = line.strip().split('---')
                if len(parts) != 3:
                    self.root.after(0, lambda: self._remove_line_from_multiadd(0))
                    continue
                account_id, name, password = [p.strip() for p in parts]
                if not account_id or not name or not password:
                    self.root.after(0, lambda: self._remove_line_from_multiadd(0))
                    continue
                if any(acc.account_id.lower() == account_id.lower() and acc.region == region for acc in self.manager.accounts):
                    self.root.after(0, lambda: self._remove_line_from_multiadd(0))
                    continue
                keyring.set_password('LeagueAccounts', f'{region}:{account_id}', password)
                new_acc = Account(
                    account_id=account_id,
                    name=name,
                    region=region,
                    region_display=region_display,
                    password=password,
                    description=''
                )
                self.manager.add_account(new_acc)
                rank_info = self.manager.rank_fetcher.fetch_rank(new_acc)
                new_acc.tier = rank_info.get('tier', 'Unranked')
                new_acc.division = rank_info.get('division', '')
                new_acc.lp = rank_info.get('lp', '')
                new_acc.reached_last_season = rank_info.get('reached_last_season', 'N/A')
                new_acc.finished_last_season = rank_info.get('finished_last_season', 'N/A')
                self.manager.save_accounts()
                self.root.after(0, lambda: self._remove_line_from_multiadd(0))
                self.root.after(0, lambda: self.display_accounts(self.manager.accounts))
        threading.Thread(target=worker, daemon=True).start()

    def _remove_line_from_multiadd(self, idx):
        lines = self.multiadd_text.get('1.0', tk.END).splitlines()
        if 0 <= idx < len(lines):
            del lines[idx]
            self.multiadd_text.delete('1.0', tk.END)
            self.multiadd_text.insert('1.0', '\n'.join(lines))

    def display_accounts(self, accounts):
        self.tree.delete(*self.tree.get_children())
        for acc in accounts:
            tier = acc.tier or 'Unranked'
            division = acc.division or ''
            lp = acc.lp or ''
            reached_last_season = acc.reached_last_season or 'N/A'
            finished_last_season = acc.finished_last_season or 'N/A'
            if not tier or tier == 'Unranked':
                tier = '...'
            if not division:
                division = '...'
            if not lp:
                lp = '...'
            self.tree.insert('', 'end', values=(
                acc.account_id,
                acc.name,
                acc.region_display,
                tier,
                division,
                lp,
                reached_last_season,
                finished_last_season,
                acc.description
            ))
        self.tree.update_idletasks()
        columns = self.tree['columns']
        padding = 18
        tree_font = tkfont.nametofont('TkDefaultFont')
        for col in columns:
            header_text = str(col)
            header_width = tree_font.measure(header_text)
            max_width = header_width
            for item in self.tree.get_children():
                cell = str(self.tree.set(item, col))
                cell_width = tree_font.measure(cell)
                if cell_width > max_width:
                    max_width = cell_width
            self.tree.column(col, width=max_width + padding)

    def on_search_change(self):
        search = self.search_var.get().strip().lower()
        if not search:
            self.display_accounts(self.manager.accounts)
            return
        filtered = [acc for acc in self.manager.accounts if search in acc.name.lower() or search in acc.account_id.lower()]
        self.display_accounts(filtered)

    def copy_selected_account_id(self):
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        values = self.tree.item(item, 'values')
        if not values or len(values) < 1:
            return
        account_id = values[0]
        pyperclip.copy(account_id)

    def copy_selected_password(self):
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        values = self.tree.item(item, 'values')
        if not values or len(values) < 3:
            return
        account_id = values[0]
        region_display = values[2]
        from utils import REGION_MAP
        region = REGION_MAP.get(region_display, region_display)
        password = keyring.get_password('LeagueAccounts', f'{region}:{account_id}')
        if password:
            pyperclip.copy(password)

    def refresh_all_ranks(self):
        def worker():
            for idx, acc in enumerate(self.manager.accounts):
                # Find the row in the tree corresponding to this account
                for item in self.tree.get_children():
                    values = self.tree.item(item, 'values')
                    if values and values[0] == acc.account_id and values[2] == acc.region_display:
                        # Highlight the row in grey
                        self.root.after(0, lambda item=item: self.tree.item(item, tags=('refreshing',)))
                        self.root.after(0, lambda: self.tree.tag_configure('refreshing', background='#d1d5db'))
                        break
                # Fetch new rank info
                rank_info = self.manager.rank_fetcher.fetch_rank(acc)
                acc.tier = rank_info.get('tier', 'Unranked')
                acc.division = rank_info.get('division', '')
                acc.lp = rank_info.get('lp', '')
                acc.reached_last_season = rank_info.get('reached_last_season', 'N/A')
                acc.finished_last_season = rank_info.get('finished_last_season', 'N/A')
                self.manager.save_accounts()
                # Update the row in the tree with new rank info
                for item in self.tree.get_children():
                    values = self.tree.item(item, 'values')
                    if values and values[0] == acc.account_id and values[2] == acc.region_display:
                        new_values = list(values)
                        new_values[3] = acc.tier or '...'
                        new_values[4] = acc.division or '...'
                        new_values[5] = acc.lp or '...'
                        new_values[6] = acc.reached_last_season or 'N/A'
                        new_values[7] = acc.finished_last_season or 'N/A'
                        self.root.after(0, lambda item=item, vals=new_values: self.tree.item(item, values=vals))
                        # Remove highlight after update
                        self.root.after(0, lambda item=item: self.tree.item(item, tags=()))
                        break
        threading.Thread(target=worker, daemon=True).start()

    def delete_selected_account(self):
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        values = self.tree.item(item, 'values')
        if not values or len(values) < 3:
            return
        account_id = values[0]
        region_display = values[2]
        from utils import REGION_MAP
        region = REGION_MAP.get(region_display, region_display)
        # Find the next item to select
        all_items = self.tree.get_children()
        idx = all_items.index(item)
        self.manager.delete_account(account_id, region)
        self.display_accounts(self.manager.accounts)
        # Select next item if possible, else previous
        all_items = self.tree.get_children()
        if all_items:
            next_idx = min(idx, len(all_items)-1)
            self.tree.selection_set(all_items[next_idx])
            self.tree.focus(all_items[next_idx])

    def on_tree_double_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        col_num = int(col_id.replace('#', '')) - 1
        if col_num not in [1, 8]:
            return
        bbox = self.tree.bbox(row_id, col_id)
        if not bbox:
            return
        x, y, width, height = bbox
        values = list(self.tree.item(row_id, 'values'))
        current_value = values[col_num] if len(values) > col_num else ""
        entry = tk.Entry(self.tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, current_value)
        entry.focus_set()
        def save_edit(event=None):
            new_value = entry.get()
            entry.destroy()
            values[col_num] = new_value
            self.tree.item(row_id, values=values)
            account_id = values[0]
            region_display = values[2]
            for acc in self.manager.accounts:
                if acc.account_id == account_id and acc.region_display == region_display:
                    if col_num == 1:
                        acc.name = new_value
                    elif col_num == 8:
                        acc.description = new_value
                    break
            self.manager.save_accounts()
        entry.bind('<Return>', save_edit)
        entry.bind('<FocusOut>', save_edit)

    def on_friend_elo_change(self, *_):
        tier = self.friend_tier_var.get()
        division = self.friend_division_var.get()
        if tier == 'Show All' or not tier:
            self.display_accounts(self.manager.accounts)
            return
        filtered = [acc for acc in self.manager.accounts if self.can_play_with(acc, tier, division)]
        self.display_accounts(filtered)

    def can_play_with(self, acc, friend_tier, friend_division):
        from utils import TIER_ORDER
        def division_to_int(division):
            roman_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4}
            if isinstance(division, str):
                d = division.strip().upper()
                if d in roman_map:
                    return roman_map[d]
                if d in ['1', '2', '3', '4']:
                    return int(d)
            return None
        acc_tier = acc.tier.capitalize()
        acc_div = str(acc.division).upper()
        friend_tier = friend_tier.capitalize()
        friend_div = str(friend_division).upper()
        if friend_tier == 'Master':
            if acc_tier == 'Master':
                return True
            if acc_tier == 'Diamond' and division_to_int(acc_div) == 1:
                return True
            return False
        if friend_tier == 'Diamond':
            acc_div_num = division_to_int(acc_div)
            friend_div_num = division_to_int(friend_div)
            if acc_tier == 'Diamond' and friend_div_num is not None and acc_div_num is not None:
                if abs(acc_div_num - friend_div_num) <= 2:
                    return True
                if friend_div_num == 1 and acc_tier == 'Master':
                    return True
                if friend_div_num == 4 and acc_tier == 'Emerald' and acc_div_num == 1:
                    return True
            if acc_tier == 'Emerald' and acc_div_num == 1 and friend_div_num == 4:
                return True
            if acc_tier == 'Master' and friend_div_num == 1:
                return True
            return False
        if friend_tier == 'Emerald':
            acc_div_num = division_to_int(acc_div)
            friend_div_num = division_to_int(friend_div)
            if acc_tier in ['Emerald', 'Platinum']:
                return True
            if friend_div_num == 1 and acc_tier == 'Diamond' and acc_div_num == 4:
                return True
            return False
        if friend_tier == 'Platinum':
            return acc_tier in ['Platinum', 'Emerald', 'Gold']
        if friend_tier == 'Iron':
            return acc_tier in ['Iron', 'Bronze', 'Silver']
        if friend_tier in ['Bronze', 'Silver', 'Gold']:
            idx = TIER_ORDER.index(friend_tier)
            allowed = set()
            if idx > 0:
                allowed.add(TIER_ORDER[idx-1])
            allowed.add(friend_tier)
            if idx < len(TIER_ORDER)-3:
                allowed.add(TIER_ORDER[idx+1])
            return acc_tier in allowed
        return False

    def show_ranks_image(self):
        try:
            response = requests.get(PNG_URL)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))
            img_window = tk.Toplevel(self.root)
            img_window.title('Ranks Compatibilities')
            img_window.resizable(False, False)
            screen_w = img_window.winfo_screenwidth()
            screen_h = img_window.winfo_screenheight()
            max_w, max_h = screen_w - 100, screen_h - 100
            w, h = img.size
            if hasattr(Image, 'Resampling'):
                _RESAMPLE = Image.Resampling.LANCZOS
            else:
                _RESAMPLE = Image.LANCZOS
            if w > max_w or h > max_h:
                scale = min(max_w / w, max_h / h)
                img = img.resize((int(w * scale), int(h * scale)), _RESAMPLE)
            tk_img = ImageTk.PhotoImage(img)
            label = tk.Label(img_window, image=tk_img)
            label.pack()
            self._img_refs.append(tk_img)
            img_window.update_idletasks()
            win_w = img_window.winfo_width()
            win_h = img_window.winfo_height()
            screen_w = img_window.winfo_screenwidth()
            screen_h = img_window.winfo_screenheight()
            x = (screen_w // 2) - (win_w // 2)
            y = (screen_h // 2) - (win_h // 2)
            y = max(0, y - int(screen_h * 0.15))
            img_window.geometry(f"{win_w}x{win_h}+{x}+{y}")
        except Exception as e:
            messagebox.showerror('Error', f'Could not open ranks image: {e}')

    def on_tree_ctrl_c(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        if self._last_selected_item != item:
            self._copy_counter = 0
            self._last_selected_item = item
        values = self.tree.item(item, 'values')
        if not values or len(values) < 3:
            return
        if self._copy_counter % 2 == 0:
            account_id = values[0]
            pyperclip.copy(account_id)
        else:
            account_id = values[0]
            region_display = values[2]
            from utils import REGION_MAP
            region = REGION_MAP.get(region_display, region_display)
            password = keyring.get_password('LeagueAccounts', f'{region}:{account_id}')
            if password:
                pyperclip.copy(password)
        self._copy_counter += 1

    def on_tree_ctrl_shift_v(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        values = self.tree.item(item, 'values')
        if not values or len(values) < 3:
            return
        account_id = values[0]
        region_display = values[2]
        from utils import REGION_MAP
        region = REGION_MAP.get(region_display, region_display)
        password = keyring.get_password('LeagueAccounts', f'{region}:{account_id}')
        self.root.after(100, lambda: self._do_autotype(account_id, password))

    def _do_autotype(self, account_id, password):
        pyautogui.keyDown('alt')
        pyautogui.press('tab')
        pyautogui.keyUp('alt')
        time.sleep(0.2)
        pyperclip.copy(str(account_id))
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('tab')
        if password:
            pyperclip.copy(str(password))
            pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')

    def show_shortcuts_help(self):
        help_text = (
            "Keyboard Shortcuts:\n"
            "\n"
            "- Ctrl+C: Copy Account ID (press again to copy Password)\n"
            "- Ctrl+Shift+V: Auto-type Account ID and Password into another window\n"
            "- Delete: Delete selected account\n"
            "- Double-click Summoner Name or Description: Edit in place\n"
            "- Enter (on Add Account button): Add new account\n"
            "\n"
            "Other Tips:\n"
            "- Use the search bar to filter accounts by name or ID.\n"
            "- Use the Friend Elo filter to show compatible accounts.\n"
        )
        win = tk.Toplevel(self.root)
        win.title('Shortcuts Help')
        win.geometry('420x260')
        win.resizable(False, False)
        text = tk.Text(win, wrap='word', font=('Segoe UI', 10), bg='#f8fafc', relief='flat', borderwidth=0)
        text.insert('1.0', help_text)
        text.config(state='disabled')
        text.pack(expand=True, fill='both', padx=12, pady=12)
        win.transient(self.root)
        win.grab_set()
        win.focus_set() 