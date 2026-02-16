import requests
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import io
from datetime import datetime
import mplfinance as mpf

# 🎨 ธีมสี (Color Palette)
BG_COLOR = (18, 18, 24)
CARD_COLOR = (30, 32, 40)
TEXT_WHITE = (255, 255, 255)
TEXT_GRAY = (120, 120, 130)
GREEN_RGB = (0, 230, 118)
RED_RGB = (255, 82, 82)
BAR_BG_RGB = (40, 40, 50)

UP_COLOR_HEX = '#00E676'
DOWN_COLOR_HEX = '#FF5252'
EDGE_COLOR_HEX = '#303240'
AXIS_TEXT_HEX = '#707080'

def fetch_coin_details(symbol, name):
    """ดึงข้อมูลราคา High/Low จาก Binance (เร็วกว่าและไม่โดนแบนแบบ CoinGecko)"""
    binance_symbol = symbol + "USDT"
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={binance_symbol}"
        res = requests.get(url, timeout=5).json()
        
        # ใช้โลโก้จาก GitHub Repo สาธารณะ โหลดเร็วกว่ามาก
        logo_url = f"https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/{symbol.lower()}.png"
        
        return {
            'symbol': symbol,
            'name': name,
            'current_price': float(res['lastPrice']),
            'price_change_percentage_24h': float(res['priceChangePercent']),
            'high_24h': float(res['highPrice']),
            'low_24h': float(res['lowPrice']),
            'image': logo_url
        }
    except Exception as e:
        print("Error fetching details:", e)
        return None

def fetch_graph_data(symbol):
    binance_symbol = symbol + "USDT"
    url = "https://data-api.binance.vision/api/v3/klines"
    params = {'symbol': binance_symbol, 'interval': '1h', 'limit': 48}
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'vol', 'ct', 'qv', 'tr', 'tb', 'tq', 'ig'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            cols = ['open', 'high', 'low', 'close']
            df[cols] = df[cols].astype(float)
            return df
        return None
    except:
        return None

def calculate_ema_prediction(df, period=9):
    if df is None or len(df) < period:
        return None, None, None
    df['ema'] = df['close'].ewm(span=period, adjust=False).mean()
    ema_t = df['ema'].iloc[-1]
    ema_prev = df['ema'].iloc[-2]
    slope = ema_t - ema_prev
    current_price = df['close'].iloc[-1]
    price_next = current_price + slope
    return price_next, slope, current_price

def get_logo_image(url, size=(60, 60)):
    try:
        response = requests.get(url, stream=True, timeout=3)
        img = Image.open(response.raw).convert("RGBA")
        img = img.resize(size, Image.LANCZOS)
        return img
    except:
        # ถ้าโหลดรูปไม่ได้ ให้วาดวงกลมสีเทาแทน
        return Image.new('RGBA', size, (50, 50, 50, 255))

def create_chart_image(df, width, height):
    if df is None: return Image.new('RGB', (width, height), CARD_COLOR)
    mc = mpf.make_marketcolors(up=UP_COLOR_HEX, down=DOWN_COLOR_HEX, edge='inherit', wick='inherit', volume='inherit')
    s = mpf.make_mpf_style(marketcolors=mc, base_mpf_style='nightclouds', gridstyle=':', facecolor='#1E2028', edgecolor=EDGE_COLOR_HEX, rc={'axes.labelcolor': AXIS_TEXT_HEX, 'xtick.color': AXIS_TEXT_HEX, 'ytick.color': AXIS_TEXT_HEX})
    
    buf = io.BytesIO()
    fig, axlist = mpf.plot(df, type='candle', style=s, returnfig=True, volume=False, figsize=(width/100, height/100), ylabel='', title='', tight_layout=True, datetime_format='%H:%M')
    
    ax = axlist[0]
    ax.tick_params(axis='x', labelsize=7, rotation=0, colors=AXIS_TEXT_HEX)
    ax.tick_params(axis='y', labelsize=7, colors=AXIS_TEXT_HEX)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.05, facecolor='#1E2028')
    buf.seek(0)
    img = Image.open(buf).convert('RGB')
    plt.close(fig)
    return img

