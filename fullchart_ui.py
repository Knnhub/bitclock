import requests
import pandas as pd
import mplfinance as mpf
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import io

# 🎨 ธีมสี
BG_COLOR = (15, 15, 20)
TEXT_WHITE = (255, 255, 255)
TEXT_GRAY = (160, 160, 170)
EMA_COLORS_HEX = ['#29B6F6', '#FFA726', '#EF5350']
EMA_COLORS_RGB = [(41, 182, 246), (255, 167, 38), (239, 83, 80)]

def fetch_graph_data(symbol, interval):
    """ดึงข้อมูลกราฟตาม Timeframe ที่เลือก"""
    binance_symbol = symbol + "USDT"
    url = "https://data-api.binance.vision/api/v3/klines"
    params = {'symbol': binance_symbol, 'interval': interval, 'limit': 100}
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            df = pd.DataFrame(response.json(), columns=['timestamp', 'open', 'high', 'low', 'close', 'vol', 'ct', 'qv', 'tr', 'tb', 'tq', 'ig'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
            return df
        return None
    except:
        return None

def create_chart_image(df, width, height, interval):
    if df is None: return Image.new('RGB', (width, height), BG_COLOR)

    # 🕒 ปรับรูปแบบเวลาให้เหมาะสมกับ Timeframe
    if interval in ['1m', '5m', '1h']:
        dt_format = '%H:%M'
    elif interval == '4h':
        dt_format = '%d %b %H:00'
    else: # 1d
        dt_format = '%d %b'

    mc = mpf.make_marketcolors(up='#00E676', down='#FF5252', edge='inherit', wick='inherit', volume='inherit')
    s = mpf.make_mpf_style(
        marketcolors=mc, base_mpf_style='nightclouds', gridstyle=':', 
        facecolor='#0F0F14', edgecolor='#303240', mavcolors=EMA_COLORS_HEX,
        rc={'axes.labelcolor': '#808080', 'xtick.color': '#808080', 'ytick.color': '#808080'}
    )

    plot_df = df.iloc[-60:] # โชว์ 60 แท่งให้เต็มจอพอดี

    buf = io.BytesIO()
    fig, axlist = mpf.plot(
        plot_df, 
        type='candle', 
        style=s, 
        mav=(12, 26, 50), 
        returnfig=True, 
        volume=False,
        figsize=(width/100, height/100), 
        tight_layout=True, 
        datetime_format=dt_format, 
        xrotation=0,
    )

    ax = axlist[0]
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    ax.yaxis.tick_right()

    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, facecolor='#0F0F14')
    buf.seek(0)
    img = Image.open(buf).convert('RGB')
    plt.close(fig)
    return img

def create_full_dashboard(coin_info, interval='1h'):
    """ฟังก์ชันหลักสร้างรูปภาพกราฟเต็มจอ"""
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 480
    symbol = coin_info['symbol']
    price = coin_info['price']
    pct = coin_info['percent']

    df_graph = fetch_graph_data(symbol, interval)
    
    image = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(image)

    try:
        font_large = ImageFont.truetype("arialbd.ttf", 36)
        font_med = ImageFont.truetype("arial.ttf", 20)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font_large = font_med = font_small = ImageFont.load_default()

    if df_graph is None:
        draw.text((300, 200), "LOADING CHART...", font=font_large, fill=TEXT_WHITE)
        return image

    # --- Header ---
    price_str = f"${price:,.2f}" if price > 1 else f"${price:,.4f}"
    draw.text((20, 15), f"{symbol.upper()} / USDT  ({interval.upper()})", font=font_med, fill=TEXT_GRAY)
    draw.text((20, 40), price_str, font=font_large, fill=TEXT_WHITE)

    pct_color = (0, 230, 118) if pct >= 0 else (255, 82, 82)
    bbox = draw.textbbox((0,0), price_str, font=font_large)
    price_w = bbox[2] - bbox[0]
    draw.text((20 + price_w + 15, 52), f"{pct:+.2f}%", font=font_med, fill=pct_color)

    # --- EMA Legend ---
    ema12 = df_graph['close'].ewm(span=12, adjust=False).mean().iloc[-1]
    ema26 = df_graph['close'].ewm(span=26, adjust=False).mean().iloc[-1]
    ema50 = df_graph['close'].ewm(span=50, adjust=False).mean().iloc[-1]
    
    legend_y = 85
    start_x = 20
    gap = 140
    draw.text((start_x, legend_y), f"EMA(12): {ema12:,.2f}", font=font_small, fill=EMA_COLORS_RGB[0])
    draw.text((start_x + gap, legend_y), f"EMA(26): {ema26:,.2f}", font=font_small, fill=EMA_COLORS_RGB[1])
    draw.text((start_x + gap*2, legend_y), f"EMA(50): {ema50:,.2f}", font=font_small, fill=EMA_COLORS_RGB[2])

    # --- Chart Area ---
    chart_y = 110
    chart_h = SCREEN_HEIGHT - chart_y
    chart_img = create_chart_image(df_graph, SCREEN_WIDTH, chart_h, interval)
    chart_img = chart_img.resize((SCREEN_WIDTH, chart_h), Image.LANCZOS)
    image.paste(chart_img, (0, chart_y))

    return image