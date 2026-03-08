import requests
import pandas as pd
import time
import history_manager

# ==========================================
# 🛑 นำ API Key ของ CoinMarketCap มาใส่ตรงนี้
# ==========================================
CMC_API_KEY = "YOUR_API_KEY_HERE"

# ระบบ Cache เก็บรายชื่อเหรียญไว้ 1 ชั่วโมง (3600 วินาที) จะได้ไม่เปลืองโควต้า API ฟรี
cached_top_10_list = []
last_list_fetch_time = 0
CACHE_DURATION = 3600  

def fetch_coin_list():
    """ดึงรายชื่อ Top 10 จาก CMC (หลัก) หรือ CG (สำรอง)"""
    global cached_top_10_list, last_list_fetch_time
    current_time = time.time()
    
    # ถ้ายังไม่ครบ 1 ชั่วโมง ให้ใช้รายชื่อเดิมจากรอบที่แล้ว
    if cached_top_10_list and (current_time - last_list_fetch_time < CACHE_DURATION):
        return cached_top_10_list

    exclude_symbols = ['usdt', 'usdc', 'steth', 'dai', 'wbtc', 'weeth', 'ton']
    results = []

    # --- 1. ลองดึงจาก CoinMarketCap (Primary) ---
    if CMC_API_KEY != "YOUR_API_KEY_HERE":
        try:
            url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
            params = {'start': '1', 'limit': '30', 'convert': 'USD'}
            headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': CMC_API_KEY}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data['data']:
                    symbol = item['symbol'].lower()
                    if symbol not in exclude_symbols:
                        results.append({'name': item['name'], 'symbol': symbol.upper()})
                    if len(results) == 10: break
                
                if results:
                    print("✅ อัปเดตอันดับเหรียญจาก CoinMarketCap สำเร็จ")
                    cached_top_10_list = results
                    last_list_fetch_time = current_time
                    return results
            else:
                print(f"⚠️ CoinMarketCap Error: {response.status_code} - ลองใช้ API สำรอง...")
        except Exception as e:
            print(f"⚠️ CoinMarketCap Connection Error: {e}")

    # --- 2. ถ้า CMC พัง หรือยังไม่ได้ใส่ API Key -> สลับมาใช้ CoinGecko (Fallback) ---
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 30, "page": 1, "sparkline": False}
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for item in data:
                symbol = item['symbol'].lower()
                if symbol not in exclude_symbols:
                    results.append({'name': item['name'], 'symbol': symbol.upper()})
                if len(results) == 10: break
                
            if results:
                print("🔄 ใช้รายชื่อเหรียญจาก CoinGecko (API สำรอง)")
                cached_top_10_list = results
                last_list_fetch_time = current_time
                return results
    except Exception as e:
        print(f"❌ CoinGecko Error: {e}")

    return cached_top_10_list # ถ้าพังทั้งคู่ ให้ใช้ของเก่าที่เคยดึงได้

def get_top_10_coins():
    """ดึงรายชื่อเหรียญ (จาก Cache) แล้วไปเอา 'ราคาล่าสุด' จาก Binance"""
    top_10_base = fetch_coin_list()
    
    if not top_10_base:
        return []

    # --- 3. ดึงราคา + เปอร์เซ็นต์ แบบ Real-time จาก Binance ---
    try:
        # โหลดราคาของทุกเหรียญรวดเดียว (เร็วกว่าและไม่เปลืองโควต้า Binance)
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=10)
        binance_data = response.json()
        
        # จัดข้อมูลให้อยู่ในรูป Dictionary เพื่อให้ค้นหาราคาได้เร็วๆ
        binance_dict = {item['symbol']: item for item in binance_data}
        
        final_results = []
        for coin in top_10_base:
            binance_pair = coin['symbol'] + "USDT"
            
            # จับคู่รายชื่อเหรียญ กับ ราคาของ Binance
            if binance_pair in binance_dict:
                b_info = binance_dict[binance_pair]
                price = float(b_info['lastPrice'])
                percent = float(b_info['priceChangePercent'])
            else:
                price = 0.0
                percent = 0.0
                
            final_results.append({
                'id': binance_pair,
                'name': coin['name'],
                'symbol': coin['symbol'],
                'price': price,
                'percent': percent
            })
            
        return final_results
    except Exception as e:
        print(f"❌ Binance Price Error: {e}")
        return []

def get_coin_ohlc(symbol, interval='1m', limit=60):
    """ดึงกราฟแท่งเทียน 1 นาที ย้อนหลัง 60 แท่ง จาก Binance"""
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if isinstance(data, dict): return None
            
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        return df
    except Exception as e:
        return None

def get_ema_values(symbol, emas):

    df = history_manager.update_and_get_data(symbol, "1m")

    if df is None or df.empty:
        return None

    price = df["close"].iloc[-1]

    # กำหนดค่าเริ่มต้น
    ema_short = None
    ema_mid = None
    ema_long = None

    if len(emas) >= 1:
        ema_short = df["close"].ewm(span=emas[0], adjust=False).mean().iloc[-1]

    if len(emas) >= 2:
        ema_mid = df["close"].ewm(span=emas[1], adjust=False).mean().iloc[-1]

    if len(emas) >= 3:
        ema_long = df["close"].ewm(span=emas[2], adjust=False).mean().iloc[-1]

    # ===== PRINT STATUS =====
    print(f"\n📊 {symbol}")
    print(f"Price: {price:.4f}")

    if ema_short:
        status = "⬆️ Above" if price > ema_short else "⬇️ Below"
        print(f"EMA{emas[0]}: {ema_short:.4f} ({status})")

    if ema_mid:
        status = "⬆️ Above" if price > ema_mid else "⬇️ Below"
        print(f"EMA{emas[1]}: {ema_mid:.4f} ({status})")

    if ema_long:
        status = "⬆️ Above" if price > ema_long else "⬇️ Below"
        print(f"EMA{emas[2]}: {ema_long:.4f} ({status})")

    return {
        "short": ema_short,
        "mid": ema_mid,
        "long": ema_long,
        "price": price
    }