import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================
# ⚙️ ตั้งค่าข้อมูลอีเมล
# ==========================================
SENDER_EMAIL = "66011212205@msu.ac.th"      # 👈 ใส่อีเมล Gmail ของคุณ (ผู้ส่ง)
SENDER_PASSWORD = "ppwygwhrcmirgepg"    # 👈 ใส่ App Password 16 หลัก (ไม่ต้องมีเว้นวรรคก็ได้)
RECEIVER_EMAIL = "phoophachanthayung@gmail.com"  # 👈 ใส่อีเมลผู้รับ (อาจจะเป็นอีเมลตัวเองก็ได้เพื่อทดสอบ)

def send_ema_alert(coin_symbol, cross_type, current_price):
    """ฟังก์ชันสำหรับส่งอีเมลแจ้งเตือน"""
    
    # 1. ตั้งค่าหัวข้อและเนื้อหาอีเมล
    subject = f"🚨 BitClock Alert: {coin_symbol} เกิดสัญญาณ {cross_type}!"
    
    body = f"""
    แจ้งเตือนจากระบบ BitClock Station
    -----------------------------------
   
    
    *นี่คือข้อความอัตโนมัติจากโปรแกรมของคุณ*
    """

    # 2. จัดรูปแบบข้อความ (MIME)
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 3. เชื่อมต่อเซิร์ฟเวอร์ Gmail และส่งข้อความ
    try:
        print("กำลังเชื่อมต่อเซิร์ฟเวอร์อีเมล...")
        # ใช้พอร์ต 587 สำหรับ TLS
        server = smtplib.SMTP('smtp.gmail.com', 587) 
        server.starttls() # เข้ารหัสข้อมูล
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        print("กำลังส่งข้อความ...")
        server.send_message(msg)
        server.quit()
        
        print(f"✅ ส่งอีเมลแจ้งเตือน {coin_symbol} สำเร็จ!")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการส่งอีเมล: {e}")

# ==========================================
# 🚀 จำลองการเกิดเหตุการณ์ EMA ตัดกัน
# ==========================================
if __name__ == "__main__":
    print("เริ่มทดสอบระบบส่งอีเมล...")
    
    # สมมติว่าโปรแกรมตรวจพบว่า EMA 12 ตัด EMA 26 ขึ้น (Golden Cross) ของ BTC
    test_coin = "BTC/USDT"
    test_signal = "Golden Cross (ขาขึ้น 🚀)"
    test_price = 65432.10
    
    send_ema_alert(test_coin, test_signal, test_price)