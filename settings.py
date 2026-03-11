# settings.py — หน้า Settings และ sub-pages ทั้งหมด
# ใช้งาน: SettingsManager(app).show_settings_page()

import tkinter as tk
from app_themes import THEMES

MENU_ITEMS = [
    {"icon": "⏰", "label": "Alarm Clock",        "sub": "ตั้งนาฬิกาปลุก",        "color": "#FF7043", "key": "alarm"},
    {"icon": "🎨", "label": "Color Theme",         "sub": "dark / light / matrix",  "color": "#AB47BC", "key": "theme"},
    {"icon": "🔔", "label": "Sound Notification",  "sub": "ตั้งค่าเสียงแจ้งเตือน",  "color": "#29B6F6", "key": "sound"},
    {"icon": "📧", "label": "Email Alert",          "sub": "อีเมลรับการแจ้งเตือน",   "color": "#26A69A", "key": "email"},
    {"icon": "🕐", "label": "Time Zone",            "sub": "ตั้งค่า Timezone",        "color": "#FFA726", "key": "timezone"},
    {"icon": "📈", "label": "EMA Period Settings",  "sub": "ตั้งค่าเส้น EMA",         "color": "#00E676", "key": "ema"},
]


class SettingsManager:
    """
    จัดการทุกหน้าใน Settings
    รับ app (CryptoApp) เพื่อเข้าถึง root window, theme, ค่าต่างๆ
    และ callback กลับหน้า Home / Settings
    """

    def __init__(self, app):
        self.app = app  # reference ไปยัง CryptoApp instance

    # ── shortcut ──────────────────────────────────────────
    @property
    def T(self):
        return self.app.T  # dict สีธีมปัจจุบัน

    def _root(self):
        return self.app  # tk.Tk root window

    # =====================================================
    # SETTINGS PAGE (หน้าหลัก)
    # =====================================================
    def show_settings_page(self):
        self.app.clear_screen()
        T = self.T
        root = self._root()

        # ----- Header -----
        header = tk.Frame(root, bg=T["bg"])
        header.pack(fill=tk.X)

        tk.Label(header, text="⚙️  Settings",
                 font=('Arial', 22, 'bold'), fg=T["text"], bg=T["bg"]
                 ).pack(side=tk.LEFT, padx=20, pady=14)

        tk.Frame(root, bg=T["divider"], height=2).pack(fill=tk.X)

        # ----- กริด 2×3 -----
        grid_frame = tk.Frame(root, bg=T["bg"])
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=10)

        for col in range(2):
            grid_frame.columnconfigure(col, weight=1, uniform="col")
        for row in range(3):
            grid_frame.rowconfigure(row, weight=1, uniform="row")

        for idx, item in enumerate(MENU_ITEMS):
            self._make_menu_card(grid_frame, item, idx // 2, idx % 2)

        # ----- Back bar -----
        tk.Frame(root, bg=T["back_divider"], height=2).pack(fill=tk.X)
        back_bar = tk.Frame(root, bg=T["back_bar"])
        back_bar.pack(fill=tk.X)

        tk.Button(back_bar, text="◀   Back to Dashboard",
                  font=('Arial', 13, 'bold'),
                  bg=T["back_bar"], fg=T["subtext"],
                  relief=tk.FLAT, cursor="hand2",
                  activebackground=T["accent"], activeforeground=T["text"],
                  command=self.app.show_home_page
                  ).pack(side=tk.LEFT, padx=20, pady=12)

    # =====================================================
    # COLOR THEME PAGE
    # =====================================================
    def show_color_theme_page(self):
        self.app.clear_screen()
        T = self.T
        root = self._root()

        # ----- Header -----
        header = tk.Frame(root, bg=T["bg"])
        header.pack(fill=tk.X)

        tk.Label(header, text="🎨  Color Theme",
                 font=('Arial', 22, 'bold'), fg=T["text"], bg=T["bg"]
                 ).pack(side=tk.LEFT, padx=20, pady=14)

        tk.Frame(root, bg=T["divider"], height=2).pack(fill=tk.X)

        # ----- การ์ดธีม 3 คอลัมน์ -----
        body = tk.Frame(root, bg=T["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

        for col in range(3):
            body.columnconfigure(col, weight=1)
        body.rowconfigure(0, weight=1)

        for col_idx, (key, theme) in enumerate(THEMES.items()):
            self._make_theme_card(body, key, theme, col_idx)

        # ----- Back bar -----
        tk.Frame(root, bg=T["back_divider"], height=2).pack(fill=tk.X)
        back_bar = tk.Frame(root, bg=T["back_bar"])
        back_bar.pack(fill=tk.X)

        tk.Button(back_bar, text="◀   Back to Settings",
                  font=('Arial', 13, 'bold'),
                  bg=T["back_bar"], fg=T["subtext"],
                  relief=tk.FLAT, cursor="hand2",
                  activebackground=T["accent"], activeforeground=T["text"],
                  command=self.show_settings_page
                  ).pack(side=tk.LEFT, padx=20, pady=12)

    # =====================================================
    # EMA SETTINGS (popup)
    # =====================================================
    def show_ema_settings(self):
        T = self.T
        root = self._root()

        win = tk.Toplevel(root)
        win.title("EMA Period Settings")
        win.geometry("340x185")
        win.configure(bg=T["bg"])
        win.resizable(False, False)

        tk.Label(win, text="📈  EMA Period Settings",
                 font=('Arial', 13, 'bold'), fg='#00E676', bg=T["bg"]
                 ).pack(pady=(16, 4))
        tk.Label(win, text="กรอกค่า EMA คั่นด้วยลูกน้ำ  (เช่น  12, 26, 50)",
                 font=('Arial', 10), fg=T["subtext"], bg=T["bg"]).pack()

        entry = tk.Entry(win, font=('Arial', 14), justify='center',
                         bg=T["accent"], fg=T["entry_fg"],
                         insertbackground=T["entry_fg"], relief=tk.FLAT)
        entry.pack(pady=8, padx=24, fill=tk.X, ipady=6)
        entry.insert(0, ", ".join(map(str, self.app.custom_emas)))

        def save():
            val = entry.get()
            if val.strip():
                try:
                    self.app.custom_emas = [
                        int(x.strip()) for x in val.split(',')
                        if x.strip().isdigit()
                    ]
                except:
                    pass
            else:
                self.app.custom_emas = []
            win.destroy()

        tk.Button(win, text="บันทึก", font=('Arial', 11, 'bold'),
                  bg='#00E676', fg='black', relief=tk.FLAT,
                  command=save).pack(pady=4, ipadx=20, ipady=4)

    # =====================================================
    # PLACEHOLDER (Coming Soon)
    # =====================================================
    def show_placeholder(self, title):
        T = self.T
        win = tk.Toplevel(self._root())
        win.title(title)
        win.geometry("300x130")
        win.configure(bg=T["bg"])
        win.resizable(False, False)

        tk.Label(win, text=title, font=('Arial', 14, 'bold'),
                 fg=T["text"], bg=T["bg"]).pack(pady=18)
        tk.Label(win, text="🚧  Coming Soon", font=('Arial', 11),
                 fg=T["subtext"], bg=T["bg"]).pack()
        tk.Button(win, text="ปิด", font=('Arial', 11),
                  bg=T["accent"], fg=T["text"], relief=tk.FLAT,
                  command=win.destroy).pack(pady=14)

    # =====================================================
    # HELPERS — สร้าง UI ชิ้นส่วน
    # =====================================================
    def _get_handler(self, key):
        """จับคู่ key กับฟังก์ชัน"""
        return {
            "alarm":    lambda: self.show_placeholder("⏰ Alarm Clock"),
            "theme":    self.show_color_theme_page,
            "sound":    lambda: self.show_placeholder("🔔 Sound Notification"),
            "email":    lambda: self.show_placeholder("📧 Email Alert"),
            "timezone": lambda: self.show_placeholder("🕐 Time Zone"),
            "ema":      self.show_ema_settings,
        }.get(key, lambda: None)

    def _make_menu_card(self, parent, item, row, col):
        T = self.T
        card = tk.Frame(parent, bg=T["accent"], cursor="hand2")
        card.grid(row=row, column=col, padx=8, pady=6, sticky="nsew")

        accent_bar = tk.Frame(card, bg=item["color"], width=5)
        accent_bar.pack(side=tk.LEFT, fill=tk.Y)

        text_frame = tk.Frame(card, bg=T["accent"])
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=10)

        title_row = tk.Frame(text_frame, bg=T["accent"])
        title_row.pack(anchor='w')

        tk.Label(title_row, text=item["icon"],
                 font=('Arial', 18), bg=T["accent"], fg=item["color"]
                 ).pack(side=tk.LEFT, padx=(0, 6))

        tk.Label(title_row, text=item["label"],
                 font=('Arial', 14, 'bold'), bg=T["accent"], fg=T["text"]
                 ).pack(side=tk.LEFT)

        tk.Label(text_frame, text=item["sub"],
                 font=('Arial', 10), bg=T["accent"], fg=T["subtext"]
                 ).pack(anchor='w', pady=(2, 0))

        handler = self._get_handler(item["key"])
        for w in [card, text_frame, title_row]:
            w.bind("<Button-1>", lambda e, h=handler: h())

        def on_enter(e, c=card, clr=item["color"]):
            c.config(bg=clr)
            self._set_bg_recursive(c, clr, skip=accent_bar)

        def on_leave(e, c=card):
            c.config(bg=T["accent"])
            self._set_bg_recursive(c, T["accent"], skip=accent_bar)

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

    def _make_theme_card(self, parent, key, theme, col):
        is_active    = (key == self.app.current_theme_key)
        border_color = "#AB47BC" if is_active else theme["accent"]

        card = tk.Frame(parent, bg=theme["bg"],
                        highlightbackground=border_color,
                        highlightthickness=3,
                        cursor="hand2")
        card.grid(row=0, column=col, padx=10, sticky="nsew")

        # Preview header
        prev_header = tk.Frame(card, bg=theme["accent"], height=36)
        prev_header.pack(fill=tk.X)
        prev_header.pack_propagate(False)

        tk.Label(prev_header, text=f"{theme['icon']}  {theme['name']}",
                 font=('Arial', 13, 'bold'),
                 fg=theme["text"], bg=theme["accent"]
                 ).pack(side=tk.LEFT, padx=10, pady=6)

        if is_active:
            tk.Label(prev_header, text="✔ ใช้งานอยู่",
                     font=('Arial', 9, 'bold'),
                     fg="#AB47BC", bg=theme["accent"]
                     ).pack(side=tk.RIGHT, padx=8)

        # Preview rows
        prev_body = tk.Frame(card, bg=theme["bg"])
        prev_body.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        samples = [
            ("BTC", "$67,420", "+2.34%", True),
            ("ETH", "$3,512",  "-1.10%", False),
            ("BNB", "$598",    "+0.88%", True),
        ]
        for i, (sym, price, pct, up) in enumerate(samples):
            row_bg = theme["accent"] if i % 2 == 0 else theme["bg"]
            row = tk.Frame(prev_body, bg=row_bg)
            row.pack(fill=tk.X, pady=1)

            tk.Label(row, text=sym,   font=('Arial', 10, 'bold'),
                     fg=theme["text"],  bg=row_bg, width=5, anchor='w'
                     ).pack(side=tk.LEFT, padx=(6, 0), pady=4)
            tk.Label(row, text=price, font=('Arial', 10),
                     fg=theme["price"], bg=row_bg
                     ).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=pct,   font=('Arial', 9, 'bold'),
                     fg=theme["up"] if up else theme["down"], bg=row_bg
                     ).pack(side=tk.RIGHT, padx=6)

        # ปุ่มเลือก
        tk.Button(card,
                  text="✔ ธีมปัจจุบัน" if is_active else "เลือกธีมนี้",
                  font=('Arial', 11, 'bold'),
                  bg="#AB47BC" if is_active else theme["accent"],
                  fg="#FFFFFF",
                  relief=tk.FLAT, cursor="hand2",
                  activebackground="#7B1FA2",
                  command=lambda k=key: self._apply_theme(k)
                  ).pack(fill=tk.X, padx=10, pady=(4, 10), ipady=6)

        card.bind("<Button-1>", lambda e, k=key: self._apply_theme(k))

    def _apply_theme(self, key):
        """เปลี่ยนธีมแล้ว re-render หน้า Color Theme"""
        self.app.current_theme_key = key
        self.app.T = THEMES[key]
        self.app.configure(bg=self.app.T["bg"])
        self.show_color_theme_page()

    def _set_bg_recursive(self, widget, color, skip=None):
        for child in widget.winfo_children():
            if child is skip:
                continue
            try:
                child.config(bg=color)
            except tk.TclError:
                pass
            self._set_bg_recursive(child, color, skip=skip)