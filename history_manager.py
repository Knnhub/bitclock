#history_manager.py
import os
import pandas as pd
import requests

# สร้างโฟลเดอร์เก็บข้อมูลอัตโนมัติถ้ายังไม่มี
SAVE_DIR = "crypto_data"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def update_and_get_data(symbol, interval):
    """
    ฟังก์ชันอัจฉริยะ: ดึงข้อมูลจาก CSV เดิม -> เช็คเวลาล่าสุด -> ดึงส่วนต่างจาก API -> เซฟทับ -> ส่งข้อมูลไปวาดกราฟ
    """
    file_path = os.path.join(SAVE_DIR, f"{symbol}_{interval}.csv")
    binance_symbol = symbol + 'USDT'
    
    # 1. เช็คว่ามีไฟล์เก่าไหม
    if os.path.exists(file_path):
        # มีไฟล์เก่า: โหลดขึ้นมา
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        
        # หาเวลาล่าสุดที่มีในเครื่อง (แปลงเป็น Timestamp มิลลิวินาที)
        last_time_ms = int(df['date'].max().timestamp() * 1000)
        
        # ดึงเฉพาะของใหม่ที่เพิ่งเกิดหลังจาก last_time_ms
        new_data = fetch_from_binance(binance_symbol, interval, start_time=last_time_ms)
        
        if not new_data.empty:
            # เอาของใหม่มาต่อท้ายของเก่า แล้วลบข้อมูลซ้ำ (เผื่อแท่งสุดท้ายยังไม่จบ)
            df = pd.concat([df, new_data]).drop_duplicates(subset=['date'], keep='last')
            df.sort_values('date', inplace=True)
            df.to_csv(file_path, index=False) # เซฟทับไฟล์เดิม
            # print(f"✅ อัปเดต {symbol} ({interval}) ดึงของใหม่มาเพิ่ม {len(new_data)} แท่ง")
            
    else:
        # ไม่มีไฟล์เก่า: ดึงใหม่ทั้งหมด 1,000 แท่ง
        # print(f"ดาวน์โหลดข้อมูลใหม่ทั้งหมดสำหรับ {symbol} ({interval})...")
        df = fetch_from_binance(binance_symbol, interval)
        if not df.empty:
            df.to_csv(file_path, index=False)
            
    return df

def fetch_from_binance(symbol, interval, start_time=None):
    """ฟังก์ชันย่อยสำหรับคุยกับ Binance API"""
    url = "https://api.binance.com/api/v3/klines"
    params = {'symbol': symbol, 'interval': interval, 'limit': 1000}
    if start_time:
        params['startTime'] = start_time
        
    try:
        res = requests.get(url, params=params, timeout=10).json()
        if not res or isinstance(res, dict): return pd.DataFrame()
            
        df = pd.DataFrame(res, columns=['date', 'open', 'high', 'low', 'close', 'volume', 'ct', 'qv', 'tr', 'tb', 'tq', 'ig'])
        df['date'] = pd.to_datetime(df['date'], unit='ms')
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        return df
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return pd.DataFrame()