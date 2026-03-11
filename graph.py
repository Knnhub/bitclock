import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def create_candlestick_widget(parent, df, coin_name, is_fullscreen=False):
    figsize = (10, 6) if is_fullscreen else (7, 3.5)
    
    # --- ตั้งค่า Theme แบบ Dark Mode ให้เข้ากับหน้าแรก ---
    mc = mpf.make_marketcolors(up='#00FF64', down='#FF5050', edge='inherit', wick='inherit', volume='in')
    s = mpf.make_mpf_style(
        marketcolors=mc, 
        gridstyle=':', 
        facecolor='#141414',   # สีพื้นหลังกราฟ
        edgecolor='white',
        figcolor='#141414',    # สีขอบนอกกราฟ
        gridcolor='#323232',
        rc={'text.color': 'white', 'axes.labelcolor': 'white', 'xtick.color': 'white', 'ytick.color': 'white'}
    )

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor('#141414')

    
    if df is not None and not df.empty:
        # ✅ ใหม่: เลือก type ตาม chart_type ที่รับเข้ามา ('candle' หรือ 'line')
        mpf.plot(df, ax=ax, type=chart_type, style=s,
                 axtitle=f'{coin_name}/USDT', ylabel='Price (USDT)')
    else:
        ax.set_facecolor('#141414')
        ax.set_title("กำลังโหลดข้อมูล...", color='white')
        
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    
    return canvas.get_tk_widget(), fig