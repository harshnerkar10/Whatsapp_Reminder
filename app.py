from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from datetime import datetime
import threading
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import dateparser
import os
import platform

# 🕐 Set timezone
os.environ['TZ'] = 'Asia/Kolkata'
if platform.system() != 'Windows':
    time.tzset()

app = Flask(__name__)

# 🔐 Twilio Credentials
account_sid = 'ACc2d2c9997e3bc7e93157b501bba6566d'  # ✔️ Replace with valid SID
auth_token = '3b4ecfcc1c8ee2459064286cafe4897d'   # ✔️ Replace with valid token
from_number = 'whatsapp:+14155238886'
twilio_client = Client(account_sid, auth_token)

# 📄 Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Reminders").sheet1  # First sheet with headers: time | task | sender

# 🧠 Extract time string from message
def extract_time_text(message):
    patterns = [
        r"(tomorrow\s+at\s+\d{1,2}(:\d{2})?\s*(am|pm))",
        r"(today\s+at\s+\d{1,2}(:\d{2})?\s*(am|pm))",
        r"(at\s+\d{1,2}(:\d{2})?\s*(am|pm))",
        r"(\d{1,2}(:\d{2})?\s*(am|pm))",
        r"\d{1,2}:\d{2}\s+\d{1,2}-\d{1,2}-\d{4}"
    ]
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(0)
    return None

# 📲 WhatsApp webhook
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get("Body", "").strip()
    sender_number = request.values.get("From", "").strip()
    resp = MessagingResponse()
    msg = resp.message()

    print(f"📩 Message received: {incoming_msg} from {sender_number}")

    time_text = extract_time_text(incoming_msg)
    if not time_text:
        msg.body("⚠️ Please include time like 'Remind me to call mom at 5 PM today'.")
        return str(resp)

    parsed_time = dateparser.parse(
        time_text,
        settings={
            'PREFER_DATES_FROM': 'future',
            'RELATIVE_BASE': datetime.now(),
            'TIMEZONE': 'Asia/Kolkata',
            'RETURN_AS_TIMEZONE_AWARE': False
        }
    )

    if parsed_time and parsed_time > datetime.now():
        parsed_time = parsed_time.replace(second=0, microsecond=0)
        formatted_time = parsed_time.strftime("%Y-%m-%d %H:%M")
        task = incoming_msg.replace(time_text, "").strip().rstrip(".,;:") or "Reminder"

        try:
            sheet.append_row([formatted_time, task, sender_number])
            msg.body(f"✅ Reminder set for *{parsed_time.strftime('%A %I:%M %p')}*: *{task}*")
            print(f"✅ Stored to sheet: {formatted_time} | {task} | {sender_number}")
        except Exception as e:
            msg.body("❌ Error saving your reminder.")
            print("❌ Google Sheet Error:", e)
    else:
        msg.body("⚠️ The time seems to be invalid or in the past.")

    return str(resp)

# 🛎️ Reminder checker (for current minute)
def check_reminders():
    now = datetime.now().replace(second=0, microsecond=0)
    try:
        rows = sheet.get_all_records()
        for i, row in enumerate(rows):
            reminder_time_str = str(row.get("time", "")).strip()
            try:
                reminder_time = datetime.strptime(reminder_time_str, "%Y-%m-%d %H:%M")
                diff = abs((reminder_time - now).total_seconds())
                print(f"🔍 Checking: {reminder_time} vs now: {now} | diff: {diff}s")
                if diff < 60:
                    task = row.get("task", "").strip()
                    recipient = row.get("sender", "").strip()
                    try:
                        twilio_client.messages.create(
                            body=f"🔔 Reminder: {task}",
                            from_=from_number,
                            to=recipient
                        )
                        print(f"✅ Sent to {recipient}: {task}")
                        sheet.delete_rows(i + 2)  # header offset
                    except Exception as e:
                        print(f"❌ Failed to send to {recipient}: {e}")
            except Exception as e:
                print(f"⚠️ Failed to parse reminder time: {reminder_time_str} | Error: {e}")
    except Exception as e:
        print("❌ Failed to read sheet:", e)

# 🔁 Run reminder checker every 20 seconds
def run_scheduler():
    print("📅 Scheduler started...")
    while True:
        check_reminders()
        time.sleep(20)

# 🧪 Test endpoint
@app.route("/test", methods=["GET"])
def test():
    try:
        msg = twilio_client.messages.create(
            body="✅ This is a test message from your Reminder Bot",
            from_=from_number,
            to="whatsapp:+917522946205"
        )
        print("✅ Test message sent:", msg.sid)
        return "✅ Test message sent."
    except Exception as e:
        print("❌ Test failed:", e)
        return f"❌ Failed: {e}", 500

# 🚀 Start Flask + Scheduler
if __name__ == "__main__":
    threading.Thread(target=run_scheduler, daemon=True).start()
    print("🌐 Running Flask on http://localhost:5000")
    app.run(port=5000)
