import tkinter as tk
import matplotlib.pyplot as plt
from PIL import ImageTk
import api
import dashboard_ui
import tv_chart  # ✅ เรียกใช้งานระบบกราฟ TradingView ตัวใหม่

# โทนสีตามที่คุณออกแบบ
BG_COLOR = "#141414"      # ดำเทา
ACCENT_COLOR = "#323232"  # พื้นหลังสลับแถว
TEXT_COLOR = "#FFFFFF"
GOLD_COLOR = "#FFD700"
PRICE_COLOR = "#C8C8FF"

class CryptoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BitClock - App Mode")
        self.geometry("800x480")
        self.configure(bg=BG_COLOR)
        
        self.current_coin = None
        self.graph_fig = None
        self.refresh_job = None
        
        # ✅ ค่า EMA เริ่มต้น (ผู้ใช้แก้ได้)
        self.custom_emas = [12, 26, 50] 
        
        self.show_home_page()

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

    # ================= PAGE 1 : หน้าแรกสไตล์ Dashboard =================
    def show_home_page(self):
        self.clear_screen()
        
        header_frame = tk.Frame(self, bg=BG_COLOR)
        header_frame.pack(fill=tk.X, pady=(15, 5))
        tk.Label(header_frame, text="🏆 TOP 10 MARKET CAP", font=('Arial', 24, 'bold'), fg=GOLD_COLOR, bg=BG_COLOR).pack(side=tk.LEFT, padx=20)
        tk.Frame(self, bg='#646464', height=2).pack(fill=tk.X, padx=20, pady=(0, 10))
        
        content_frame = tk.Frame(self, bg=BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        left_col = tk.Frame(content_frame, bg=BG_COLOR)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        right_col = tk.Frame(content_frame, bg=BG_COLOR)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        coins = api.get_top_10_coins()
        if not coins:
            tk.Label(self, text="กำลังโหลดข้อมูล...", font=('Arial', 14), fg=TEXT_COLOR, bg=BG_COLOR).pack()
            self.after(5000, self.show_home_page)
            return

        for i, coin in enumerate(coins):
            parent_col = right_col if i >= 5 else left_col
            row_index = i - 5 if i >= 5 else i
            row_bg = ACCENT_COLOR if row_index % 2 == 0 else BG_COLOR
            row_frame = tk.Frame(parent_col, bg=row_bg, cursor="hand2")
            row_frame.pack(fill=tk.X, pady=2)
            
            percent = coin['percent']
            pct_color = '#00FF64' if percent >= 0 else '#FF5050'
            arrow = "▲" if percent >= 0 else "▼"
            price_text = f"${coin['price']:,.2f}" if coin['price'] >= 1 else f"${coin['price']:.4f}"
            
            lbl_name = tk.Label(row_frame, text=f"{i+1}. {coin['symbol']}", font=('Arial', 14, 'bold'), fg=TEXT_COLOR, bg=row_bg, anchor='w', width=8)
            lbl_name.pack(side=tk.LEFT, padx=(10, 0), pady=12)
            lbl_price = tk.Label(row_frame, text=price_text, font=('Arial', 14), fg=PRICE_COLOR, bg=row_bg, anchor='w')
            lbl_price.pack(side=tk.LEFT, expand=True, fill=tk.X)
            lbl_pct = tk.Label(row_frame, text=f"{arrow} {abs(percent):.2f}%", font=('Arial', 12, 'bold'), fg=pct_color, bg=row_bg, anchor='e', width=9)
            lbl_pct.pack(side=tk.RIGHT, padx=(0, 10))
            
            def on_click(event, c=coin):
                self.show_detail_page(c)
            row_frame.bind("<Button-1>", on_click)
            lbl_name.bind("<Button-1>", on_click)
            lbl_price.bind("<Button-1>", on_click)
            lbl_pct.bind("<Button-1>", on_click)

    # ================= PAGE 2 : หน้า Detail ย่อย =================
    def show_detail_page(self, coin):
        self.clear_screen()
        self.current_coin = coin
        
        self.img_label = tk.Label(self, bg=BG_COLOR)
        self.img_label.pack(fill=tk.BOTH, expand=True)
        
        # 🔘 ปุ่มปิด
        btn_back = tk.Button(self, text="✖ ปิด", font=('Arial', 12, 'bold'), bg='#FF5252', fg='white', relief=tk.FLAT, command=self.show_home_page)
        btn_back.place(x=720, y=20)

        # 🔘 ปุ่มตั้งค่า EMA (ยังคงป๊อปอัปแบบเดิมเป๊ะๆ)
        btn_ema = tk.Button(self, text="⚙️ ตั้งค่า EMA", font=('Arial', 12, 'bold'), bg='#FFA726', fg='black', relief=tk.FLAT, command=self.open_ema_settings)
        btn_ema.place(x=420, y=20)

        # 🔘 ปุ่มเปิดกราฟ TradingView (ส่งค่า EMA ล่าสุดไปให้ไฟล์ tv_chart วาดกราฟ)
        btn_tv = tk.Button(self, text="📊 เปิดกราฟ TradingView", font=('Arial', 12, 'bold'), bg='#29B6F6', fg='black', relief=tk.FLAT, 
                           command=lambda: tv_chart.show_interactive_chart(coin['symbol'], self.custom_emas))
        btn_tv.place(x=540, y=20)
        
        self.update_dashboard_loop()

    def update_dashboard_loop(self):
        if not self.current_coin: return
        pil_image = dashboard_ui.create_dashboard(self.current_coin)
        self.tk_image = ImageTk.PhotoImage(pil_image)
        self.img_label.config(image=self.tk_image)
        self.refresh_job = self.after(60000, self.update_dashboard_loop)

    # 🔧 หน้าต่างตั้งค่า EMA (ผู้ใช้แก้ได้ตามอิสระ)
    def open_ema_settings(self):
        win = tk.Toplevel(self)
        win.title("ตั้งค่าเส้น EMA")
        win.geometry("320x160")
        win.configure(bg=BG_COLOR)
        
        tk.Label(win, text="กรอกตัวเลข EMA คั่นด้วยลูกน้ำ (,)\n(เช่น: 12, 26, 50 หรือ 7, 14, 21)\n*มีผลกับกราฟ TradingView*", font=('Arial', 10), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
        
        entry = tk.Entry(win, font=('Arial', 14), justify='center')
        entry.pack(pady=5, padx=20, fill=tk.X)
        
        current_str = ", ".join(map(str, self.custom_emas))
        entry.insert(0, current_str)
        
        def save_emas():
            val = entry.get()
            if val.strip():
                try:
                    self.custom_emas = [int(x.strip()) for x in val.split(',') if x.strip().isdigit()]
                except:
                    pass
            else:
                self.custom_emas = []
                
            win.destroy()

        tk.Button(win, text="บันทึก", font=('Arial', 10, 'bold'), bg='#00E676', fg='black', command=save_emas).pack(pady=10)

if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()