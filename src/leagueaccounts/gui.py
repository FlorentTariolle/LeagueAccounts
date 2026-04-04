import json
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import threading
import customtkinter as ctk

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Lazy imports for heavy dependencies
def _lazy_imports():
    global pyperclip, pyautogui, time, Image, ImageTk
    import pyperclip
    try:
        import pyautogui
    except ImportError as e:
        print(f"Warning: pyautogui import failed: {e}")
        pyautogui = None
    import time
    from PIL import Image, ImageTk

from pathlib import Path
import sys

from .account_manager import AccountManager, KEYRING_SERVICE
from . import windows_credential as cred
from .rank_fetcher import RankFetcher
from .utils import REGION_DISPLAY_NAMES, TIER_ORDER, REGION_MAP
from .models import Account

# Handle PyInstaller bundled paths
def get_asset_path(relative_path):
    """Get path to asset, works for dev and PyInstaller bundle"""
    if getattr(sys, 'frozen', False):
        # Running as bundled exe
        base_path = Path(sys._MEIPASS)
    else:
        # Running in development
        base_path = Path(__file__).parent.parent.parent
    return base_path / relative_path

# Path to local assets
RANKS_IMAGE_PATH = get_asset_path("assets/ranks_compatibilities.webp")
WINDOW_ICON_PATH = get_asset_path("assets/icons/blue_icon.ico")

# Dark theme colors
COLORS = {
    'bg_main': '#1a1a1a',
    'bg_card': '#2b2b2b',
    'text_primary': '#DCE4EE',
    'text_secondary': '#888888',
    'accent': '#1f6aa5',
    'border': '#3d3d3d',
    'tree_bg': '#2b2b2b',
    'tree_selected': '#1f538d',
    'tree_heading': '#3d3d3d',
}

class LeagueAccountApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title('League Accounts')
        # Set window icon
        if WINDOW_ICON_PATH.exists():
            self.root.iconbitmap(str(WINDOW_ICON_PATH))
        self.manager = AccountManager(self.root, RankFetcher())
        self.gui = LeagueAccountManagerGUI(self.root, self.manager)
        # Maximize after GUI is set up
        self.root.after(50, lambda: self.root.state('zoomed'))

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
        # Defer account loading to after GUI is ready
        self.root.after(100, self._delayed_init)

    def _delayed_init(self):
        """Initialize heavy operations after GUI is ready"""
        self.manager.load_accounts()
        self.display_accounts(self.manager.accounts)

    def setup_gui(self):
        # Configure dark theme for ttk.Treeview
        style = ttk.Style()
        style.theme_use('clam')

        # Treeview dark styling
        style.configure('Treeview',
            background=COLORS['tree_bg'],
            foreground=COLORS['text_primary'],
            fieldbackground=COLORS['tree_bg'],
            rowheight=28,
            font=('Segoe UI', 10)
        )
        style.configure('Treeview.Heading',
            background=COLORS['tree_heading'],
            foreground=COLORS['text_primary'],
            font=('Segoe UI', 10, 'bold'),
            relief='flat'
        )
        style.map('Treeview',
            background=[('selected', COLORS['tree_selected'])],
            foreground=[('selected', COLORS['text_primary'])]
        )
        style.map('Treeview.Heading',
            background=[('active', COLORS['border'])]
        )

        # Configure root window
        self.root.configure(fg_color=COLORS['bg_main'])

        # Main container with padding
        main_container = ctk.CTkFrame(self.root, fg_color=COLORS['bg_main'])
        main_container.pack(fill='both', expand=True, padx=15, pady=15)

        # Table frame with Treeview
        self.table_frame = ctk.CTkFrame(main_container, fg_color=COLORS['bg_card'], corner_radius=10)
        self.table_frame.pack(padx=0, pady=(0, 15), fill='both', expand=True)

        # Inner padding for table frame
        table_inner = ctk.CTkFrame(self.table_frame, fg_color='transparent')
        table_inner.pack(fill='both', expand=True, padx=10, pady=10)

        # Search bar
        search_frame = ctk.CTkFrame(table_inner, fg_color='transparent')
        search_frame.pack(fill='x', pady=(0, 10))

        ctk.CTkLabel(search_frame, text='Search:', text_color=COLORS['text_primary']).pack(side='left', padx=(0, 10))
        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=300,
                                    placeholder_text="Filter by name or account ID...")
        search_entry.pack(side='left', fill='x', expand=True)
        self.search_var.trace_add('write', lambda *_: self.on_search_change())

        # Main row container for tree + actions
        tree_row = ctk.CTkFrame(table_inner, fg_color='transparent')
        tree_row.pack(fill='both', expand=True)

        # Action buttons frame (side panel) - pack FIRST so it's on the right
        self.action_frame = ctk.CTkFrame(tree_row, fg_color='transparent', width=150)
        self.action_frame.pack(side='right', fill='y', padx=(10, 0))
        self.action_frame.pack_propagate(False)  # Keep fixed width

        ctk.CTkLabel(self.action_frame, text='Actions', font=('Segoe UI', 12, 'bold'),
                     text_color=COLORS['text_primary']).pack(pady=(0, 10))

        self.copy_id_button = ctk.CTkButton(self.action_frame, text='Copy Account ID',
                                            command=self.copy_selected_account_id, width=140)
        self.copy_id_button.pack(pady=5)

        self.copy_password_button = ctk.CTkButton(self.action_frame, text='Copy Password',
                                                  command=self.copy_selected_password, width=140)
        self.copy_password_button.pack(pady=5)

        self.refresh_button = ctk.CTkButton(self.action_frame, text='Refresh Ranks',
                                            command=self.refresh_all_ranks, width=140)
        self.refresh_button.pack(pady=5)

        self.export_button = ctk.CTkButton(self.action_frame, text='Export Data',
                                            command=self.export_data, width=140)
        self.export_button.pack(pady=5)

        self.import_button = ctk.CTkButton(self.action_frame, text='Import Data',
                                            command=self.import_data, width=140)
        self.import_button.pack(pady=5)

        self.help_button = ctk.CTkButton(self.action_frame, text='Shortcuts Help',
                                         command=self.show_shortcuts_help, width=140)
        self.help_button.pack(pady=5)

        # Treeview container - pack AFTER actions so it fills remaining space
        tree_container = ctk.CTkFrame(tree_row, fg_color='transparent')
        tree_container.pack(side='left', fill='both', expand=True)

        columns = ('Account ID', 'Summoner Name', 'Region', 'Level', 'Tier', 'Division', 'LP', 'Reached Last Season', 'Finished Last Season', 'Description')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'Description':
                self.tree.column(col, width=180, anchor='w', stretch=True)
            elif col in ['Reached Last Season', 'Finished Last Season']:
                self.tree.column(col, width=120, anchor='center', stretch=True)
            elif col == 'Level':
                self.tree.column(col, width=60, anchor='center', stretch=True)
            else:
                self.tree.column(col, width=100, anchor='center', stretch=True)
        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.bind('<Control-c>', self.on_tree_ctrl_c)
        self.tree.bind('<Control-Shift-V>', self.on_tree_ctrl_shift_v)

        # Custom scrollbar for treeview
        scrollbar = ctk.CTkScrollbar(tree_container, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Add New Account section
        self.form_frame = ctk.CTkFrame(main_container, fg_color=COLORS['bg_card'], corner_radius=10)
        self.form_frame.pack(padx=0, pady=(0, 15), fill='x')

        form_inner = ctk.CTkFrame(self.form_frame, fg_color='transparent')
        form_inner.pack(fill='x', padx=15, pady=15)

        ctk.CTkLabel(form_inner, text='Add New Account', font=('Segoe UI', 12, 'bold'),
                     text_color=COLORS['text_primary']).pack(anchor='w', pady=(0, 10))

        # Form fields row
        form_row = ctk.CTkFrame(form_inner, fg_color='transparent')
        form_row.pack(fill='x')

        # Account ID
        field1 = ctk.CTkFrame(form_row, fg_color='transparent')
        field1.pack(side='left', padx=(0, 10))
        ctk.CTkLabel(field1, text='Account ID:', text_color=COLORS['text_secondary']).pack(anchor='w')
        self.account_id_entry = ctk.CTkEntry(field1, width=120)
        self.account_id_entry.pack()

        # Summoner Name
        field2 = ctk.CTkFrame(form_row, fg_color='transparent')
        field2.pack(side='left', padx=(0, 10))
        ctk.CTkLabel(field2, text='Summoner Name:', text_color=COLORS['text_secondary']).pack(anchor='w')
        self.name_entry = ctk.CTkEntry(field2, width=150)
        self.name_entry.pack()

        # Region
        field3 = ctk.CTkFrame(form_row, fg_color='transparent')
        field3.pack(side='left', padx=(0, 10))
        ctk.CTkLabel(field3, text='Region:', text_color=COLORS['text_secondary']).pack(anchor='w')
        self.region_var = tk.StringVar(value='EUW')
        self.region_menu = ctk.CTkOptionMenu(field3, variable=self.region_var,
                                             values=list(REGION_DISPLAY_NAMES), width=100)
        self.region_menu.pack()

        # Password
        field4 = ctk.CTkFrame(form_row, fg_color='transparent')
        field4.pack(side='left', padx=(0, 10))
        ctk.CTkLabel(field4, text='Password:', text_color=COLORS['text_secondary']).pack(anchor='w')
        self.password_entry = ctk.CTkEntry(field4, width=120, show='*')
        self.password_entry.pack()

        # Description
        field5 = ctk.CTkFrame(form_row, fg_color='transparent')
        field5.pack(side='left', padx=(0, 10), fill='x', expand=True)
        ctk.CTkLabel(field5, text='Description:', text_color=COLORS['text_secondary']).pack(anchor='w')
        self.description_entry = ctk.CTkEntry(field5)
        self.description_entry.pack(fill='x')

        # Add button
        self.add_button = ctk.CTkButton(form_row, text='Add Account', command=self.add_account, width=120)
        self.add_button.pack(side='left', padx=(10, 0), pady=(18, 0))

        # Multi-add section
        self.multiadd_frame = ctk.CTkFrame(main_container, fg_color=COLORS['bg_card'], corner_radius=10)
        self.multiadd_frame.pack(padx=0, pady=(0, 15), fill='x')

        multiadd_inner = ctk.CTkFrame(self.multiadd_frame, fg_color='transparent')
        multiadd_inner.pack(fill='x', padx=15, pady=15)

        ctk.CTkLabel(multiadd_inner, text='Multi Add', font=('Segoe UI', 12, 'bold'),
                     text_color=COLORS['text_primary']).pack(anchor='w', pady=(0, 10))

        multiadd_row = ctk.CTkFrame(multiadd_inner, fg_color='transparent')
        multiadd_row.pack(fill='x')

        self.multiadd_text = ctk.CTkTextbox(multiadd_row, height=70, width=500,
                                            fg_color=COLORS['bg_main'], text_color=COLORS['text_primary'])
        self.multiadd_text.pack(side='left', fill='x', expand=True, padx=(0, 10))

        self.multiadd_placeholder = (
            "AccountID1--InGameName1#TAG--password1\n"
            "AccountID2--InGameName2#TAG--password2\n"
            "..."
        )

        def set_placeholder():
            self.multiadd_text.delete('1.0', tk.END)
            self.multiadd_text.insert('1.0', self.multiadd_placeholder)
            self.multiadd_text.configure(text_color=COLORS['text_secondary'])

        def clear_placeholder(event=None):
            if self.multiadd_text.get('1.0', tk.END).strip() == self.multiadd_placeholder:
                self.multiadd_text.delete('1.0', tk.END)
                self.multiadd_text.configure(text_color=COLORS['text_primary'])

        def restore_placeholder(event=None):
            if not self.multiadd_text.get('1.0', tk.END).strip():
                set_placeholder()

        set_placeholder()
        self.multiadd_text.bind('<FocusIn>', clear_placeholder)
        self.multiadd_text.bind('<FocusOut>', restore_placeholder)

        self.multiadd_button = ctk.CTkButton(multiadd_row, text='Multi Add',
                                             command=self.multi_add_accounts, width=120)
        self.multiadd_button.pack(side='left')

        # Filter section
        self.filter_frame = ctk.CTkFrame(main_container, fg_color=COLORS['bg_card'], corner_radius=10)
        self.filter_frame.pack(padx=0, pady=0, fill='x')

        filter_inner = ctk.CTkFrame(self.filter_frame, fg_color='transparent')
        filter_inner.pack(fill='x', padx=15, pady=15)

        filter_row = ctk.CTkFrame(filter_inner, fg_color='transparent')
        filter_row.pack(fill='x')

        ctk.CTkLabel(filter_row, text='Friend Elo:', text_color=COLORS['text_primary']).pack(side='left', padx=(0, 10))

        self.friend_tier_var = tk.StringVar(value='Show All')
        self.friend_division_var = tk.StringVar(value='I')
        tier_options = ['Show All'] + TIER_ORDER[:-2]
        tier_options = [t for t in tier_options if t not in ['Grandmaster', 'Challenger']]

        self.tier_menu = ctk.CTkOptionMenu(filter_row, variable=self.friend_tier_var,
                                           values=tier_options, command=self.on_friend_elo_change, width=120)
        self.tier_menu.pack(side='left', padx=(0, 10))

        roman_divisions = ['I', 'II', 'III', 'IV']
        self.division_menu = ctk.CTkOptionMenu(filter_row, variable=self.friend_division_var,
                                               values=roman_divisions, command=self.on_friend_elo_change, width=80)
        self.division_menu.pack(side='left')

        self.show_ranks_button = ctk.CTkButton(filter_row, text='Ranks Compatibilities',
                                               command=self.show_ranks_image, width=160)
        self.show_ranks_button.pack(side='right')

        # Bind tree events
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        self.tree.bind('<Delete>', lambda event: self.delete_selected_account())

    def add_account(self):
        _lazy_imports()
        account_id = self.account_id_entry.get().strip()
        name = self.name_entry.get().strip()
        region_display = self.region_var.get().strip()
        password = self.password_entry.get().strip()
        description = self.description_entry.get().strip()


        if not account_id or not name or not region_display or not password:
            messagebox.showerror('Input Error', 'Please fill in all fields.')
            return
        region = REGION_MAP.get(region_display)
        if not region:
            messagebox.showerror('Input Error', 'Invalid region selected.')
            return
        for acc in self.manager.accounts:
            if acc.account_id.lower() == account_id.lower() and acc.region == region:
                messagebox.showerror('Duplicate', 'This account is already added.')
                return

        try:
            _lazy_imports()
            cred.set_password(KEYRING_SERVICE, f'{region}:{account_id}', password)

            new_acc = Account(
                account_id=account_id,
                name=name,
                region=region,
                region_display=region_display,
                password=password,
                description=description
            )
            self.manager.add_account(new_acc)

        except Exception as e:
            messagebox.showerror('Add Account Error',
                               f'Failed to add account.\n\n'
                               f'Error: {str(e)}\n\n'
                               f'This might be a Windows Credential Manager issue. Please check:\n'
                               f'1. Windows Credential Manager access\n'
                               f'2. User permissions\n'
                               f'3. Try running as administrator')
            return

        # Fetch rank information for the new account
        def fetch_rank_worker():
            try:
                rank_info = self.manager.rank_fetcher.fetch_rank(new_acc)
                new_acc.tier = rank_info.get('tier', 'Unranked')
                new_acc.division = rank_info.get('division', '')
                new_acc.lp = rank_info.get('lp', '')
                new_acc.level = rank_info.get('level', '')
                new_acc.reached_last_season = rank_info.get('reached_last_season', 'N/A')
                new_acc.finished_last_season = rank_info.get('finished_last_season', 'N/A')
                self.manager.save_accounts()
                # Update the display in the main thread
                self.root.after(0, lambda: self.display_accounts(self.manager.accounts))
            except Exception as e:
                print(f"Error fetching rank for {account_id}: {e}")

        threading.Thread(target=fetch_rank_worker, daemon=True).start()

        # Display accounts immediately (with placeholder rank info)
        self.display_accounts(self.manager.accounts)
        self.account_id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

    def multi_add_accounts(self):
        def worker():
            _lazy_imports()
            region_display = self.region_var.get().strip()
            region = REGION_MAP.get(region_display)

            # Get the text content, filtering out placeholder text
            text_content = self.multiadd_text.get('1.0', tk.END).strip()

            # Check if content is empty or just placeholder
            if not text_content:
                self.root.after(0, lambda: messagebox.showwarning('Input Error', 'Please enter account data in the multi-add field.'))
                return

            # Check if it's the placeholder text (compare without trailing newlines)
            placeholder_stripped = self.multiadd_placeholder.strip()
            if text_content == placeholder_stripped:
                self.root.after(0, lambda: messagebox.showwarning('Input Error', 'Please enter account data in the multi-add field.'))
                return

            lines = text_content.splitlines()
            processed_count = 0
            error_count = 0

            # Process accounts one by one, removing each line as it's processed
            while True:
                # Get current text content (it may have changed as lines are removed)
                current_text = self.multiadd_text.get('1.0', tk.END).strip()
                if not current_text or current_text == self.multiadd_placeholder.strip():
                    break

                current_lines = current_text.splitlines()
                if not current_lines:
                    break

                # Process the first line
                line = current_lines[0].strip()
                if not line:  # Skip empty lines
                    self.root.after(0, lambda: self._remove_line_from_multiadd(0))
                    continue

                # Try both --- and -- as separators
                if '---' in line:
                    parts = line.split('---')
                else:
                    parts = line.split('--')
                if len(parts) != 3:
                    error_count += 1
                    self.root.after(0, lambda: self._remove_line_from_multiadd(0))
                    continue

                account_id, name, password = [p.strip() for p in parts]
                if not account_id or not name or not password:
                    error_count += 1
                    self.root.after(0, lambda: self._remove_line_from_multiadd(0))
                    continue

                # Check for duplicates
                if any(acc.account_id.lower() == account_id.lower() and acc.region == region for acc in self.manager.accounts):
                    error_count += 1
                    self.root.after(0, lambda: self._remove_line_from_multiadd(0))
                    continue

                try:
                    cred.set_password(KEYRING_SERVICE, f'{region}:{account_id}', password)
                    new_acc = Account(
                        account_id=account_id,
                        name=name,
                        region=region,
                        region_display=region_display,
                        password=password,
                        description=''
                    )
                    self.manager.add_account(new_acc)

                    # Fetch rank information
                    rank_info = self.manager.rank_fetcher.fetch_rank(new_acc)
                    new_acc.tier = rank_info.get('tier', 'Unranked')
                    new_acc.division = rank_info.get('division', '')
                    new_acc.lp = rank_info.get('lp', '')
                    new_acc.level = rank_info.get('level', '')
                    new_acc.reached_last_season = rank_info.get('reached_last_season', 'N/A')
                    new_acc.finished_last_season = rank_info.get('finished_last_season', 'N/A')

                    processed_count += 1

                    # Remove the processed line and update display
                    self.root.after(0, lambda: self._remove_line_from_multiadd(0))
                    self.root.after(0, lambda: self.display_accounts(self.manager.accounts))
                    self.manager.save_accounts()

                except Exception as e:
                    # Log error information
                    error_msg = f"Error processing account {account_id}: {str(e)}"
                    print(error_msg)
                    error_count += 1
                    # Remove the error line as well
                    self.root.after(0, lambda: self._remove_line_from_multiadd(0))

            # Clear the multi-add field when all accounts are processed
            if processed_count > 0 or error_count > 0:
                self.root.after(0, lambda: self._clear_multiadd_field())

        threading.Thread(target=worker, daemon=True).start()

    def _remove_line_from_multiadd(self, idx):
        lines = self.multiadd_text.get('1.0', tk.END).splitlines()
        if 0 <= idx < len(lines):
            del lines[idx]
            self.multiadd_text.delete('1.0', tk.END)
            self.multiadd_text.insert('1.0', '\n'.join(lines))

    def _clear_multiadd_field(self):
        """Clear the multi-add field and restore placeholder text"""
        self.multiadd_text.delete('1.0', tk.END)
        self.multiadd_text.insert('1.0', self.multiadd_placeholder)
        self.multiadd_text.configure(text_color=COLORS['text_secondary'])

    def display_accounts(self, accounts):
        self.tree.delete(*self.tree.get_children())
        for acc in accounts:
            tier = acc.tier or 'Unranked'
            division = acc.division or ''
            lp = acc.lp or ''
            level = acc.level or ''
            reached_last_season = acc.reached_last_season or 'N/A'
            finished_last_season = acc.finished_last_season or 'N/A'
            if not tier or tier == 'Unranked':
                tier = '...'
            if not division:
                division = '...'
            if not lp:
                lp = '...'
            if not level:
                level = '...'
            self.tree.insert('', 'end', values=(
                acc.account_id,
                acc.name,
                acc.region_display,
                level,
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
        _lazy_imports()
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        values = self.tree.item(item, 'values')
        if not values or len(values) < 1:
            return
        account_id = values[0]
        pyperclip.copy(account_id)

    def _find_account(self, account_id, region_display):
        """Find an account in memory by account_id and region_display."""
        region = REGION_MAP.get(region_display, region_display)
        for acc in self.manager.accounts:
            if acc.account_id == account_id and acc.region in (region, region_display):
                return acc
        return None

    def _get_password(self, account_id, region_display):
        """Get password from in-memory account, falling back to credential store."""
        acc = self._find_account(account_id, region_display)
        if acc and acc.password:
            return acc.password
        # Fallback to credential store if in-memory password is empty
        region = REGION_MAP.get(region_display, region_display)
        try:
            return cred.get_password(KEYRING_SERVICE, f'{region}:{account_id}') or ''
        except Exception:
            return ''

    def copy_selected_password(self):
        _lazy_imports()
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        values = self.tree.item(item, 'values')
        if not values or len(values) < 3:
            return
        account_id = values[0]
        region_display = values[2]
        password = self._get_password(account_id, region_display)
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
                        self.root.after(0, lambda: self.tree.tag_configure('refreshing', background='#4a4a4a'))
                        break
                # Fetch new rank info
                rank_info = self.manager.rank_fetcher.fetch_rank(acc)
                acc.tier = rank_info.get('tier', 'Unranked')
                acc.division = rank_info.get('division', '')
                acc.lp = rank_info.get('lp', '')
                acc.level = rank_info.get('level', '')
                acc.reached_last_season = rank_info.get('reached_last_season', 'N/A')
                acc.finished_last_season = rank_info.get('finished_last_season', 'N/A')
                self.manager.save_accounts()
                # Update the row in the tree with new rank info
                for item in self.tree.get_children():
                    values = self.tree.item(item, 'values')
                    if values and values[0] == acc.account_id and values[2] == acc.region_display:
                        new_values = list(values)
                        new_values[3] = acc.level or '...'
                        new_values[4] = acc.tier or '...'
                        new_values[5] = acc.division or '...'
                        new_values[6] = acc.lp or '...'
                        new_values[7] = acc.reached_last_season or 'N/A'
                        new_values[8] = acc.finished_last_season or 'N/A'
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
        if col_num not in [1, 9]:
            return
        bbox = self.tree.bbox(row_id, col_id)
        if not bbox:
            return
        x, y, width, height = bbox
        values = list(self.tree.item(row_id, 'values'))
        current_value = values[col_num] if len(values) > col_num else ""
        entry = tk.Entry(self.tree, bg=COLORS['bg_card'], fg=COLORS['text_primary'],
                        insertbackground=COLORS['text_primary'])
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
                    elif col_num == 9:
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
            _lazy_imports()
            if not RANKS_IMAGE_PATH.exists():
                messagebox.showerror('Error', f'Ranks image not found: {RANKS_IMAGE_PATH}')
                return

            # Load and scale image
            img = Image.open(RANKS_IMAGE_PATH)
            self.root.update_idletasks()
            max_w = int(self.root.winfo_width() * 0.9)
            max_h = int(self.root.winfo_height() * 0.85)
            w, h = img.size

            if w > max_w or h > max_h:
                scale = min(max_w / w, max_h / h)
                new_w, new_h = int(w * scale), int(h * scale)
                if hasattr(Image, 'Resampling'):
                    resample = Image.Resampling.LANCZOS
                else:
                    resample = Image.LANCZOS
                img = img.resize((new_w, new_h), resample)
            else:
                new_w, new_h = w, h

            # Blocker to capture all clicks
            blocker = tk.Frame(self.root, bg=COLORS['bg_main'])
            blocker.place(relx=0, rely=0, relwidth=1, relheight=1)

            def close_popup():
                blocker.destroy()

            # Create popup on top of blocker
            popup = ctk.CTkFrame(blocker, fg_color=COLORS['bg_card'], corner_radius=10,
                                 border_width=2, border_color=COLORS['border'])
            popup.place(relx=0.5, rely=0.5, anchor='center')

            # Close button row
            header = ctk.CTkFrame(popup, fg_color='transparent', height=25)
            header.pack(fill='x', padx=5, pady=(5, 0))
            close_btn = ctk.CTkButton(header, text='✕', width=25, height=25,
                                      fg_color='transparent', hover_color=COLORS['border'],
                                      command=close_popup)
            close_btn.pack(side='right')

            # Image
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(new_w, new_h))
            label = ctk.CTkLabel(popup, image=ctk_img, text='')
            label.pack(padx=10, pady=(5, 10))
            self._img_refs.append(ctk_img)

            # Close on Escape key
            blocker.focus_set()
            blocker.bind('<Escape>', lambda e: close_popup())

        except Exception as e:
            messagebox.showerror('Error', f'Could not open ranks image: {e}')

    def on_tree_ctrl_c(self, event=None):
        _lazy_imports()
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
            password = self._get_password(account_id, region_display)
            if password:
                pyperclip.copy(password)
        self._copy_counter += 1

    def on_tree_ctrl_shift_v(self, event=None):
        _lazy_imports()
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        values = self.tree.item(item, 'values')
        if not values or len(values) < 3:
            return
        account_id = values[0]
        region_display = values[2]
        password = self._get_password(account_id, region_display)
        self.root.after(100, lambda: self._do_autotype(account_id, password))

    def _do_autotype(self, account_id, password):
        _lazy_imports()
        if pyautogui is None:
            messagebox.showwarning('Feature Unavailable',
                                 'Auto-type feature is not available.\n'
                                 'PyAutoGUI could not be loaded.')
            return
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

    def export_data(self):
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            initialfile='credentials',
            defaultextension='.json',
            filetypes=[('JSON files', '*.json'), ('All files', '*.*')],
            title='Export Accounts Data'
        )
        if not file_path:
            return
        try:
            json_str = self.manager.export_accounts()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
            messagebox.showinfo('Export Successful', f'Accounts exported to:\n{file_path}')
        except Exception as e:
            messagebox.showerror('Export Error', f'Failed to export accounts.\n\nError: {str(e)}')

    def import_data(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            filetypes=[('JSON files', '*.json'), ('All files', '*.*')],
            title='Import Accounts Data'
        )
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_str = f.read()
            added, skipped = self.manager.import_accounts(json_str)
            self.display_accounts(self.manager.accounts)
            messagebox.showinfo('Import Successful',
                                f'Import complete.\n\nAccounts added: {added}\nAccounts skipped (duplicates): {skipped}')
        except json.JSONDecodeError:
            messagebox.showerror('Import Error', 'Invalid JSON file. Please check the file format.')
        except Exception as e:
            messagebox.showerror('Import Error', f'Failed to import accounts.\n\nError: {str(e)}')

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
        win = ctk.CTkToplevel(self.root)
        win.title('Shortcuts Help')
        win.geometry('450x300')
        win.resizable(False, False)

        text = ctk.CTkTextbox(win, wrap='word', fg_color=COLORS['bg_card'],
                              text_color=COLORS['text_primary'])
        text.insert('1.0', help_text)
        text.configure(state='disabled')
        text.pack(expand=True, fill='both', padx=15, pady=15)

        win.transient(self.root)
        win.grab_set()
        win.focus_set()
