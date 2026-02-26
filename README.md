# בוט הפקדות טלגרם | Deposit Bot

בוט טלגרם להפקדות – צד לקוח + צד עובד (Back Office).  
Python 3.10+, python-telegram-bot v20+.

## התקנה

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/deposit_bot.git
cd deposit_bot

# Virtual environment (מומלץ)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Dependencies
pip install -r requirements.txt

# Config
cp .env.example .env
# ערוך .env והזן BOT_TOKEN, ADMIN_CHAT_ID, ADMIN_USER_IDS
```

## הרצה

```bash
python bot.py
```

## משתני סביבה (.env)

| משתנה | תיאור |
|-------|--------|
| `BOT_TOKEN` | הטוקן מ־@BotFather |
| `ADMIN_CHAT_ID` | מזהה הצ'אט/קבוצה של הנציגים (מספר שלילי לקבוצה) |
| `ADMIN_USER_IDS` | מזהי משתמש של עובדים, מופרדים בפסיק |

## הרצה ב־VPS

1. העתק את הפרויקט ל־VPS
2. צור קובץ `.env` עם הערכים שלך
3. הרץ: `python bot.py`
4. לשימוש ב־systemd או screen: `nohup python bot.py &`
