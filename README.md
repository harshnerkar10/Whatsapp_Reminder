# 📲 WhatsApp Reminder Bot

A smart Flask-based WhatsApp Reminder Bot that allows users to send reminder messages (like "Remind me to take medicine at 5 PM today") and receive WhatsApp notifications at the exact scheduled time using **Twilio** and **Google Sheets**.

---

## 🚀 Features

- ✅ Accepts natural language reminder commands (e.g., "Remind me to drink water at 3 PM").
- 🧠 Parses time using `dateparser` with support for "today", "tomorrow", AM/PM, and specific formats.
- 📅 Stores reminders in a Google Sheet for persistence.
- ⏰ Sends timely WhatsApp notifications using Twilio.
- 🔁 Background thread checks every 20 seconds for pending reminders.
- 🌐 Built with Flask for easy webhook/API management.
- 🇮🇳 Timezone: `Asia/Kolkata`

---

## 🛠️ Technologies Used

- **Python 3**
- **Flask**
- **Twilio API**
- **Google Sheets API** (`gspread`, `oauth2client`)
- **dateparser**
- **threading**
- **schedule** (optional)

---

## 📦 Project Structure


