import smtplib
import time
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_USER = "66011212205@msu.ac.th"
EMAIL_PASS = "ppwygwhrcmirgepg"

# cooldown 15 นาที
COOLDOWN_SECONDS = 900

# เก็บเวลาส่งล่าสุด
last_email_time = 0


def send_email(subject, message, to_email):
    global last_email_time

    now = time.time()

    # เช็ค cooldown
    if now - last_email_time < COOLDOWN_SECONDS:
        print("Email cooldown active, skip sending")
        return

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        last_email_time = now
        print("Email sent!")

    except Exception as e:
        print("Email error:", e)