def create_dashboard(coin_info):
    """ฟังก์ชันหลักสำหรับสร้างรูปภาพ Dashboard ส่งออกเป็น PIL Image"""
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 480
    
    # 1. โหลดข้อมูลเหรียญที่ถูกส่งเข้ามา
    symbol = coin_info['symbol']
    name = coin_info['name']
    
    coin = fetch_coin_details(symbol, name)
    df_graph = fetch_graph_data(symbol)

    image = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(image)

    # 2. ตั้งค่าฟอนต์ (ปรับให้รองรับ Windows / Mac / Linux อัตโนมัติ)
    try:
        font_huge = ImageFont.truetype("arialbd.ttf", 80)
        font_large = ImageFont.truetype("arialbd.ttf", 40)
        font_med = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        font_huge = font_large = font_med = font_small = ImageFont.load_default()

    if not coin:
        draw.text((250, 200), f"LOADING DATA FOR {symbol}...", font=font_large, fill=TEXT_WHITE)
        return image

    # --- Header ---
    logo = get_logo_image(coin['image'])
    image.paste(logo, (30, 30), logo)
    draw.text((110, 35), coin['symbol'].upper(), font=font_large, fill=TEXT_WHITE)
    
    # ใช้ bbox แทน textlength เพื่อความแม่นยำในฟอนต์ใหม่
    bbox = draw.textbbox((0,0), coin['symbol'].upper(), font=font_large)
    sym_w = bbox[2] - bbox[0]
    draw.text((110 + sym_w + 15, 50), coin['name'], font=font_med, fill=TEXT_GRAY)

    # Date/Time
    now = datetime.now()
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%d %b")
    draw.text((SCREEN_WIDTH - 130, 35), time_str, font=font_large, fill=TEXT_WHITE)
    draw.text((SCREEN_WIDTH - 110, 80), date_str, font=font_med, fill=TEXT_GRAY)

    # --- Price Info ---
    price = coin['current_price']
    price_str = f"${price:,.2f}" if price > 1 else f"${price:,.4f}"
    draw.text((30, 140), price_str, font=font_huge, fill=TEXT_WHITE)

    pct = coin['price_change_percentage_24h']
    pct_col = GREEN_RGB if pct >= 0 else RED_RGB
    arrow = "▲" if pct >= 0 else "▼"
    draw.text((30, 230), f"{arrow} {abs(pct):.2f}% (24h)", font=font_med, fill=pct_col)

    # --- Progress Bar (High/Low) ---
    low_24h = coin['low_24h']
    high_24h = coin['high_24h']
    bx, by, bw, bh = 30, 300, 320, 10
    draw.rectangle([bx, by, bx+bw, by+bh], fill=BAR_BG_RGB)

    if high_24h > low_24h:
        ratio = (price - low_24h) / (high_24h - low_24h)
        ratio = max(0, min(1, ratio))
        mx = bx + int(ratio * bw)
        draw.rectangle([mx-2, by-5, mx+2, by+bh+5], fill=TEXT_WHITE)

    draw.text((bx, by+20), f"L: ${low_24h:,.2f}", font=font_small, fill=TEXT_GRAY)
    draw.text((bx+bw-100, by+20), f"H: ${high_24h:,.2f}", font=font_small, fill=TEXT_GRAY)

    # --- 🔮 AI PREDICTION ---
    if df_graph is not None:
        pred_price, slope, _ = calculate_ema_prediction(df_graph, period=9)
        if pred_price is not None:
            pred_col = GREEN_RGB if slope >= 0 else RED_RGB
            arrow_sym = "▲" if slope >= 0 else "▼"
            pred_y = 360
            draw.text((30, pred_y), "PREDICTION (1H):", font=font_small, fill=TEXT_GRAY)
            draw.text((30, pred_y+25), f"{arrow_sym} ${pred_price:,.2f}", font=font_large, fill=pred_col)

    # --- Chart Area ---
    cx, cy, cw, ch = 380, 120, 390, 330
    chart_img = create_chart_image(df_graph, cw, ch)
    draw.rectangle([cx, cy, cx+cw, cy+ch], fill=CARD_COLOR)
    image.paste(chart_img, (cx, cy))

    return image