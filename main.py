import tkinter as tk
import matplotlib.pyplot as plt
from PIL import ImageTk
import api
import dashboard_ui

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
        self.configure(bg=BG_COLOR) # พื้นหลังหลักเป็นสีดำ
        
        self.current_coin = None
        self.graph_fig = None
        self.refresh_job = None
        self.fullscreen_window = None
        
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
        
        # Header "TOP 10 MARKET CAP"
        header_frame = tk.Frame(self, bg=BG_COLOR)
        header_frame.pack(fill=tk.X, pady=(15, 5))
        tk.Label(header_frame, text="🏆 TOP 10 MARKET CAP", font=('Arial', 24, 'bold'), fg=GOLD_COLOR, bg=BG_COLOR).pack(side=tk.LEFT, padx=20)
        tk.Frame(self, bg='#646464', height=2).pack(fill=tk.X, padx=20, pady=(0, 10)) # เส้นคั่น
        
        content_frame = tk.Frame(self, bg=BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # แบ่ง 2 คอลัมน์ (ซ้าย-ขวา)
        left_col = tk.Frame(content_frame, bg=BG_COLOR)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        right_col = tk.Frame(content_frame, bg=BG_COLOR)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        coins = api.get_top_10_coins()
        if not coins:
            tk.Label(self, text="กำลังโหลดข้อมูล...", font=('Arial', 14), fg=TEXT_COLOR, bg=BG_COLOR).pack()
            self.after(5000, self.show_home_page)
            return

        # วนลูปสร้างตารางทีละแถว
        for i, coin in enumerate(coins):
            # ตัดสินใจว่าจะอยู่ฝั่งซ้าย (0-4) หรือขวา (5-9)
            parent_col = right_col if i >= 5 else left_col
            row_index = i - 5 if i >= 5 else i
            
            # สลับสีพื้นหลัง
            row_bg = ACCENT_COLOR if row_index % 2 == 0 else BG_COLOR
            
            # สร้าง Frame ที่ทำหน้าที่เป็นปุ่มกด
            row_frame = tk.Frame(parent_col, bg=row_bg, cursor="hand2")
            row_frame.pack(fill=tk.X, pady=2)
            
            # จัดการตัวเลข สีเปอร์เซ็นต์ และลูกศร
            percent = coin['percent']
            pct_color = '#00FF64' if percent >= 0 else '#FF5050'
            arrow = "▲" if percent >= 0 else "▼"
            price_text = f"${coin['price']:,.2f}" if coin['price'] >= 1 else f"${coin['price']:.4f}"
            
            # 1. ลำดับและชื่อเหรียญ
            lbl_name = tk.Label(row_frame, text=f"{i+1}. {coin['symbol']}", font=('Arial', 14, 'bold'), fg=TEXT_COLOR, bg=row_bg, anchor='w', width=8)
            lbl_name.pack(side=tk.LEFT, padx=(10, 0), pady=12)
            
            # 2. ราคา (สีฟ้าอ่อน)
            lbl_price = tk.Label(row_frame, text=price_text, font=('Arial', 14), fg=PRICE_COLOR, bg=row_bg, anchor='w')
            lbl_price.pack(side=tk.LEFT, expand=True, fill=tk.X)
            
            # 3. เปอร์เซ็นต์ (สีเขียว/แดง)
            lbl_pct = tk.Label(row_frame, text=f"{arrow} {abs(percent):.2f}%", font=('Arial', 12, 'bold'), fg=pct_color, bg=row_bg, anchor='e', width=9)
            lbl_pct.pack(side=tk.RIGHT, padx=(0, 10))
            
            # ทำให้ส่วนใดส่วนหนึ่งของแถวนี้คลิกได้หมดเลย
            def on_click(event, c=coin):
                self.show_detail_page(c)
            row_frame.bind("<Button-1>", on_click)
            lbl_name.bind("<Button-1>", on_click)
            lbl_price.bind("<Button-1>", on_click)
            lbl_pct.bind("<Button-1>", on_click)

    # ================= PAGE 2 : หน้ากราฟ (Detail) =================
    # ================= PAGE 2 : หน้ากราฟ Dashboard สุดเท่ =================
    def show_detail_page(self, coin):
        self.clear_screen()
        self.current_coin = coin
        
        # สร้างพื้นที่สำหรับแสดงรูปภาพ
        self.img_label = tk.Label(self, bg=BG_COLOR)
        self.img_label.pack(fill=tk.BOTH, expand=True)
        
        # สร้างปุ่มกลับ (ลอยอยู่มุมขวาบน เพื่อไม่ให้บังโลโก้เหรียญ)
        btn_back = tk.Button(self, text="✖ ปิด", font=('Arial', 12, 'bold'), bg='#FF5252', fg='white', relief=tk.FLAT, command=self.show_home_page)
        btn_back.place(x=720, y=20) # ใช้ place เพื่อวางลอยบนรูป

        # ปุ่มขยายกราฟตรงนี้
        btn_expand = tk.Button(self, text="📈 ขยายกราฟ", font=('Arial', 12, 'bold'), bg='#29B6F6', fg='white', relief=tk.FLAT, command=lambda: self.show_full_chart_page(coin, '1h'))
        btn_expand.place(x=600, y=20)
        
        self.update_dashboard_loop()

    def update_dashboard_loop(self):
        if not self.current_coin: return
        
        # 1. ให้ dashboard_ui สร้างรูปภาพขึ้นมา
        pil_image = dashboard_ui.create_dashboard(self.current_coin)
        
        # 2. แปลงรูปจาก PIL เป็นภาพที่ Tkinter รู้จัก
        self.tk_image = ImageTk.PhotoImage(pil_image)
        
        # 3. อัปเดตรูปบนหน้าจอ
        self.img_label.config(image=self.tk_image)
        
        # 4. ตั้งเวลาอัปเดตใหม่ทุกๆ 1 นาที (ไม่ควรตั้งถี่กว่านี้เพราะดึงกราฟ 1h)
        self.refresh_job = self.after(60000, self.update_dashboard_loop)

    # ================= PAGE 3 : หน้าต่างเต็มจอ =================
    def show_fullscreen(self):
        if not self.current_coin: return
        self.fullscreen_window = tk.Toplevel(self)
        self.fullscreen_window.title("Fullscreen Graph")
        self.fullscreen_window.attributes('-fullscreen', True)
        self.fullscreen_window.configure(bg=BG_COLOR)
        
        btn_close = tk.Button(self.fullscreen_window, text="ย่อหน้าต่าง [X]", font=('Arial', 14, 'bold'), bg='#ff5050', fg='white', relief=tk.FLAT, command=self.fullscreen_window.destroy)
        btn_close.pack(side=tk.TOP, anchor='ne', padx=10, pady=10)
        
        self.fullscreen_graph_frame = tk.Frame(self.fullscreen_window, bg=BG_COLOR)
        self.fullscreen_graph_frame.pack(fill=tk.BOTH, expand=True)
        self.update_graph_loop()


    # ================= PAGE 3 : กราฟเต็มจอ (Full Chart) =================
    def show_full_chart_page(self, coin, interval='1h'):
        self.clear_screen()
        self.current_coin = coin
        self.current_interval = interval
        
        # พื้นที่แสดงรูปกราฟเต็มจอ
        self.full_img_label = tk.Label(self, bg='#0F0F14')
        self.full_img_label.pack(fill=tk.BOTH, expand=True)
        
        # ✅ แถบปุ่มเลือก Timeframe (ลอยอยู่ตรงกลางบน)
        tf_frame = tk.Frame(self, bg='#0F0F14')
        tf_frame.place(x=350, y=20)
        
        timeframes = ['1m', '5m', '1h', '4h', '1d']
        for tf in timeframes:
            bg_color = '#00E676' if tf == interval else '#282832'
            fg_color = 'black' if tf == interval else 'white'
            btn = tk.Button(tf_frame, text=tf.upper(), font=('Arial', 10, 'bold'), bg=bg_color, fg=fg_color, relief=tk.FLAT,
                            command=lambda t=tf: self.show_full_chart_page(coin, t))
            btn.pack(side=tk.LEFT, padx=5)
            
        # ปุ่มย้อนกลับไปหน้า Detail
        btn_back = tk.Button(self, text="ย้อนกลับ", font=('Arial', 10, 'bold'), bg='#FF5252', fg='white', relief=tk.FLAT, command=lambda: self.show_detail_page(coin))
        btn_back.place(x=700, y=20)
        
        self.update_fullchart_loop()

    def update_fullchart_loop(self):
        if not self.current_coin or not hasattr(self, 'current_interval'): return
        
        import fullchart_ui # เรียกใช้ไฟล์ UI ที่เราเพิ่งสร้าง
        
        # สร้างรูปภาพกราฟเต็มจอ พร้อม Timeframe
        pil_image = fullchart_ui.create_full_dashboard(self.current_coin, self.current_interval)
        
        self.full_tk_image = ImageTk.PhotoImage(pil_image)
        self.full_img_label.config(image=self.full_tk_image)
        
        # 🔄 ถ้ารายนาที ให้รีเฟรชทุก 10 วิ, ถ้ารายชั่วโมงขึ้นไป รีเฟรชทุก 1 นาที
        refresh_rate = 10000 if self.current_interval in ['1m', '5m'] else 60000
        self.refresh_job = self.after(refresh_rate, self.update_fullchart_loop)

# --- 3 บรรทัดนี้คือหัวใจสำคัญที่ทำให้หน้าต่างเด้งขึ้นมาครับ ---
if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()