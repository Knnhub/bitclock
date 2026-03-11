import tkinter as tk
import multiprocessing
import matplotlib.pyplot as plt
from PIL import ImageTk

import api
import dashboard_ui
import tv_chart
from app_themes import THEMES
from settings import SettingsManager

from alerts.ema_cross import check_ema_cross
from alerts.email_sender import send_email


class CryptoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BitClock - App Mode")
        self.geometry("800x480")
        self.resizable(False, False)

        self.current_coin      = None
        self.graph_fig         = None
        self.refresh_job       = None
        self.custom_emas       = [12, 26, 50]
        self.last_signal       = None
        self.current_theme_key = "dark"
        self.T                 = THEMES[self.current_theme_key]

        self.settings = SettingsManager(self)

        self.configure(bg=self.T["bg"])
        self.show_home_page()

    # ==================== CLEAR SCREEN ====================
    def clear_screen(self):
        if self.refresh_job:
            self.after_cancel(self.refresh_job)
            self.refresh_job = None
        if self.graph_fig:
            plt.close(self.graph_fig)
            self.graph_fig = None
        for widget in self.winfo_children():
            if not isinstance(widget, tk.Toplevel):
                widget.destroy()

    # ==================== HOME PAGE ====================
    def show_home_page(self):
        self.clear_screen()
        T = self.T

        header_frame = tk.Frame(self, bg=T["bg"])
        header_frame.pack(fill=tk.X, pady=(15, 5))

        tk.Label(header_frame, text="🏆 TOP 10 MARKET CAP",
                 font=('Arial', 24, 'bold'), fg=T["gold"], bg=T["bg"]
                 ).pack(side=tk.LEFT, padx=20)

        tk.Button(header_frame, text="⚙️",
                  font=('Arial', 18), bg=T["bg"], fg=T["text"],
                  relief=tk.FLAT, cursor="hand2",
                  activebackground=T["accent"],
                  command=self.settings.show_settings_page
                  ).pack(side=tk.RIGHT, padx=20)

        tk.Frame(self, bg=T["divider"], height=2).pack(fill=tk.X, padx=20, pady=(0, 10))

        content_frame = tk.Frame(self, bg=T["bg"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        left_col = tk.Frame(content_frame, bg=T["bg"])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        right_col = tk.Frame(content_frame, bg=T["bg"])
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        coins = api.get_top_10_coins()
        if not coins:
            tk.Label(self, text="กำลังโหลดข้อมูล...",
                     font=('Arial', 14), fg=T["text"], bg=T["bg"]).pack()
            self.after(5000, self.show_home_page)
            return

        for i, coin in enumerate(coins):
            parent_col = right_col if i >= 5 else left_col
            row_index  = i - 5 if i >= 5 else i
            row_bg     = T["accent"] if row_index % 2 == 0 else T["bg"]

            row_frame = tk.Frame(parent_col, bg=row_bg, cursor="hand2")
            row_frame.pack(fill=tk.X, pady=2)

            percent    = coin['percent']
            pct_color  = T["up"] if percent >= 0 else T["down"]
            arrow      = "▲" if percent >= 0 else "▼"
            price      = coin['price']
            price_text = f"${price:,.2f}" if price >= 1 else f"${price:.4f}"

            lbl_name = tk.Label(row_frame, text=f"{i+1}. {coin['symbol']}",
                                font=('Arial', 14, 'bold'), fg=T["text"],
                                bg=row_bg, anchor='w', width=8)
            lbl_name.pack(side=tk.LEFT, padx=(10, 0), pady=12)

            lbl_price = tk.Label(row_frame, text=price_text,
                                 font=('Arial', 14), fg=T["price"],
                                 bg=row_bg, anchor='w')
            lbl_price.pack(side=tk.LEFT, expand=True, fill=tk.X)

            lbl_pct = tk.Label(row_frame, text=f"{arrow} {abs(percent):.2f}%",
                               font=('Arial', 12, 'bold'), fg=pct_color,
                               bg=row_bg, anchor='e', width=9)
            lbl_pct.pack(side=tk.RIGHT, padx=(0, 10))

            def on_click(event, c=coin):
                self.show_detail_page(c)
            for w in [row_frame, lbl_name, lbl_price, lbl_pct]:
                w.bind("<Button-1>", on_click)

    # ==================== DETAIL PAGE ====================
    def show_detail_page(self, coin):
        self.clear_screen()
        self.current_coin = coin
        T = self.T

        self.img_label = tk.Label(self, bg=T["bg"])
        self.img_label.pack(fill=tk.BOTH, expand=True)

        tk.Button(self, text="✖ ปิด", font=('Arial', 12, 'bold'),
                  bg='#FF5252', fg='white', relief=tk.FLAT,
                  command=self.show_home_page).place(x=720, y=20)

        tk.Button(self, text="📊 TradingView", font=('Arial', 12, 'bold'),
                  bg='#29B6F6', fg='black', relief=tk.FLAT,
                  command=lambda: tv_chart.show_interactive_chart(
                      coin['symbol'], self.custom_emas)
                  ).place(x=580, y=20)

        self.update_dashboard_loop()

    # ==================== DASHBOARD LOOP ====================
    def update_dashboard_loop(self):
        if not self.current_coin:
            return
        pil_image = dashboard_ui.create_dashboard(self.current_coin)
        self.tk_image = ImageTk.PhotoImage(pil_image)
        self.img_label.config(image=self.tk_image)

        try:
            symbol   = self.current_coin['symbol']
            ema_data = api.get_ema_values(symbol, self.custom_emas)
            if ema_data:
                price      = ema_data["price"]
                ema_values = {"short": ema_data["short"],
                              "mid":   ema_data["mid"],
                              "long":  ema_data["long"]}
                signals = check_ema_cross(symbol, ema_values)
                for s in signals:
                    signal_id = f"{symbol}_{s['type']}_{s['signal']}"
                    if signal_id == self.last_signal:
                        continue
                    direction = s["signal"]
                    msg = (f"📈 EMA Bullish Cross\n{symbol}\nType: {s['type']}\nPrice: {price}"
                           if direction == "bullish" else
                           f"📉 EMA Bearish Cross\n{symbol}\nType: {s['type']}\nPrice: {price}")
                    send_email("BitClock EMA Alert", msg, "phoophachanthayung@gmail.com")
                    print(msg)
                    self.last_signal = signal_id
        except Exception as e:
            print("EMA alert error:", e)

        self.refresh_job = self.after(60000, self.update_dashboard_loop)


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    app = CryptoApp()
    app.mainloop()