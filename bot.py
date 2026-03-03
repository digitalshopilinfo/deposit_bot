<<<<<<< Updated upstream
"""
בוט הפקדות טלגרם - צד לקוח + צד עובד (Back Office)
python-telegram-bot v20+
"""
import asyncio
import os
import re
import time
=======
import os
>>>>>>> Stashed changes
import sqlite3
import logging
import html
from datetime import datetime, timedelta
<<<<<<< Updated upstream
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
=======

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
>>>>>>> Stashed changes
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# CONFIG
# =========================
<<<<<<< Updated upstream
load_dotenv()

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
ADMIN_CHAT_ID = int((os.getenv("ADMIN_CHAT_ID") or "0").strip() or "0")
ADMIN_USER_IDS = set()
_raw = (os.getenv("ADMIN_USER_IDS") or "").strip()
if _raw:
    for x in _raw.split(","):
        if x.strip().isdigit():
            ADMIN_USER_IDS.add(int(x.strip()))
DB_PATH = os.getenv("DB_PATH") or "deposit_bot.db"
=======
load_dotenv("_env")  # טוען מ-_env (אפשר גם .env)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0").strip() or "0")

ADMIN_USER_IDS = set()
_raw_admins = os.getenv("ADMIN_USER_IDS", "").strip()
if _raw_admins:
    for x in _raw_admins.split(","):
        x = x.strip()
        if x.isdigit():
            ADMIN_USER_IDS.add(int(x))

DB_PATH = os.getenv("DB_PATH", "deposit_bot.db")
>>>>>>> Stashed changes

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# =========================
<<<<<<< Updated upstream
# FLOW
# =========================
QUICK_AMOUNTS = [300, 400, 500, 600, 700, 800, 900, 1000]
CUSTOM_MIN_AMOUNT = 1000

PAYMENT_METHODS = [
    ("bit", "🟢 תשלום בביט"),
    ("bank", "🏦 העברה בנקאית"),
]

# סדר לשני טורים: ימני (שורות 0-3) | שמאלי (שורות 0-3)
BANKS_RIGHT = ["בנק לאומי", "בנק הפועלים", "בנק דיסקונט/מרכנתיל", "בנק מזרחי טפחות"]
BANKS_LEFT = ["הבנק הבינלאומי", "בנק One zero", "בנק יהב", "בנק מסד"]
BANKS = BANKS_RIGHT + BANKS_LEFT  # אינדקס 0-3 ימני, 4-7 שמאלי
BANK_TO_ENGLISH = {
    "בנק לאומי": "Bank Leumi",
    "בנק הפועלים": "Bank Hapoalim",
    "בנק דיסקונט/מרכנתיל": "Bank Discount/Mercantile",
    "בנק מזרחי טפחות": "Bank Mizrahi Tefahot",
    "הבנק הבינלאומי": "Bank Habinleumi",
    "בנק One zero": "Bank One Zero",
    "בנק יהב": "Bank Yahav",
    "בנק מסד": "Bank Massad",
}
BANK_OTHER = "בנק אחר"

def bank_for_admin(hebrew_name):
    """Returns English bank name for admin display."""
    return BANK_TO_ENGLISH.get(hebrew_name, hebrew_name)

BANK_SELECT_TEXT = "מאיזה בנק את/ה מעביר?"
BANK_OTHER_PROMPT_TEXT = "הקלד את שם הבנק שממנו את/ה מעביר"

START_INTRO_TEXT = (
    "ברוכים הבאים לבוט ההפקדות של 888 🎰\n"
    "הפקדה מהירה – בדרך כלל פחות מדקה ⏱️\n"
    "ותוכלו להתחיל לשחק מיידי!\n"
    "מוכנים? לחצו למטה כדי להתחיל 👇"
)
WELCOME_TEXT = "כמה תרצה/י להפקיד היום 💰"
AMOUNT_SELECT_ONLY_TEXT = "ניתן לבחור אך ורק מהאופציות הקיימות.\nאנא לחץ על הסכום הרצוי."

SITE_USER_TEXT = (
    "כדי לשייך את ההפקדה לחשבון שלך 👤\n"
    "שלח/י את שם המשתמש באתר בדיוק כמו שמופיע שם\n"
    "✅ מומלץ להעתיק ולהדביק (חשוב מאוד)"
)

AWAIT_USERNAME_TEXT = "⏳ אנא המתן, המערכת מאתרת את חשבונך..."
USERNAME_FOUND_TEXT = "✅ מצאנו את החשבון שלך. ממשיכים!"
USERNAME_INVALID_TEXT = "לא מצאנו את שם המשתמש הזה במערכת ❌\nשלח/י שוב את שם המשתמש בדיוק כמו שמופיע באתר."
WAIT_FOR_DETAILS_TEXT = "אנא המתן מיד נשלח לך פרטי העברה.. ⏳"

RECEIPT_ONLY_PHOTO_TEXT = "כאן אפשר לשלוח רק צילום מסך של האסמכתא (תמונה בלבד)📸"
RECEIPT_CHECKING_TEXT = "האסמכתא ששלחת נמצאת בבדיקה, מיד נעדכן ⏳"

AFTER_RECEIPT_TEXT = "קיבלתי ✅\nשולח לבדיקה, מיד נעדכן אותך ⏳"

SUCCESS_TEXT = "✅ ההפקדה בוצעה בהצלחה והיתרה באתר עודכנה. בהצלחה! 🎉"
def problem_text_for_client(uid):
    return (
        "❌ יש בעיה עם ההפקדה ולא הצלחנו להשלים אותה כרגע! ❌\n"
        "נא לפנות לנציג שירות בשעות הפעילות.\n"
        f"מספר פנייה: {uid}"
    )
METHOD_SELECT_TEXT = "💳 בחר/י שיטת תשלום:"
PAYMENT_METHOD_UNAVAILABLE_TEXT = "❌ שיטת התשלום שבחרת לא זמינה כעת, אנא בחר שיטת תשלום אחרת."
MORE_INFO_TEXT = (
    "🔄 לא הצלחנו לאמת את התשלום.\n"
    "בבקשה שלח/י אסמכתא חדשה וברורה שבה רואים:\n"
    "• מספר אסמכתא\n"
    "• סכום\n"
    "• תאריך ושעה\n"
    "📸 שלח/י עכשיו צילום מסך חדש (תמונה בלבד)."
)

REMINDER_TEXT = "⏱️ תזכורת: אם כבר ביצעת תשלום – שלח/י צילום מסך של האסמכתא כדי להשלים את ההפקדה."
REMINDER_MINUTES = 8
RETURN_TO_MENU_SECONDS = 120

# Admin-side (English + Spanish)
ADM_PAYMENT_REQUEST = "🧾 Payment details request (before receipt) | Solicitud de datos de pago (antes del comprobante)"
ADM_USERNAME_CHECK = "👤 Username verification | Verificación de usuario"
ADM_RECEIPT_UPDATED = "🔄 Receipt updated (resent) | Comprobante actualizado (reenviado)"
ADM_NEW_DEPOSIT = "🧾 New deposit request | Nueva solicitud de depósito"
ADM_MSG_DELIVERED = "✅ Message delivered to client | Mensaje entregado al cliente"
ADM_CANT_ATTACH = "❌ Could not attach image | No pude adjuntar la imagen"
ADM_ERROR = "❌ Error | Error"
ADM_SUCCESS_SENT = "✅ Approved | Aprobado"
ADM_PROBLEM_SENT = "❌ Marked as problem | Marcado como problema"
ADM_MORE_SENT = "🔄 New receipt requested | Nuevo comprobante solicitado"
ADM_CANT_SEND = "❌ Could not send to client | No pude enviar al cliente"

ADM_BTN_SUCCESS = "✅ Success | Éxito"
ADM_BTN_MORE = "🔄 New receipt | Nuevo comprobante"
ADM_BTN_PROBLEM = "❌ Problem | Problema"
ADM_BTN_USERNAME_OK = "✅ Valid | Válido"
ADM_BTN_USERNAME_BAD = "❌ Invalid | Inválido"

# States
S_AMOUNT, S_CUSTOM_AMOUNT, S_SITE_USER, S_METHOD = "AMOUNT", "CUSTOM_AMOUNT", "SITE_USER", "METHOD"
S_BANK_SELECTION, S_BANK_OTHER = "BANK_SELECTION", "BANK_OTHER"
S_AWAIT_USERNAME_VALIDATION = "AWAIT_USERNAME_VALIDATION"
S_WAIT_PAYMENT_DETAILS, S_WAIT_RECEIPT, S_WAIT_RECEIPT_MORE, S_LOCKED = (
    "WAIT_PAYMENT_DETAILS", "WAIT_RECEIPT", "WAIT_RECEIPT_MORE", "LOCKED"
)
EMPLOYEE_PENDING_STATES = (S_AWAIT_USERNAME_VALIDATION, S_WAIT_PAYMENT_DETAILS, S_WAIT_RECEIPT, S_WAIT_RECEIPT_MORE)
=======
# FLOW SETTINGS
# =========================
QUICK_AMOUNTS = [300, 400, 500, 600, 700, 800, 900, 1000]
CUSTOM_MIN_AMOUNT = 1000  # סכום אחר מינימום 1000+

PAYMENT_METHODS = [
    ("bit", "Bit"),
    ("bank", "העברה בנקאית"),
    ("paybox", "PayBox"),
]

WELCOME_TEXT = (
    "ברוכים הבאים, לבוט ההפקדות של 888\n"
    "זמן ההפקדה פחות מדקה ותוכלי להתחיל לשחק מיידי!\n\n"
    "כמה אתה רוצה להפקיד?"
)

SITE_USER_TEXT = (
    "כדי לשייך את ההפקדה שלך,\n"
    "אנא כתוב את שם המשתמש שלך באתר, **חשוב מאוד** בדיוק כמו שמופיע באתר (אפשר להעתיק ולהדביק)."
)

WAIT_FOR_DETAILS_TEXT = "אנא המתן מיד נשלח לך פרטי העברה.. ⏳"

RECEIPT_ONLY_PHOTO_TEXT = "כאן אפשר לשלוח *רק צילום מסך* של האסמכתא (תמונה בלבד)."

AFTER_RECEIPT_TEXT = "קיבלתי ✅\nשולח לבדיקה, נעדכן אותך פה"

SUCCESS_TEXT = "✅ ההפקדה שלך בוצע בהצלחה ויתרת הנקודות באתר התעדכנה"
PROBLEM_TEXT = "❌ יש בעיה עם ההפקדה שלך, אנה פנה לנציג שירות בשעות הפעילות להמשך בירור (14:00-22:00)"
MORE_INFO_TEXT = (
    "🔄 לא הצלחנו לאמת את התשלום. שלח אסמכתא ברורה/בדוק פרטים.\n"
    "יש לשים לב שמספר האסמכתא, הסכום, התאריך והשעה מופיעים בצורה ברורה!\n\n"
    "שלח עכשיו צילום מסך חדש וברור (תמונה בלבד)."
)

REMINDER_TEXT = "תזכורת⏱️ אם כבר ביצעת תשלום – שלח צילום מסך של האסמכתא כדי להשלים את ההפקדה."
REMINDER_MINUTES = 7

RETURN_TO_MENU_SECONDS = 120  # אחרי הצלחה: 2 דקות לחזרה לתפריט

# =========================
# STATES (user-side)
# =========================
S_AMOUNT = "AMOUNT"
S_CUSTOM_AMOUNT = "CUSTOM_AMOUNT"
S_SITE_USER = "SITE_USER"
S_METHOD = "METHOD"
S_WAIT_PAYMENT_DETAILS = "WAIT_PAYMENT_DETAILS"
S_WAIT_RECEIPT = "WAIT_RECEIPT"
S_WAIT_RECEIPT_MORE = "WAIT_RECEIPT_MORE"
S_LOCKED = "LOCKED"
>>>>>>> Stashed changes

# =========================
# DB
# =========================
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

<<<<<<< Updated upstream
def now_utc():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

def gen_request_id():
    import random
    return f"DEP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"

def init_db():
    c = db()
    cur = c.cursor()
=======
def init_db():
    conn = db()
    cur = conn.cursor()

>>>>>>> Stashed changes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS locks (
            user_id INTEGER PRIMARY KEY,
            locked INTEGER NOT NULL DEFAULT 0
        )
    """)
<<<<<<< Updated upstream
    cur.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT,
=======

    cur.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT UNIQUE,
>>>>>>> Stashed changes
            user_id INTEGER,
            username TEXT,
            amount INTEGER,
            site_user TEXT,
            method TEXT,
            status TEXT,
            created_at TEXT
        )
    """)
<<<<<<< Updated upstream
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin_pending (
            admin_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            method TEXT,
            created_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS awaiting_receipt (
            user_id INTEGER PRIMARY KEY,
            request_id TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS client_pending (
            user_id INTEGER PRIMARY KEY,
            amount INTEGER,
            site_user TEXT,
            method TEXT,
            bank TEXT,
            created_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS awaiting_username (
            user_id INTEGER PRIMARY KEY,
            site_user TEXT,
            amount INTEGER,
            created_at TEXT
        )
    """)
    try:
        cur.execute("ALTER TABLE client_pending ADD COLUMN bank TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE locks ADD COLUMN locked_until TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE locks ADD COLUMN lock_reason TEXT")
    except sqlite3.OperationalError:
        pass
    c.commit()
    c.close()

def log_request(rid, user_id, username, amount, site_user, method, status):
    c = db()
    c.cursor().execute(
        "INSERT INTO requests(request_id, user_id, username, amount, site_user, method, status, created_at) VALUES(?,?,?,?,?,?,?,?)",
        (rid, user_id, username or "", amount, site_user, method, status, now_utc())
    )
    c.commit()
    c.close()

def update_request_status(rid, status):
    c = db()
    c.cursor().execute(
        "UPDATE requests SET status=?, created_at=? WHERE request_id=?",
        (status, now_utc(), rid)
    )
    c.commit()
    c.close()

PROBLEM_LOCK_HOURS = 4

def is_locked(uid):
    c = db()
    r = c.cursor().execute(
        "SELECT locked, locked_until FROM locks WHERE user_id=?",
        (uid,)
    ).fetchone()
    c.close()
    if not r or not r[0]:
        return False
    locked_until = r[1] if len(r) > 1 else None
    if locked_until:
        try:
            from datetime import datetime as dt
            until = dt.strptime(locked_until, "%Y-%m-%d %H:%M:%S")
            if dt.utcnow() >= until:
                set_locked(uid, False)
                return False
        except Exception:
            pass
    return True

def get_lock_reason(uid):
    c = db()
    r = c.cursor().execute(
        "SELECT lock_reason FROM locks WHERE user_id=? AND locked=1",
        (uid,)
    ).fetchone()
    c.close()
    return (r[0] if r and len(r) > 0 else None) or ""

def set_locked(uid, locked, lock_hours=None, lock_reason=None):
    locked_until = None
    reason = lock_reason
    if locked and lock_hours:
        from datetime import datetime as dt
        until = dt.utcnow() + timedelta(hours=lock_hours)
        locked_until = until.strftime("%Y-%m-%d %H:%M:%S")
    c = db()
    if locked:
        c.cursor().execute(
            "INSERT OR REPLACE INTO locks(user_id, locked, locked_until, lock_reason) VALUES(?,?,?,?)",
            (uid, 1, locked_until, reason or "")
        )
    else:
        c.cursor().execute(
            "INSERT OR REPLACE INTO locks(user_id, locked, locked_until, lock_reason) VALUES(?,?,?,?)",
            (uid, 0, None, "")
        )
    c.commit()
    c.close()

def set_admin_pending(admin_id, user_id, method):
    c = db()
    c.cursor().execute(
        "INSERT OR REPLACE INTO admin_pending(admin_id, user_id, method, created_at) VALUES(?,?,?,?)",
        (admin_id, user_id, method, now_utc())
    )
    c.commit()
    c.close()

def get_admin_pending(admin_id):
    c = db()
    r = c.cursor().execute("SELECT user_id, method FROM admin_pending WHERE admin_id=?", (admin_id,)).fetchone()
    c.close()
    return r

def clear_admin_pending(admin_id):
    c = db()
    c.cursor().execute("DELETE FROM admin_pending WHERE admin_id=?", (admin_id,))
    c.commit()
    c.close()

def set_awaiting_receipt(user_id, rid):
    c = db()
    c.cursor().execute("INSERT OR REPLACE INTO awaiting_receipt(user_id, request_id) VALUES(?,?)", (user_id, rid))
    c.commit()
    c.close()

def get_awaiting_receipt(user_id):
    c = db()
    r = c.cursor().execute("SELECT request_id FROM awaiting_receipt WHERE user_id=?", (user_id,)).fetchone()
    c.close()
    return r[0] if r else None

def get_request_by_rid(rid):
    c = db()
    r = c.cursor().execute(
        "SELECT user_id, amount, site_user, method FROM requests WHERE request_id=? ORDER BY id DESC LIMIT 1",
        (rid,)
    ).fetchone()
    c.close()
    if not r:
        return None
    return {"user_id": r[0], "amount": r[1], "site_user": r[2] or "", "method": r[3]}

def clear_awaiting_receipt(user_id):
    c = db()
    c.cursor().execute("DELETE FROM awaiting_receipt WHERE user_id=?", (user_id,))
    c.commit()
    c.close()

def set_client_pending(user_id, amount, site_user, method, bank=None):
    c = db()
    c.cursor().execute(
        "INSERT OR REPLACE INTO client_pending(user_id, amount, site_user, method, bank, created_at) VALUES(?,?,?,?,?,?)",
        (user_id, amount, site_user or "", method, bank or "", now_utc())
    )
    c.commit()
    c.close()

def get_client_pending(user_id):
    c = db()
    r = c.cursor().execute(
        "SELECT amount, site_user, method, bank FROM client_pending WHERE user_id=?",
        (user_id,)
    ).fetchone()
    c.close()
    if r:
        return {
            "amount": r["amount"],
            "site_user": r["site_user"] or "",
            "method": r["method"],
            "bank": (r["bank"] or "") if "bank" in r.keys() else "",
        }
    return None

def clear_client_pending(user_id):
    c = db()
    c.cursor().execute("DELETE FROM client_pending WHERE user_id=?", (user_id,))
    c.commit()
    c.close()

def set_awaiting_username(user_id, site_user, amount):
    c = db()
    c.cursor().execute(
        "INSERT OR REPLACE INTO awaiting_username(user_id, site_user, amount, created_at) VALUES(?,?,?,?)",
        (user_id, site_user, amount, now_utc())
    )
    c.commit()
    c.close()

def get_awaiting_username(user_id):
    c = db()
    r = c.cursor().execute(
        "SELECT site_user, amount FROM awaiting_username WHERE user_id=?",
        (user_id,)
    ).fetchone()
    c.close()
    return dict(zip(r.keys(), r)) if r else None

def clear_awaiting_username(user_id):
    c = db()
    c.cursor().execute("DELETE FROM awaiting_username WHERE user_id=?", (user_id,))
    c.commit()
    c.close()
=======

    # pending guidance for admins (admin clicks button -> next message becomes details)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin_pending (
            admin_id INTEGER,
            user_id INTEGER,
            method TEXT,
            created_at TEXT,
            PRIMARY KEY (admin_id)
        )
    """)

    conn.commit()
    conn.close()

def now_utc():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

def gen_request_id():
    import random
    return f"DEP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"

def log_request(rid: str, user_id: int, username: str, amount: int, site_user: str, method: str, status: str):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO requests(request_id, user_id, username, amount, site_user, method, status, created_at)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
    """, (rid, user_id, username or "", amount, site_user, method, status, now_utc()))
    conn.commit()
    conn.close()

def is_locked(user_id: int) -> bool:
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT locked FROM locks WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return bool(row["locked"]) if row else False

def set_locked(user_id: int, locked: bool):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO locks(user_id, locked) VALUES(?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET locked=excluded.locked",
        (user_id, 1 if locked else 0),
    )
    conn.commit()
    conn.close()

def set_admin_pending(admin_id: int, user_id: int, method: str):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO admin_pending(admin_id, user_id, method, created_at)
        VALUES(?, ?, ?, ?)
        ON CONFLICT(admin_id) DO UPDATE SET user_id=excluded.user_id, method=excluded.method, created_at=excluded.created_at
    """, (admin_id, user_id, method, now_utc()))
    conn.commit()
    conn.close()

def get_admin_pending(admin_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, method, created_at FROM admin_pending WHERE admin_id=?", (admin_id,))
    row = cur.fetchone()
    conn.close()
    return row

def clear_admin_pending(admin_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("DELETE FROM admin_pending WHERE admin_id=?", (admin_id,))
    conn.commit()
    conn.close()
>>>>>>> Stashed changes

# =========================
# HELPERS
# =========================
<<<<<<< Updated upstream
def is_admin(uid):
    return uid in ADMIN_USER_IDS

def set_state(ctx, state):
    ctx.user_data["state"] = state

def get_state(ctx):
    return ctx.user_data.get("state", S_AMOUNT)

def get_waiting_msg_for_employee_pending(state):
    """Returns (text, parse_mode) to show when client acts during employee-pending state."""
    if state == S_AWAIT_USERNAME_VALIDATION:
        return ("אנא המתן, המערכת בודקת את החשבון שלך.", None)
    if state == S_WAIT_PAYMENT_DETAILS:
        return (WAIT_FOR_DETAILS_TEXT, None)
    if state in (S_WAIT_RECEIPT, S_WAIT_RECEIPT_MORE):
        return (RECEIPT_CHECKING_TEXT, None)
    return (None, None)

def _apply_client_state_override(uid, ctx):
    overrides = ctx.bot_data.get("client_state_override")
    if overrides and uid in overrides:
        data = overrides.pop(uid)
        ctx.user_data.update(data)

def set_client_state_override(ctx, uid, state, **kw):
    if "client_state_override" not in ctx.bot_data:
        ctx.bot_data["client_state_override"] = {}
    ctx.bot_data["client_state_override"][uid] = {"state": state, **kw}

def reset_flow(ctx):
    job = ctx.user_data.get("reminder_job")
=======
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_USER_IDS

def set_state(context: ContextTypes.DEFAULT_TYPE, state: str):
    context.user_data["state"] = state

def get_state(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("state", S_AMOUNT)

def reset_flow(context: ContextTypes.DEFAULT_TYPE):
    # cancel any reminder job stored in user_data
    job = context.user_data.get("reminder_job")
>>>>>>> Stashed changes
    if job:
        try:
            job.schedule_removal()
        except Exception:
            pass
<<<<<<< Updated upstream
    ctx.user_data.clear()
    set_state(ctx, S_AMOUNT)

def cancel_jobs(jq, name):
    if not jq:
        return
    for j in list(jq.jobs()):
=======
    context.user_data.clear()
    set_state(context, S_AMOUNT)

def amounts_kb():
    rows = []
    row = []
    for a in QUICK_AMOUNTS:
        row.append(InlineKeyboardButton(str(a), callback_data=f"amt:{a}"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("סכום אחר ✍️", callback_data="amt:custom")])
    # אין "ביטול" לפי בקשתך
    return InlineKeyboardMarkup(rows)

def methods_kb():
    rows = [[InlineKeyboardButton(lbl, callback_data=f"pm:{key}")] for key, lbl in PAYMENT_METHODS]
    rows.append([InlineKeyboardButton("🔙 חזרה", callback_data="nav:back_to_siteuser")])
    rows.append([InlineKeyboardButton("🏠 תפריט ראשי", callback_data="nav:home")])
    return InlineKeyboardMarkup(rows)

def back_home_kb(back_cb: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 חזרה", callback_data=back_cb)],
        [InlineKeyboardButton("🏠 תפריט ראשי", callback_data="nav:home")],
    ])

def admin_payment_details_kb(user_id: int, method_key: str):
    # button guides admin to send details (next message becomes details)
    label = {
        "bit": "📤 שלח פרטי Bit",
        "paybox": "📤 שלח פרטי PayBox",
        "bank": "📤 שלח פרטי העברה בנקאית",
    }.get(method_key, "📤 שלח פרטי תשלום")

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data=f"adp:{method_key}:{user_id}")],
        [InlineKeyboardButton("🔓 שחרור נעילה", callback_data=f"ad:unlock:{user_id}")],
        [InlineKeyboardButton("🚫 חסימה/נעילה", callback_data=f"ad:block:{user_id}")],
    ])

def admin_receipt_ticket_kb(rid: str, user_id: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ההפקדה שלך בוצע בהצלחה ויתרת הנקודות באתר התעדכנה", callback_data=f"ad:ok:{rid}:{user_id}")],
        [InlineKeyboardButton("❌ יש בעיה עם ההפקדה שלך, אנה פנה לנציג שירות בשעות הפעילות להמשך בירור (14:00-22:00)", callback_data=f"ad:problem:{rid}:{user_id}")],
        [InlineKeyboardButton("🔄 לא הצלחנו לאמת את התשלום. שלח אסמכתא ברורה/בדוק פרטים. יש לשים לב שמספר האסמכתא, הסכום, התאריך והשעה מופיעים בצורה ברורה!", callback_data=f"ad:more:{rid}:{user_id}")],
        [InlineKeyboardButton("🔓 שחרור נעילה", callback_data=f"ad:unlock:{user_id}")],
        [InlineKeyboardButton("🚫 חסימה/נעילה", callback_data=f"ad:block:{user_id}")],
    ])

# פילטר: צ'אט פרטי או קבוצה (למעט צ'אט האדמין)
def _user_chat_filter():
    base = filters.ChatType.PRIVATE
    if ADMIN_CHAT_ID:
        base = base | ((filters.ChatType.GROUP | filters.ChatType.SUPERGROUP) & ~filters.Chat(ADMIN_CHAT_ID))
    else:
        base = base | (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP)
    return base

USER_CHAT_FILTER = _user_chat_filter()

def cancel_jobs_by_name(job_queue, name: str):
    # best-effort: remove all jobs with this name
    if not job_queue:
        return
    for j in list(job_queue.jobs()):
>>>>>>> Stashed changes
        if j.name == name:
            try:
                j.schedule_removal()
            except Exception:
                pass

<<<<<<< Updated upstream
def _receipt_completed_set(ctx):
    if "receipt_completed_user_ids" not in ctx.bot_data:
        ctx.bot_data["receipt_completed_user_ids"] = set()
    return ctx.bot_data["receipt_completed_user_ids"]

def _mark_receipt_completed(ctx, uid):
    """סימון שהלקוח סיים הפקדה בהצלחה – התזכורת לא תישלח."""
    _receipt_completed_set(ctx).add(uid)

def _clear_receipt_completed(ctx, uid):
    """ניקוי לפני המתנה חדשה לאסמכתא (שליחת פרטי תשלום מחדש)."""
    _receipt_completed_set(ctx).discard(uid)

def _is_receipt_reminder_relevant(ctx, user_id):
    """האם התזכורת רלוונטית – העובד עדיין מחכה לאסמכתא."""
    return user_id not in _receipt_completed_set(ctx)

def _client_last_menu(ctx):
    if "client_last_menu" not in ctx.bot_data:
        ctx.bot_data["client_last_menu"] = {}
    return ctx.bot_data["client_last_menu"]

async def clear_client_menu(context, user_id):
    """Removes the last inline keyboard shown to this client (so only one menu is visible)."""
    last = _client_last_menu(context).get(user_id)
    if not last:
        return
    try:
        await context.bot.edit_message_reply_markup(
            chat_id=last["chat_id"],
            message_id=last["message_id"],
            reply_markup=None,
        )
    except Exception:
        pass
    finally:
        _client_last_menu(context).pop(user_id, None)

def save_client_menu(context, user_id, chat_id, message_id):
    """Stores the message that has the current menu for this client."""
    _client_last_menu(context)[user_id] = {"chat_id": chat_id, "message_id": message_id}

def _client_payment_details_msg(ctx):
    if "client_payment_details_msg" not in ctx.bot_data:
        ctx.bot_data["client_payment_details_msg"] = {}
    return ctx.bot_data["client_payment_details_msg"]

def _admin_payment_request_msg(ctx):
    """הודעה בקשת פרטי תשלום לאדמין – כדי להסיר כפתורים כשנשלחו פרטים."""
    if "admin_payment_request_msg" not in ctx.bot_data:
        ctx.bot_data["admin_payment_request_msg"] = {}
    return ctx.bot_data["admin_payment_request_msg"]

def save_admin_payment_request_msg(ctx, user_id, chat_id, message_id):
    _admin_payment_request_msg(ctx)[user_id] = {"chat_id": chat_id, "message_id": message_id}

async def _remove_admin_payment_request_buttons(ctx, user_id):
    """מסיר כפתורים מהודעת בקשת פרטי תשלום – כי העובד כבר שלח פרטים."""
    stored = _admin_payment_request_msg(ctx).pop(user_id, None)
    if stored:
        try:
            await ctx.bot.edit_message_reply_markup(
                chat_id=stored["chat_id"],
                message_id=stored["message_id"],
                reply_markup=None,
            )
        except Exception:
            pass

def _admin_revoke_msg(ctx):
    """הודעת 'Message delivered to client' עם כפתור Revoke – להסרת הכפתור כשהתשלום אושר."""
    if "admin_revoke_msg" not in ctx.bot_data:
        ctx.bot_data["admin_revoke_msg"] = {}
    return ctx.bot_data["admin_revoke_msg"]

def save_admin_revoke_msg(ctx, user_id, chat_id, message_id):
    _admin_revoke_msg(ctx)[user_id] = {"chat_id": chat_id, "message_id": message_id}

async def _remove_admin_revoke_buttons(ctx, user_id):
    """מסיר כפתור Revoke מהודעת 'Message delivered to client' – כי התשלום אושר."""
    stored = _admin_revoke_msg(ctx).pop(user_id, None)
    if stored:
        try:
            await ctx.bot.edit_message_reply_markup(
                chat_id=stored["chat_id"],
                message_id=stored["message_id"],
                reply_markup=None,
            )
        except Exception:
            pass

def save_client_payment_details_msg(context, user_id, chat_id, message_id, text, parse_mode):
    """Stores the payment-details message so we can edit it when user sends text instead of photo."""
    _client_payment_details_msg(context)[user_id] = {
        "chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode
    }

def get_client_payment_details_msg(context, user_id):
    return _client_payment_details_msg(context).get(user_id)

# =========================
# KEYBOARDS
# =========================
def start_intro_kb():
    """תפריט התחלה - מה בוט זה יכול לעשות"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("התחל הפקדה", callback_data="nav:start_deposit")],
    ])

def amounts_kb():
    rows, row = [], []
    for a in QUICK_AMOUNTS:
        row.append(InlineKeyboardButton(f"₪{a}", callback_data=f"amt:{a}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("₪1000 ומעלה", callback_data="amt:custom")])
    return InlineKeyboardMarkup(rows)

def back_home_kb(back_cb):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 חזרה", callback_data=back_cb)],
        [InlineKeyboardButton("🏠 תפריט ראשי", callback_data="nav:home")],
    ])

# כפתורי ניווט לשימוש בכל שלב (חזרה + תפריט ראשי)
def more_info_kb():
    """כפתורים להודעה 'לא הצלחנו לאמת' - שיטת תשלום אחרת, חזרה, תפריט ראשי"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("לחץ כאן לשיטת תשלום אחרת", callback_data="nav:back_method")],
        [InlineKeyboardButton("🔙 חזרה", callback_data="nav:back_method"), InlineKeyboardButton("🏠 תפריט ראשי", callback_data="nav:home")],
    ])

def client_nav_kb(back_cb="nav:home"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 חזרה", callback_data=back_cb), InlineKeyboardButton("🏠 תפריט ראשי", callback_data="nav:home")],
    ])

def methods_kb():
    # שורה 1: תשלום בביט | שורה 2: העברה בנקאית | שורה 3: חזרה + תפריט ראשי
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 תשלום בביט", callback_data="pm:bit")],
        [InlineKeyboardButton("🏦 העברה בנקאית", callback_data="pm:bank")],
        [InlineKeyboardButton("🔙 חזרה", callback_data="nav:back_site"), InlineKeyboardButton("🏠 תפריט ראשי", callback_data="nav:home")],
    ])

def banks_kb():
    rows = []
    for i in range(4):
        rows.append([
            InlineKeyboardButton(BANKS[i], callback_data=f"bank:{i}"),
            InlineKeyboardButton(BANKS[i + 4], callback_data=f"bank:{i + 4}"),
        ])
    rows.append([InlineKeyboardButton(BANK_OTHER, callback_data="bank:other")])
    rows.append([InlineKeyboardButton("🔙 חזרה", callback_data="nav:back_method"), InlineKeyboardButton("🏠 תפריט ראשי", callback_data="nav:home")])
    return InlineKeyboardMarkup(rows)

def admin_receipt_kb(rid, user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(ADM_BTN_SUCCESS, callback_data=f"ad:ok:{rid}:{user_id}")],
        [InlineKeyboardButton(ADM_BTN_MORE, callback_data=f"ad:more:{rid}:{user_id}")],
        [InlineKeyboardButton(ADM_BTN_PROBLEM, callback_data=f"ad:problem:{rid}:{user_id}")],
    ])

def admin_username_kb(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(ADM_BTN_USERNAME_OK, callback_data=f"ad:username_ok:{user_id}")],
        [InlineKeyboardButton(ADM_BTN_USERNAME_BAD, callback_data=f"ad:username_bad:{user_id}")],
    ])

def admin_payment_request_kb(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Method not available | Método no disponible", callback_data=f"ad:payment_unavailable:{user_id}")],
    ])

# =========================
# TEMPLATES
# =========================
def template_bit(details):
    return f"ביט לפה:\n{html.escape(details)}\n<b>לא לשמור את המספר, להעביר ישר למספר דרך הביט</b>\n<b>לא לרשום כלום בסיבת ההעברה</b>\n\nשלח עכשיו צילום מסך של האסמכתא (תמונה בלבד)."

def template_bank(details):
    """Format bank details for client - each field on separate line."""
    raw = details.strip().replace("\r\n", "\n").replace("\r", "\n")
    raw = raw.replace("מס' חשבון", "מס חשבון").replace("מס'חשבון", "מס חשבון")
    raw = re.sub(r"\s*סניף\s*:\s*", "\nסניף ", raw)
    raw = re.sub(r"\s*מס\s+חשבון\s*:\s*", "\nמס חשבון ", raw)
    raw = re.sub(r"\s*מוטב\s*:\s*", "\nמוטב ", raw)
    lines = [ln.strip() for ln in raw.split("\n") if ln.strip()]
    formatted = "\n".join(lines)
    return f"פרטי העברה בנקאית:\n\n{html.escape(formatted)}\n\nשלח עכשיו צילום מסך של האסמכתא (תמונה בלבד)."

_last_payment_send = {}

def admin_unlock_kb(user_id):
    """כפתור לשחרור חסימה מוקדמת (לאחר Problem)"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔓 שחרר חסימה | Unlock", callback_data=f"ad:unlock:{user_id}")],
    ])

def admin_revoke_payment_kb(user_id, message_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚨Revoke payment details | Anular y devolver al cliente🚨", callback_data=f"ad:revoke_payment:{user_id}:{message_id}")],
    ])

async def send_payment_to_user(ctx, user_id, method, details):
    key = (user_id, method)
    now = time.monotonic()
    if key in _last_payment_send and (now - _last_payment_send[key]) < 3:
        return
    _last_payment_send[key] = now

    if method == "bit":
        msg = template_bit(details)
    elif method == "bit_free":
        msg = details
    else:
        msg = template_bank(details)
    nav_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 חזרה", callback_data="nav:back_method"), InlineKeyboardButton("🏠 תפריט ראשי", callback_data="nav:home")],
    ])
    parse_mode = None if method == "bit_free" else ParseMode.HTML
    await clear_client_menu(ctx, user_id)
    sent = await ctx.bot.send_message(chat_id=user_id, text=msg, parse_mode=parse_mode, reply_markup=nav_kb)
    save_client_menu(ctx, user_id, sent.chat_id, sent.message_id)
    save_client_payment_details_msg(ctx, user_id, sent.chat_id, sent.message_id, msg, parse_mode)
    set_client_state_override(ctx, user_id, S_WAIT_RECEIPT, receipt_sent=False)
    await _remove_admin_payment_request_buttons(ctx, user_id)
    sent_admin = await ctx.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"{ADM_MSG_DELIVERED} (user_id: {user_id}).",
        reply_markup=admin_revoke_payment_kb(user_id, sent.message_id)
    )
    save_admin_revoke_msg(ctx, user_id, ADMIN_CHAT_ID, sent_admin.message_id)
    _clear_receipt_completed(ctx, user_id)  # התחלנו המתנה חדשה לאסמכתא
    _schedule_receipt_reminder(ctx, user_id)

def _schedule_receipt_reminder(ctx, user_id):
    """מתזמן תזכורת ללקוח – נשלחת רק אם העובד עדיין מחכה לאסמכתא."""
    jq = getattr(ctx, "job_queue", None) if ctx else None
    if jq:
        schedule_reminder(jq, ctx, user_id, user_id)
        return
    async def _reminder_task():
        await asyncio.sleep(60 * REMINDER_MINUTES)
        try:
            if not is_locked(user_id) and _is_receipt_reminder_relevant(ctx, user_id):
                await ctx.bot.send_message(chat_id=user_id, text=REMINDER_TEXT)
        except Exception as e:
            logger.warning("reminder fallback: %s", e)
    try:
        asyncio.create_task(_reminder_task())
    except Exception as e:
        logger.warning("could not schedule reminder: %s", e)

def schedule_reminder(jq, ctx, user_id, chat_id):
    if not jq:
        return
    cancel_jobs(jq, f"rem_{user_id}")

    async def cb(job_ctx):
        if not is_locked(user_id) and _is_receipt_reminder_relevant(job_ctx, user_id):
            await job_ctx.bot.send_message(chat_id=chat_id, text=REMINDER_TEXT)

    jq.run_once(cb, when=timedelta(minutes=REMINDER_MINUTES), name=f"rem_{user_id}")

def schedule_return_menu(jq, user_id, chat_id):
    if not jq:
        return
    cancel_jobs(jq, f"ret_{user_id}")

    async def cb(ctx):
        if not is_locked(user_id):
            await clear_client_menu(ctx, user_id)
            sent = await ctx.bot.send_message(chat_id=chat_id, text=WELCOME_TEXT, reply_markup=amounts_kb())
            save_client_menu(ctx, user_id, sent.chat_id, sent.message_id)
            set_client_state_override(ctx, user_id, S_AMOUNT)

    jq.run_once(cb, when=timedelta(seconds=RETURN_TO_MENU_SECONDS), name=f"ret_{user_id}")

# =========================
# CLIENT: START / SCREENS
# =========================
async def show_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    set_locked(uid, False)
    reset_flow(context)
    context.user_data["user_id"] = uid
    clear_awaiting_receipt(uid)
    clear_client_pending(uid)
    clear_awaiting_username(uid)
    _client_payment_details_msg(context).pop(uid, None)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(WELCOME_TEXT, reply_markup=amounts_kb())
        save_client_menu(context, uid, update.effective_chat.id, update.callback_query.message.message_id)
    else:
        await clear_client_menu(context, uid)
        sent = await update.message.reply_text(WELCOME_TEXT, reply_markup=amounts_kb())
        save_client_menu(context, uid, sent.chat_id, sent.message_id)

async def ask_site_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_state(context, S_SITE_USER)
    uid = update.effective_user.id
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(SITE_USER_TEXT, reply_markup=back_home_kb("nav:back_amount"))
        save_client_menu(context, uid, update.effective_chat.id, update.callback_query.message.message_id)
    else:
        await clear_client_menu(context, uid)
        sent = await update.message.reply_text(SITE_USER_TEXT, reply_markup=back_home_kb("nav:back_amount"))
        save_client_menu(context, uid, sent.chat_id, sent.message_id)

async def ask_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_state(context, S_METHOD)
    uid = update.effective_user.id
    _client_payment_details_msg(context).pop(uid, None)
    txt = METHOD_SELECT_TEXT
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(txt, reply_markup=methods_kb())
        save_client_menu(context, uid, update.effective_chat.id, update.callback_query.message.message_id)
    else:
        await clear_client_menu(context, uid)
        sent = await update.message.reply_text(txt, reply_markup=methods_kb())
        save_client_menu(context, uid, sent.chat_id, sent.message_id)

# =========================
# CLIENT: COMMANDS
# =========================
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    _apply_client_state_override(uid, context)
    state = get_state(context)
    if state in EMPLOYEE_PENDING_STATES:
        msg, parse = get_waiting_msg_for_employee_pending(state)
        kw = {"parse_mode": parse} if parse else {}
        return await update.message.reply_text(msg, **kw)
=======
def schedule_receipt_reminder(context: ContextTypes.DEFAULT_TYPE, user_chat_id: int, user_id: int):
    # cancel existing reminder for that user
    cancel_jobs_by_name(context.job_queue, f"rem_{user_id}")

    async def reminder_cb(ctx: ContextTypes.DEFAULT_TYPE):
        if is_locked(user_id):
            return
        await ctx.bot.send_message(chat_id=user_chat_id, text=REMINDER_TEXT)

    context.job_queue.run_once(
        reminder_cb,
        when=timedelta(minutes=REMINDER_MINUTES),
        name=f"rem_{user_id}",
    )

def schedule_return_to_menu(context: ContextTypes.DEFAULT_TYPE, user_chat_id: int, user_id: int):
    cancel_jobs_by_name(context.job_queue, f"ret_{user_id}")

    async def return_cb(ctx: ContextTypes.DEFAULT_TYPE):
        # אם המשתמש נעול בזמן הזה – לא מציג תפריט
        if is_locked(user_id):
            return
        await ctx.bot.send_message(chat_id=user_chat_id, text=WELCOME_TEXT, reply_markup=amounts_kb())

    context.job_queue.run_once(
        return_cb,
        when=timedelta(seconds=RETURN_TO_MENU_SECONDS),
        name=f"ret_{user_id}",
    )

# =========================
# PAYMENT TEMPLATES (HTML)
# =========================
def template_bit(details: str) -> str:
    d = html.escape(details)
    return (
        "ביט לפה:\n"
        f"{d}\n"
        "<b>לא לשמור את המספר, להעביר ישר למספר דרך הביט</b>\n"
        "<b>לא לרשום כלום בסיבת ההעברה</b>\n"
        "ולשלוח צילום מסך בבקשה"
    )

def template_paybox(details: str) -> str:
    d = html.escape(details)
    return (
        "פייבוקס לפה:\n"
        f"{d}\n"
        "<b>לא לשמור את המספר, להעביר ישר למספר דרך הפייבוקס</b>\n"
        "<b>לא לרשום כלום בסיבת ההעברה</b>\n"
        "ולשלוח צילום מסך בבקשה"
    )

def template_bank(details: str) -> str:
    d = html.escape(details)
    return (
        f"{d}\n"
        "נא לשלוח צילום של האסמכתא בצורה ברורה ומלאה"
    )

async def send_payment_details_and_request_photo(context: ContextTypes.DEFAULT_TYPE, user_id: int, method: str, details: str):
    if method == "bit":
        msg = template_bit(details)
    elif method == "paybox":
        msg = template_paybox(details)
    else:
        msg = template_bank(details)

    await context.bot.send_message(chat_id=user_id, text=msg, parse_mode=ParseMode.HTML)
    await context.bot.send_message(chat_id=user_id, text="שלח עכשיו <b>צילום מסך</b> של האסמכתא (תמונה בלבד).", parse_mode=ParseMode.HTML)

    # תזכורת אוטומטית אם לא שולח אסמכתא אחרי 7 דקות
    schedule_receipt_reminder(context, user_id, user_id)

# =========================
# USER SCREENS
# =========================
async def show_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if is_locked(user_id):
        set_state(context, S_LOCKED)
        txt = "הפנייה שלך נמצאת בבדיקה מול נציג. בשלב זה אי אפשר להמשיך בבוט עד שתקבל עדכון."
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(txt)
        else:
            await update.message.reply_text(txt)
        return

    reset_flow(context)
    context.user_data["user_id"] = user_id

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(WELCOME_TEXT, reply_markup=amounts_kb())
    else:
        await update.message.reply_text(WELCOME_TEXT, reply_markup=amounts_kb())

async def ask_site_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_state(context, S_SITE_USER)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(SITE_USER_TEXT, reply_markup=back_home_kb("nav:back_to_amount"), parse_mode="Markdown")
    else:
        await update.message.reply_text(SITE_USER_TEXT, reply_markup=back_home_kb("nav:back_to_amount"), parse_mode="Markdown")

async def ask_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_state(context, S_METHOD)
    txt = "בחר שיטת תשלום:"
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(txt, reply_markup=methods_kb())
    else:
        await update.message.reply_text(txt, reply_markup=methods_kb())

# =========================
# USER COMMANDS
# =========================
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
>>>>>>> Stashed changes
    await show_start(update, context)

async def cmd_myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"user_id: {update.effective_user.id}\nchat_id: {update.effective_chat.id}")

# =========================
<<<<<<< Updated upstream
# CLIENT: CALLBACKS (inline buttons)
# =========================
async def on_client_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = update.effective_user.id
    data = q.data
    if data.startswith("ad:"):
        await on_admin_callback(update, context)
        return
    _apply_client_state_override(uid, context)
    state = get_state(context)
    if is_locked(uid):
        await q.answer()
        if get_lock_reason(uid) == "problem":
            return await q.edit_message_text(problem_text_for_client(uid))
        return await q.edit_message_text("הפנייה שלך נמצאת בבדיקה מול נציג. בשלב זה אי אפשר להמשיך בבוט עד שתקבל עדכון.")
    is_client_nav = data in ("nav:home", "nav:back_amount", "nav:back_site", "nav:back_method")
    is_client_choice = data.startswith("amt:") or data.startswith("pm:") or data.startswith("bank:")
    # Allow Back/Main Menu from receipt stage so the client is not stuck
    allow_nav_from_receipt = state in (S_WAIT_RECEIPT, S_WAIT_RECEIPT_MORE) and is_client_nav
    if state in EMPLOYEE_PENDING_STATES and (is_client_nav or is_client_choice) and not allow_nav_from_receipt:
        msg, parse = get_waiting_msg_for_employee_pending(state)
        if msg:
            await q.answer()
            kw = {"parse_mode": parse} if parse else {}
            try:
                await q.edit_message_text(msg, **kw)
            except Exception:
                await context.bot.send_message(chat_id=uid, text=msg, **kw)
        return

    if data == "nav:home":
        return await show_start(update, context)
    if data == "nav:start_deposit":
        await q.answer()
        set_state(context, S_AMOUNT)
        await q.edit_message_text(WELCOME_TEXT, reply_markup=amounts_kb())
        save_client_menu(context, uid, update.effective_chat.id, q.message.message_id)
        return
    if data == "nav:back_amount":
        await q.answer()
        set_state(context, S_AMOUNT)
        await q.edit_message_text(WELCOME_TEXT, reply_markup=amounts_kb())
        save_client_menu(context, uid, update.effective_chat.id, q.message.message_id)
        return

    if data == "nav:back_site":
        await q.answer()
        return await ask_site_user(update, context)
    if data == "nav:back_method":
        await q.answer()
        set_state(context, S_METHOD)
        return await ask_method(update, context)

=======
# ADMIN COMMANDS (optional shortcuts)
# =========================
async def cmd_unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("שימוש: /unlock <user_id>")
        return
    uid = int(context.args[0])
    set_locked(uid, False)
    await update.message.reply_text(f"🔓 שוחרר נעילה למשתמש {uid}")
    try:
        await context.bot.send_message(chat_id=uid, text="🔓 שוחררת. אפשר להתחיל הפקדה מחדש עם /start")
    except Exception:
        pass

async def cmd_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("שימוש: /block <user_id>")
        return
    uid = int(context.args[0])
    set_locked(uid, True)
    await update.message.reply_text(f"🚫 המשתמש {uid} ננעל/נחסם.")

async def cmd_bit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if len(context.args) < 2 or not context.args[0].isdigit():
        await update.message.reply_text("שימוש: /bit <user_id> <מספר/טקסט ביט>")
        return
    uid = int(context.args[0])
    details = " ".join(context.args[1:]).strip()
    await send_payment_details_and_request_photo(context, uid, "bit", details)
    await update.message.reply_text("✅ נשלחו פרטי Bit ללקוח")

async def cmd_paybox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if len(context.args) < 2 or not context.args[0].isdigit():
        await update.message.reply_text("שימוש: /paybox <user_id> <מספר/טקסט פייבוקס>")
        return
    uid = int(context.args[0])
    details = " ".join(context.args[1:]).strip()
    await send_payment_details_and_request_photo(context, uid, "paybox", details)
    await update.message.reply_text("✅ נשלחו פרטי PayBox ללקוח")

async def cmd_bank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if len(context.args) < 2 or not context.args[0].isdigit():
        await update.message.reply_text("שימוש: /bank <user_id> <פרטי העברה בנקאית...>")
        return
    uid = int(context.args[0])
    details = " ".join(context.args[1:]).strip()
    await send_payment_details_and_request_photo(context, uid, "bank", details)
    await update.message.reply_text("✅ נשלחו פרטי העברה בנקאית ללקוח")

async def cmd_cancelpay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # admin-only: clears pending guidance
    if not is_admin(update.effective_user.id):
        return
    clear_admin_pending(update.effective_user.id)
    await update.message.reply_text("בוטל מצב שליחת פרטי תשלום (Pending).")

# =========================
# CALLBACKS
# =========================
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    user_id = update.effective_user.id

    # if user is locked, stop user flow (admin callbacks still allowed)
    if is_locked(user_id) and not (data.startswith("ad:") or data.startswith("adp:")):
        await q.answer()
        return await q.edit_message_text("הפנייה שלך נמצאת בבדיקה מול נציג. בשלב זה אי אפשר להמשיך בבוט עד שתקבל עדכון.")

    # NAV
    if data == "nav:home":
        return await show_start(update, context)

    if data == "nav:back_to_amount":
        await q.answer()
        set_state(context, S_AMOUNT)
        return await q.edit_message_text(WELCOME_TEXT, reply_markup=amounts_kb())

    if data == "nav:back_to_siteuser":
        await q.answer()
        return await ask_site_user(update, context)

    # AMOUNT
>>>>>>> Stashed changes
    if data.startswith("amt:"):
        await q.answer()
        val = data.split(":", 1)[1]
        if val == "custom":
            set_state(context, S_CUSTOM_AMOUNT)
<<<<<<< Updated upstream
            await q.edit_message_text(
                f"כתוב סכום (מספרים בלבד). מינימום {CUSTOM_MIN_AMOUNT} ומעלה:",
                reply_markup=back_home_kb("nav:back_amount")
            )
            save_client_menu(context, uid, update.effective_chat.id, q.message.message_id)
            return
=======
            return await q.edit_message_text(
                f"כתוב סכום (מספרים בלבד). מינימום {CUSTOM_MIN_AMOUNT} ומעלה:",
                reply_markup=back_home_kb("nav:back_to_amount")
            )
>>>>>>> Stashed changes
        amount = int(val)
        context.user_data["amount"] = amount
        return await ask_site_user(update, context)

<<<<<<< Updated upstream
=======
    # PAYMENT METHOD: user chooses -> wait + admin request
>>>>>>> Stashed changes
    if data.startswith("pm:"):
        await q.answer()
        method_key = data.split(":", 1)[1]
        context.user_data["method"] = method_key
<<<<<<< Updated upstream
        amount = context.user_data.get("amount")
        site_user = context.user_data.get("site_user", "")
        if method_key == "bank":
            set_state(context, S_BANK_SELECTION)
            await q.edit_message_text(BANK_SELECT_TEXT, reply_markup=banks_kb())
            save_client_menu(context, uid, update.effective_chat.id, q.message.message_id)
            return
        set_state(context, S_WAIT_PAYMENT_DETAILS)
        if amount and site_user:
            set_client_pending(uid, amount, site_user, method_key)
        await q.edit_message_text(WAIT_FOR_DETAILS_TEXT, reply_markup=None)
        amount = amount or context.user_data.get("amount")
        site_user = site_user or context.user_data.get("site_user", "")
        pm_label = "Bit"
        username = update.effective_user.username or ""
        example_bit = f"/bit {uid} 05X-XXXXXXX"
        example_bit_free = f"/bit_free {uid}"
        admin_text = (
            f"{ADM_PAYMENT_REQUEST}\n\n"
            f"Amount / Monto: <b>{amount}</b>\n"
            f"User / Usuario: <b>{html.escape(str(site_user))}</b>\n"
            f"Method / Método: <b>{html.escape(pm_label)}</b>\n"
            f"Telegram: @{username} (user_id: {uid})\n\n"
            f"{example_bit}\n{example_bit_free}"
        )
        sent = await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_text,
            parse_mode=ParseMode.HTML,
            reply_markup=admin_payment_request_kb(uid)
        )
        save_admin_payment_request_msg(context, uid, ADMIN_CHAT_ID, sent.message_id)
        return

    if data.startswith("bank:"):
        await q.answer()
        bank_val = data.split(":", 1)[1]
        if bank_val == "other":
            set_state(context, S_BANK_OTHER)
            await q.edit_message_text(
                BANK_OTHER_PROMPT_TEXT,
                reply_markup=back_home_kb("nav:back_method")
            )
            save_client_menu(context, uid, update.effective_chat.id, q.message.message_id)
            return
        try:
            bank_idx = int(bank_val)
            bank_name = BANKS[bank_idx] if 0 <= bank_idx < len(BANKS) else bank_val
        except (ValueError, IndexError):
            bank_name = bank_val
        context.user_data["bank"] = bank_name
        method_key = "bank"
        amount = context.user_data.get("amount")
        site_user = context.user_data.get("site_user", "")
        set_state(context, S_WAIT_PAYMENT_DETAILS)
        if amount and site_user:
            set_client_pending(uid, amount, site_user, method_key, bank_name)
        await q.edit_message_text(WAIT_FOR_DETAILS_TEXT, reply_markup=None)
        pm_label = "Bank transfer"
        username = update.effective_user.username or ""
        example = f"/bank {uid}"
        admin_text = (
            f"{ADM_PAYMENT_REQUEST}\n\n"
            f"Amount / Monto: <b>{amount}</b>\n"
            f"User / Usuario: <b>{html.escape(str(site_user))}</b>\n"
            f"Method / Método: <b>{html.escape(pm_label)}</b>\n"
            f"Bank / Banco: <b>{html.escape(bank_for_admin(bank_name))}</b>\n"
            f"Telegram: @{username} (user_id: {uid})\n\n"
            f"{example}"
        )
        sent = await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_text,
            parse_mode=ParseMode.HTML,
            reply_markup=admin_payment_request_kb(uid)
        )
        save_admin_payment_request_msg(context, uid, ADMIN_CHAT_ID, sent.message_id)
        return

# =========================
# CLIENT: TEXT (private only)
# =========================
async def on_client_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    _apply_client_state_override(uid, context)
    txt = (update.message.text or "").strip()
    state = get_state(context)
    is_start_trigger = (
        txt.lower() in ("start", "התחל", "/start", "התחלה")
        or (len(txt) <= 20 and ("start" in txt.lower() or "התחל" in txt))
        or txt.lower() in ("אני רוצה עוד", "הפקדה נוספת", "עוד הפקדה", "עוד")
    )
    if is_start_trigger:
        if state in EMPLOYEE_PENDING_STATES:
            msg, parse = get_waiting_msg_for_employee_pending(state)
            kw = {"parse_mode": parse} if parse else {}
            return await update.message.reply_text(msg, **kw)
        return await show_start(update, context)
    if is_locked(uid):
        if get_lock_reason(uid) == "problem":
            return await update.message.reply_text(problem_text_for_client(uid))
        return await update.message.reply_text("הפנייה שלך נמצאת בבדיקה מול נציג. בשלב זה אי אפשר להמשיך בבוט עד שתקבל עדכון.")

    state = get_state(context)
    if state == S_AMOUNT:
        await clear_client_menu(context, uid)
        sent = await update.message.reply_text(AMOUNT_SELECT_ONLY_TEXT, reply_markup=amounts_kb())
        save_client_menu(context, uid, sent.chat_id, sent.message_id)
        return
    if state == S_CUSTOM_AMOUNT:
        if not txt.isdigit():
            await clear_client_menu(context, uid)
            sent = await update.message.reply_text("אנא שלח מספרים בלבד.", reply_markup=back_home_kb("nav:back_amount"))
            save_client_menu(context, uid, sent.chat_id, sent.message_id)
            return
        amount = int(txt)
        if amount < CUSTOM_MIN_AMOUNT:
            await clear_client_menu(context, uid)
            sent = await update.message.reply_text(f"סכום חייב להיות מינימום {CUSTOM_MIN_AMOUNT} ומעלה.", reply_markup=back_home_kb("nav:back_amount"))
            save_client_menu(context, uid, sent.chat_id, sent.message_id)
            return
        context.user_data["amount"] = amount
        return await ask_site_user(update, context)
    if state == S_BANK_OTHER:
        bank_name = txt
        if len(bank_name) < 2:
            await clear_client_menu(context, uid)
            sent = await update.message.reply_text("אנא הקלד שם בנק תקין.", reply_markup=back_home_kb("nav:back_method"))
            save_client_menu(context, uid, sent.chat_id, sent.message_id)
            return
        context.user_data["bank"] = bank_name
        context.user_data["method"] = "bank"
        amount = context.user_data.get("amount")
        site_user = context.user_data.get("site_user", "")
        set_state(context, S_WAIT_PAYMENT_DETAILS)
        if amount and site_user:
            set_client_pending(uid, amount, site_user, "bank", bank_name)
        await clear_client_menu(context, uid)
        await update.message.reply_text(WAIT_FOR_DETAILS_TEXT)
        pm_label = "Bank transfer"
        username = update.effective_user.username or ""
        example = f"/bank {uid}"
        admin_text = (
            f"{ADM_PAYMENT_REQUEST}\n\n"
            f"Amount / Monto: <b>{amount}</b>\n"
            f"User / Usuario: <b>{html.escape(str(site_user))}</b>\n"
            f"Method / Método: <b>{html.escape(pm_label)}</b>\n"
            f"Bank / Banco: <b>{html.escape(bank_for_admin(bank_name))}</b>\n"
            f"Telegram: @{username} (user_id: {uid})\n\n"
            f"{example}"
        )
        sent = await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_text,
            parse_mode=ParseMode.HTML,
            reply_markup=admin_payment_request_kb(uid)
        )
        save_admin_payment_request_msg(context, uid, ADMIN_CHAT_ID, sent.message_id)
        return
    if state == S_SITE_USER:
        if len(txt) < 2:
            await clear_client_menu(context, uid)
            sent = await update.message.reply_text("שם משתמש קצר מדי. נסה שוב.", reply_markup=back_home_kb("nav:back_amount"))
            save_client_menu(context, uid, sent.chat_id, sent.message_id)
            return
        context.user_data["site_user"] = txt
        amount = context.user_data.get("amount")
        set_state(context, S_AWAIT_USERNAME_VALIDATION)
        set_awaiting_username(uid, txt, amount or 0)
        await clear_client_menu(context, uid)
        await update.message.reply_text(AWAIT_USERNAME_TEXT)
        username = update.effective_user.username or ""
        admin_text = (
            f"{ADM_USERNAME_CHECK}\n\n"
            f"Amount / Monto: <b>{amount if amount is not None else 0}</b>\n"
            f"User / Usuario: <b>{html.escape(txt)}</b>\n"
            f"Telegram: @{html.escape(username)} (user_id: {uid})"
        )
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=admin_text,
                parse_mode=ParseMode.HTML,
                reply_markup=admin_username_kb(uid)
            )
        except Exception as e:
            err_msg = str(e).strip() or type(e).__name__
            logger.exception("Failed to send username check to admin: %s", e)
            logger.error("ADMIN_CHAT_ID=%s | Telegram error: %s", ADMIN_CHAT_ID, err_msg)
            set_state(context, S_SITE_USER)
            await update.message.reply_text(
                "כרגע לא ניתן לשלוח את הבקשה לנציג. נסה שוב בעוד רגע או לחץ /start.",
                reply_markup=back_home_kb("nav:back_amount")
            )
        return
    if state == S_BANK_SELECTION:
        await clear_client_menu(context, uid)
        sent = await update.message.reply_text("אנא בחר בנק מהרשימה.", reply_markup=banks_kb())
        save_client_menu(context, uid, sent.chat_id, sent.message_id)
        return
    if state == S_METHOD:
        await clear_client_menu(context, uid)
        sent = await update.message.reply_text(METHOD_SELECT_TEXT, reply_markup=methods_kb())
        save_client_menu(context, uid, sent.chat_id, sent.message_id)
        return
    if state == S_AWAIT_USERNAME_VALIDATION:
        return await update.message.reply_text("אנא המתן, המערכת בודקת את החשבון שלך.")
    if state == S_WAIT_PAYMENT_DETAILS:
        return await update.message.reply_text(WAIT_FOR_DETAILS_TEXT)
    if state in (S_WAIT_RECEIPT, S_WAIT_RECEIPT_MORE):
        if context.user_data.get("receipt_sent"):
            if state == S_WAIT_RECEIPT_MORE:
                await clear_client_menu(context, uid)
                sent = await update.message.reply_text(MORE_INFO_TEXT, reply_markup=more_info_kb())
                save_client_menu(context, uid, sent.chat_id, sent.message_id)
                return
            return await update.message.reply_text(RECEIPT_CHECKING_TEXT)
        await update.message.reply_text(RECEIPT_ONLY_PHOTO_TEXT, parse_mode="Markdown")
        stored = get_client_payment_details_msg(context, uid)
        nav_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 חזרה", callback_data="nav:back_method"), InlineKeyboardButton("🏠 תפריט ראשי", callback_data="nav:home")],
        ])
        if stored:
            try:
                await clear_client_menu(context, uid)
                kw = {"parse_mode": stored["parse_mode"]} if stored["parse_mode"] else {}
                sent = await context.bot.send_message(
                    chat_id=uid,
                    text=stored["text"],
                    reply_markup=nav_kb,
                    **kw
                )
                save_client_menu(context, uid, sent.chat_id, sent.message_id)
                save_client_payment_details_msg(context, uid, sent.chat_id, sent.message_id, stored["text"], stored["parse_mode"])
            except Exception as e:
                logger.warning("resend payment details: %s", e)
        return
    await clear_client_menu(context, uid)
    sent = await update.message.reply_text("כדי להתחיל הפקדה לחץ /start", reply_markup=client_nav_kb())
    save_client_menu(context, uid, sent.chat_id, sent.message_id)
    return

# =========================
# CLIENT: PHOTO / DOCUMENT IMAGE (receipt)
# =========================
async def on_client_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        return await _on_client_photo_impl(update, context)
    except Exception as e:
        logger.exception("on_client_photo error: %s", e)
        try:
            uid = update.effective_user.id
            await clear_client_menu(context, uid)
            sent = await update.message.reply_text("אירעה שגיאה. נסה שוב או לחץ /start להתחלה מחדש.", reply_markup=client_nav_kb())
            save_client_menu(context, uid, sent.chat_id, sent.message_id)
        except Exception:
            pass
        try:
            uid = update.effective_user.id
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"{ADM_ERROR} processing receipt (user_id: {uid}): {e} | Error al procesar comprobante: {e}")
        except Exception:
            pass

async def _on_client_photo_impl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    _apply_client_state_override(uid, context)
    if is_locked(uid):
        if get_lock_reason(uid) == "problem":
            return await update.message.reply_text(problem_text_for_client(uid))
        return await update.message.reply_text("הפנייה שלך נמצאת בבדיקה מול נציג. בשלב זה אי אפשר להמשיך בבוט עד שתקבל עדכון.")

    # נתיב עדיפות: awaiting_receipt (אסמכתא שנייה)
    rid_pending = get_awaiting_receipt(uid)
    if rid_pending:
        req = get_request_by_rid(rid_pending)
        if req and req.get("amount") is not None and req.get("method"):
            if update.message.photo:
                file_id, is_photo = update.message.photo[-1].file_id, True
            elif update.message.document:
                file_id, is_photo = update.message.document.file_id, False
            else:
                return await update.message.reply_text(RECEIPT_ONLY_PHOTO_TEXT, parse_mode="Markdown")
            await update.message.reply_text(AFTER_RECEIPT_TEXT)
            pm_label = {"bit": "Bit", "bank": "Bank transfer"}.get(req["method"], req["method"])
            bank = context.user_data.get("bank", "") or (get_client_pending(uid) or {}).get("bank", "")
            username = update.effective_user.username or ""
            ticket = (
                f"{ADM_RECEIPT_UPDATED}\n\n"
                f"Amount / Monto: <b>{req['amount']}</b>\n"
                f"User / Usuario: <b>{html.escape(req.get('site_user', '') or '')}</b>\n"
                f"Method / Método: <b>{html.escape(pm_label)}</b>\n"
                + (f"Bank / Banco: <b>{html.escape(bank_for_admin(bank))}</b>\n" if req.get("method") == "bank" and bank else "")
                + f"Telegram: @{username} (user_id: {uid})\n"
                f"Time / Hora: {now_utc()} UTC"
            )
            try:
                if is_photo:
                    await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=ticket, parse_mode=ParseMode.HTML, reply_markup=admin_receipt_kb(rid_pending, uid))
                else:
                    await context.bot.send_document(chat_id=ADMIN_CHAT_ID, document=file_id, caption=ticket, parse_mode=ParseMode.HTML, reply_markup=admin_receipt_kb(rid_pending, uid))
            except Exception as e:
                logger.warning(f"send_photo/document failed: {e}")
                await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"{ADM_CANT_ATTACH}.\n{ticket}", parse_mode=ParseMode.HTML, reply_markup=admin_receipt_kb(rid_pending, uid))
            clear_awaiting_receipt(uid)
            clear_client_pending(uid)
            set_state(context, S_WAIT_RECEIPT)
            context.user_data["receipt_sent"] = True
            update_request_status(rid_pending, "receipt_updated")
            await clear_client_menu(context, uid)
            return

    state = get_state(context)
    amount = context.user_data.get("amount")
    site_user = context.user_data.get("site_user", "")
    method = context.user_data.get("method")

    if state not in (S_WAIT_PAYMENT_DETAILS, S_WAIT_RECEIPT, S_WAIT_RECEIPT_MORE) or not amount or not method:
        if rid_pending:
            req = get_request_by_rid(rid_pending)
            if req:
                amount, site_user, method = req.get("amount"), req.get("site_user", ""), req.get("method")
                context.user_data.update({"amount": amount, "site_user": site_user, "method": method, "request_id": rid_pending})
                set_state(context, S_WAIT_RECEIPT_MORE)
        if not amount or not method:
            pending = get_client_pending(uid)
            if pending and pending.get("amount") and pending.get("method"):
                amount = pending["amount"]
                site_user = pending.get("site_user", "") or ""
                method = pending["method"]
                bank = pending.get("bank", "") or ""
                context.user_data.update({"amount": amount, "site_user": site_user, "method": method, "bank": bank})
                set_state(context, S_WAIT_RECEIPT)
            else:
                await clear_client_menu(context, uid)
                sent = await update.message.reply_text("כדי לבצע הפקדה, לחץ /start והמשך לפי השלבים.", reply_markup=client_nav_kb())
                save_client_menu(context, uid, sent.chat_id, sent.message_id)
                return

    if update.message.photo:
        file_id, is_photo = update.message.photo[-1].file_id, True
    elif update.message.document:
        file_id, is_photo = update.message.document.file_id, False
    else:
        return await update.message.reply_text(RECEIPT_ONLY_PHOTO_TEXT, parse_mode="Markdown")

    rid = context.user_data.get("request_id") or gen_request_id()
    if not context.user_data.get("request_id"):
        context.user_data["request_id"] = rid
        log_request(rid, uid, update.effective_user.username or "", amount, site_user, method, "receipt_sent")
    else:
        update_request_status(rid, "receipt_updated")

    await update.message.reply_text(AFTER_RECEIPT_TEXT)

    pm_label = {"bit": "Bit", "bank": "Transferencia bancaria"}.get(method, method)
    bank = context.user_data.get("bank", "")
    username = update.effective_user.username or ""
    ticket = (
        f"{ADM_NEW_DEPOSIT}\n\n"
        f"Amount / Monto: <b>{amount}</b>\n"
        f"User / Usuario: <b>{html.escape(site_user)}</b>\n"
        f"Method / Método: <b>{html.escape(pm_label)}</b>\n"
        + (f"Bank / Banco: <b>{html.escape(bank_for_admin(bank))}</b>\n" if method == "bank" and bank else "")
        + f"Telegram: @{username} (user_id: {uid})\n"
        f"Time / Hora: {now_utc()} UTC"
    )

    try:
        if is_photo:
            await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=ticket, parse_mode=ParseMode.HTML, reply_markup=admin_receipt_kb(rid, uid))
        else:
            await context.bot.send_document(chat_id=ADMIN_CHAT_ID, document=file_id, caption=ticket, parse_mode=ParseMode.HTML, reply_markup=admin_receipt_kb(rid, uid))
    except Exception as e:
        logger.warning(f"send_photo/document failed: {e}")
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"{ADM_CANT_ATTACH}.\n{ticket}", parse_mode=ParseMode.HTML, reply_markup=admin_receipt_kb(rid, uid))

    clear_awaiting_receipt(uid)
    clear_client_pending(uid)
    set_state(context, S_WAIT_RECEIPT)
    context.user_data["receipt_sent"] = True
    await clear_client_menu(context, uid)

# =========================
# ADMIN: callbacks (from admin chat)
# =========================
async def on_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not is_admin(q.from_user.id):
        await q.answer("No permission | Sin permiso", show_alert=True)
        return
    data = q.data
    await q.answer()

    if data.startswith("ad:revoke_payment:"):
        parts = data.split(":")
        if len(parts) >= 4:
            uid = int(parts[2])
            msg_id = int(parts[3])
            try:
                await context.bot.delete_message(chat_id=uid, message_id=msg_id)
            except Exception as e:
                logger.warning("revoke delete_message: %s", e)
            pending = get_client_pending(uid)
            if pending:
                set_client_state_override(context, uid, S_METHOD, amount=pending.get("amount"), site_user=pending.get("site_user", ""), method=None, bank=None)
            else:
                set_client_state_override(context, uid, S_METHOD, method=None, bank=None)
            try:
                await clear_client_menu(context, uid)
                sent = await context.bot.send_message(chat_id=uid, text=METHOD_SELECT_TEXT, reply_markup=methods_kb())
                save_client_menu(context, uid, sent.chat_id, sent.message_id)
                await q.edit_message_text(text=(q.message.text or "") + "\n\n✓ Revoked. Client returned to method selection. | Anulado. Cliente devuelto a selección de método.")
            except Exception as e:
                logger.warning("revoke send to client: %s", e)
                await q.answer("Failed to send to client | No se pudo enviar al cliente", show_alert=True)
        return

    if data.startswith("ad:unlock:") or data.startswith("ad:block:"):
        uid = int(data.split(":")[2])
        try:
            await q.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        if "unlock" in data:
            set_locked(uid, False)
            set_client_state_override(context, uid, S_AMOUNT)
            try:
                await clear_client_menu(context, uid)
                sent = await context.bot.send_message(chat_id=uid, text=START_INTRO_TEXT, reply_markup=start_intro_kb())
                save_client_menu(context, uid, sent.chat_id, sent.message_id)
            except Exception:
                pass
            try:
                await context.bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"✅ הלקוח שוחרר מחסימה (user_id: {uid}) | Client unlocked"
                )
            except Exception:
                pass
        else:
            set_locked(uid, True)
        return

    if data.startswith("ad:payment_unavailable:"):
        uid = int(data.split(":")[2])
        try:
            await q.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        try:
            set_client_state_override(context, uid, S_METHOD, method=None, bank=None)
            clear_client_pending(uid)
            await clear_client_menu(context, uid)
            sent = await context.bot.send_message(
                chat_id=uid,
                text=PAYMENT_METHOD_UNAVAILABLE_TEXT,
                reply_markup=methods_kb()
            )
            save_client_menu(context, uid, sent.chat_id, sent.message_id)
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"{ADM_MSG_DELIVERED} (user_id: {uid}, method not available | método no disponible)"
            )
        except Exception as e:
            logger.warning(f"payment_unavailable reply: {e}")
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"{ADM_ERROR}: {e}")
        return

    if data.startswith("ad:username_ok:") or data.startswith("ad:username_bad:"):
        uid = int(data.split(":")[2])
        try:
            await q.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        pending = get_awaiting_username(uid)
        try:
            if "ok" in data and pending:
                set_client_state_override(context, uid, S_METHOD, site_user=pending["site_user"], amount=pending["amount"])
                await context.bot.send_message(chat_id=uid, text=USERNAME_FOUND_TEXT)
                await clear_client_menu(context, uid)
                sent = await context.bot.send_message(chat_id=uid, text=METHOD_SELECT_TEXT, reply_markup=methods_kb())
                save_client_menu(context, uid, sent.chat_id, sent.message_id)
                clear_awaiting_username(uid)
                await context.bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"{ADM_MSG_DELIVERED} (user_id: {uid})"
                )
            elif "bad" in data and pending:
                set_client_state_override(context, uid, S_SITE_USER)
                await clear_client_menu(context, uid)
                sent = await context.bot.send_message(chat_id=uid, text=USERNAME_INVALID_TEXT, reply_markup=back_home_kb("nav:back_amount"))
                save_client_menu(context, uid, sent.chat_id, sent.message_id)
                clear_awaiting_username(uid)
                await context.bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"{ADM_MSG_DELIVERED} (user_id: {uid})"
                )
        except Exception as e:
            logger.warning(f"username validation reply: {e}")
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"{ADM_ERROR}: {e}")
        return

    parts = data.split(":")
    if len(parts) < 4:
        return
    action, rid, uid = parts[1], parts[2], int(parts[3])

    async def _edit_ticket_done(text_suffix):
        try:
            if q.message.photo:
                cap = (q.message.caption or "") + text_suffix
                await q.edit_message_caption(caption=cap, reply_markup=None)
            elif q.message.document:
                cap = (q.message.caption or "") + text_suffix
                await q.edit_message_caption(caption=cap, reply_markup=None)
            else:
                txt = (q.message.text or q.message.caption or "") + text_suffix
                await q.edit_message_text(text=txt, reply_markup=None)
        except Exception as e:
            logger.warning(f"edit ticket feedback: {e}")
            try:
                await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text_suffix.strip())
            except Exception:
                pass

    if action == "ok":
        set_locked(uid, False)
        clear_awaiting_receipt(uid)
        clear_client_pending(uid)
        _mark_receipt_completed(context, uid)  # התזכורת לא תישלח – ההפקדה הושלמה
        set_client_state_override(context, uid, S_AMOUNT)
        await _remove_admin_revoke_buttons(context, uid)  # מסיר כפתור Revoke כי התשלום אושר
        jq = getattr(context, "job_queue", None) or (getattr(context.application, "job_queue", None) if context.application else None)
        cancel_jobs(jq, f"rem_{uid}")
        try:
            await clear_client_menu(context, uid)
            sent = await context.bot.send_message(
                chat_id=int(uid),
                text=SUCCESS_TEXT,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 הפקדה נוספת", callback_data="nav:home")],
                    [InlineKeyboardButton("🔙 חזרה", callback_data="nav:home"), InlineKeyboardButton("🏠 תפריט ראשי", callback_data="nav:home")],
                ])
            )
            save_client_menu(context, uid, sent.chat_id, sent.message_id)
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"{ADM_MSG_DELIVERED} (user_id: {uid})"
            )
        except Exception as e:
            logger.warning(f"send success to client {uid}: {e}")
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"{ADM_CANT_SEND} (user_id: {uid}): {e}")
        await _edit_ticket_done(f"\n\n{ADM_SUCCESS_SENT}.")
        schedule_return_menu(context.job_queue, uid, uid)
        return
    if action == "problem":
        try:
            await context.bot.send_message(chat_id=int(uid), text=problem_text_for_client(uid))
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"{ADM_MSG_DELIVERED} (user_id: {uid})",
                reply_markup=admin_unlock_kb(uid)
            )
        except Exception as e:
            logger.warning(f"send problem to client {uid}: {e}")
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"{ADM_CANT_SEND} (user_id: {uid}): {e}")
        set_locked(uid, True, lock_hours=PROBLEM_LOCK_HOURS, lock_reason="problem")
        set_awaiting_receipt(uid, rid)
        cancel_jobs(context.job_queue, f"rem_{uid}")
        await _edit_ticket_done(f"\n\n{ADM_PROBLEM_SENT}.")
        return
    if action == "more":
        set_awaiting_receipt(uid, rid)
        set_client_state_override(context, uid, S_WAIT_RECEIPT_MORE, receipt_sent=True)
        cancel_jobs(context.job_queue, f"rem_{uid}")
        try:
            await clear_client_menu(context, uid)
            sent = await context.bot.send_message(chat_id=int(uid), text=MORE_INFO_TEXT, reply_markup=more_info_kb())
            save_client_menu(context, uid, sent.chat_id, sent.message_id)
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"{ADM_MSG_DELIVERED} (user_id: {uid})"
            )
        except Exception as e:
            logger.warning(f"send more_info to client {uid}: {e}")
        await _edit_ticket_done(f"\n\n{ADM_MORE_SENT}.")
        _schedule_receipt_reminder(context, uid)

# =========================
# ADMIN: text (admin chat only) - guided payment details
# =========================
async def on_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    pending = get_admin_pending(update.effective_user.id)
    if not pending:
        return
    uid = int(pending["user_id"])
    method = pending["method"]
    details = (update.message.text or "").strip()
    if not details:
        return await update.message.reply_text("Send the text with the data. Or /cancelpay to cancel. | Envía el texto con los datos. O /cancelpay para cancelar.")
    try:
        await send_payment_to_user(context, uid, method, details)
    except Exception as e:
        await update.message.reply_text(f"{ADM_CANT_SEND}: {e}")
        return
    clear_admin_pending(update.effective_user.id)
    await update.message.reply_text(f"{ADM_MSG_DELIVERED}. Awaiting receipt. | Esperando comprobante.")

# =========================
# ADMIN: commands
# =========================
async def cmd_unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args or not str(context.args[0]).isdigit():
        await update.message.reply_text("Usage: /unlock <user_id> | Uso: /unlock <user_id>")
        return
    uid = int(context.args[0])
    set_locked(uid, False)
    try:
        await clear_client_menu(context, uid)
        set_client_state_override(context, uid, S_AMOUNT)
        await clear_client_menu(context, uid)
        sent = await context.bot.send_message(chat_id=uid, text=START_INTRO_TEXT, reply_markup=start_intro_kb())
        save_client_menu(context, uid, sent.chat_id, sent.message_id)
        await update.message.reply_text(f"✅ Unlocked {uid}. {ADM_MSG_DELIVERED} | הלקוח שוחרר מחסימה.")
    except Exception as e:
        await update.message.reply_text(f"Unlocked {uid}. {ADM_CANT_SEND}: {e} | Desbloqueado {uid}.")

async def cmd_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args or not str(context.args[0]).isdigit():
        await update.message.reply_text("Usage: /block <user_id> | Uso: /block <user_id>")
        return
    uid = int(context.args[0])
    set_locked(uid, True)
    await update.message.reply_text(f"🚫 Blocked {uid} | Bloqueado {uid}")

async def cmd_bit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if len(context.args) < 2 or not str(context.args[0]).isdigit():
        await update.message.reply_text("Usage: /bit <user_id> <number/text> | Uso: /bit <user_id> <número/texto>")
        return
    uid = int(context.args[0])
    details = " ".join(context.args[1:]).strip()
    try:
        await send_payment_to_user(context, uid, "bit", details)
    except Exception as e:
        await update.message.reply_text(f"❌ Could not send | No se pudo enviar: {e}")
        return
    await update.message.reply_text(f"{ADM_MSG_DELIVERED}.")

async def cmd_bit_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    text = (update.message.text or "").strip()
    parts = text.split(maxsplit=2)
    if len(parts) < 2 or not parts[1].isdigit():
        await update.message.reply_text("Usage: /bit_free <user_id>\nAdd the full Bit message after the command. | Uso: /bit_free <user_id>\nAñade el mensaje completo después del comando.")
        return
    uid = int(parts[1])
    details = (parts[2].strip() if len(parts) >= 3 else "")
    if not details:
        await update.message.reply_text("Usage: /bit_free <user_id>\nAdd the full message. | Uso: /bit_free <user_id>\nAñade el mensaje completo.")
        return
    try:
        await send_payment_to_user(context, uid, "bit_free", details)
    except Exception as e:
        await update.message.reply_text(f"❌ Could not send | No se pudo enviar: {e}")
        return
    await update.message.reply_text(f"{ADM_MSG_DELIVERED}.")

async def cmd_bank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    text = (update.message.text or "").strip()
    parts = text.split(maxsplit=2)
    if len(parts) < 2 or not parts[1].isdigit():
        await update.message.reply_text("Usage: /bank <user_id>\nAdd bank details (each on new line). | Uso: /bank <user_id>\nAñade datos bancarios (cada uno en nueva línea).")
        return
    uid = int(parts[1])
    details = (parts[2].strip() if len(parts) >= 3 else "")
    if not details:
        await update.message.reply_text("Usage: /bank <user_id>\nAdd bank details. | Uso: /bank <user_id>\nAñade los datos bancarios.")
        return
    try:
        await send_payment_to_user(context, uid, "bank", details)
    except Exception as e:
        await update.message.reply_text(f"❌ Could not send | No se pudo enviar: {e}")
        return
    await update.message.reply_text(f"{ADM_MSG_DELIVERED}.")

async def cmd_cancelpay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    clear_admin_pending(update.effective_user.id)
    await update.message.reply_text("Payment send mode cancelled. | Modo de envío de pago cancelado.")
=======
        set_state(context, S_WAIT_PAYMENT_DETAILS)

        # user waiting message
        await q.edit_message_text(
            WAIT_FOR_DETAILS_TEXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 תפריט ראשי", callback_data="nav:home")],
                [InlineKeyboardButton("🔙 חזרה", callback_data="nav:back_to_siteuser")],
            ])
        )

        # admin request message with guidance button
        amount = context.user_data.get("amount")
        site_user = context.user_data.get("site_user")
        pm_label = dict(PAYMENT_METHODS).get(method_key, method_key)
        username = update.effective_user.username or ""

        example = ""
        if method_key == "bit":
            example = f"או פקודה מהירה:\n/bit {user_id} 05X-XXXXXXX"
        elif method_key == "paybox":
            example = f"או פקודה מהירה:\n/paybox {user_id} 05X-XXXXXXX"
        else:
            example = f"או פקודה מהירה:\n/bank {user_id} בנק ___ סניף ___ חשבון ___ שם ___"

        admin_text = (
            "🧾 בקשת פרטי תשלום (לפני אסמכתא)\n\n"
            f"סכום: {amount}\n"
            f"משתמש באתר: {site_user}\n"
            f"שיטה שנבחרה: {pm_label}\n"
            f"טלגרם: @{username} (user_id: {user_id})\n\n"
            "לחץ על הכפתור כדי לשלוח פרטי תשלום בצורה נוחה (ואז שלח רק את המספר/פרטים בהודעה הבאה).\n\n"
            f"{example}\n"
        )

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_text,
            reply_markup=admin_payment_details_kb(user_id, method_key)
        )
        return

    # ADMIN GUIDED PAYMENT BUTTON
    # adp:<method>:<user_id>
    if data.startswith("adp:"):
        if not is_admin(q.from_user.id):
            await q.answer("אין הרשאה", show_alert=True)
            return
        _, method, uid = data.split(":")
        uid = int(uid)

        # store pending for this admin
        set_admin_pending(q.from_user.id, uid, method)

        method_name = {"bit": "Bit", "paybox": "PayBox", "bank": "העברה בנקאית"}.get(method, method)
        hint = (
            f"✅ מצב שליחה הופעל ({method_name}).\n"
            f"שלח עכשיו בהודעה הבאה *רק* את הפרט המשתנה:\n"
            f"- Bit/PayBox: מספר/שם\n"
            f"- בנק: כל פרטי החשבון\n\n"
            f"ברגע שתשלח — הבוט ישלח ללקוח תבנית מוכנה ויבקש צילום אסמכתא.\n"
            f"לביטול מצב: /cancelpay"
        )

        await q.answer()
        # send guidance message into admin chat
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=hint, parse_mode="Markdown")
        return

    # ADMIN ACTIONS
    if data.startswith("ad:"):
        return await on_admin_action(update, context)

# =========================
# USER TEXT
# =========================
async def on_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if is_locked(user_id):
        return await update.message.reply_text("הפנייה שלך נמצאת בבדיקה מול נציג. בשלב זה אי אפשר להמשיך בבוט עד שתקבל עדכון.")

    state = get_state(context)

    # custom amount
    if state == S_CUSTOM_AMOUNT:
        txt = (update.message.text or "").strip()
        if not txt.isdigit():
            return await update.message.reply_text("אנא שלח מספרים בלבד.")
        amount = int(txt)
        if amount < CUSTOM_MIN_AMOUNT:
            return await update.message.reply_text(f"סכום חייב להיות מינימום {CUSTOM_MIN_AMOUNT} ומעלה. נסה שוב.")
        context.user_data["amount"] = amount
        return await ask_site_user(update, context)

    # site user
    if state == S_SITE_USER:
        site_user = (update.message.text or "").strip()
        if len(site_user) < 2:
            return await update.message.reply_text("שם משתמש קצר מדי. נסה שוב.")
        context.user_data["site_user"] = site_user
        return await ask_method(update, context)

    # waiting states -> photo only
    if state in (S_WAIT_PAYMENT_DETAILS, S_WAIT_RECEIPT):
        return await update.message.reply_text(RECEIPT_ONLY_PHOTO_TEXT, parse_mode="Markdown")

    return await update.message.reply_text("כדי להתחיל הפקדה לחץ /start")

# =========================
# USER PHOTO (receipt)
# =========================
async def on_user_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if is_locked(user_id):
        return await update.message.reply_text("הפנייה שלך נמצאת בבדיקה מול נציג. בשלב זה אי אפשר להמשיך בבוט עד שתקבל עדכון.")

    state = get_state(context)

    # Accept photos only in WAIT_RECEIPT / WAIT_RECEIPT_MORE.
    # BUT: after admin sends /sendpay, user will still be in WAIT_PAYMENT_DETAILS in memory.
    # So we allow photo in WAIT_PAYMENT_DETAILS too (because user received details and can now send receipt).
    if state not in (S_WAIT_PAYMENT_DETAILS, S_WAIT_RECEIPT, S_WAIT_RECEIPT_MORE):
        return await update.message.reply_text("כדי לבצע הפקדה, לחץ /start והמשך לפי השלבים.")

    amount = context.user_data.get("amount")
    site_user = context.user_data.get("site_user")
    method = context.user_data.get("method")
    if not amount or not site_user or not method:
        reset_flow(context)
        return await update.message.reply_text("חסר מידע בתהליך. לחץ /start להתחלה מחדש.")

    # Photo file id (best resolution)
    file_id = update.message.photo[-1].file_id

    # Create request id if not exists in this run
    rid = context.user_data.get("request_id")
    if not rid:
        rid = gen_request_id()
        context.user_data["request_id"] = rid
        log_request(rid, user_id, update.effective_user.username or "", amount, site_user, method, "receipt_sent")
    else:
        # additional receipt
        log_request(rid, user_id, update.effective_user.username or "", amount, site_user, method, "receipt_updated")

    # User reply
    await update.message.reply_text(AFTER_RECEIPT_TEXT)

    # Send ticket to admins
    pm_label = dict(PAYMENT_METHODS).get(method, method)
    username = update.effective_user.username or ""
    ticket_text = (
        "🧾 בקשת הפקדה חדשה\n\n"
        f"Request ID: {rid}\n\n"
        f"סכום: {amount}\n\n"
        f"משתמש במערכת: {site_user}\n\n"
        f"שיטה: {pm_label}\n\n"
        f"טלגרם: @{username} (user_id: {user_id})\n\n"
        f"זמן: {now_utc()} UTC"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=file_id,
        caption=ticket_text,
        reply_markup=admin_receipt_ticket_kb(rid, user_id),
    )

    # Move to receipt waiting state (pending admin decision)
    set_state(context, S_WAIT_RECEIPT)

    # Reminder if admin asked for more will be scheduled later. For now, no reminder needed after receipt sent.

# =========================
# ADMIN TEXT (guided details capture)
# =========================
async def on_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only handle non-command text messages IN ADMIN CHAT from admins
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return
    admin_id = update.effective_user.id
    if not is_admin(admin_id):
        return

    pending = get_admin_pending(admin_id)
    if not pending:
        return

    user_id = int(pending["user_id"])
    method = pending["method"]
    details = (update.message.text or "").strip()

    if not details:
        return await update.message.reply_text("שלח טקסט עם הפרטים (מספר/פרטי חשבון). או /cancelpay לביטול.")

    # send template to user
    try:
        await send_payment_details_and_request_photo(context, user_id, method, details)
    except Exception:
        await update.message.reply_text("לא הצלחתי לשלוח ללקוח. אולי הוא חסום/לא התחיל שיחה עם הבוט.")
        return

    clear_admin_pending(admin_id)

    method_name = {"bit": "Bit", "paybox": "PayBox", "bank": "העברה בנקאית"}.get(method, method)
    await update.message.reply_text(f"✅ נשלחו פרטי תשלום ללקוח ({method_name}). עכשיו מחכים לאסמכתא (תמונה בלבד).")

# =========================
# ADMIN INLINE ACTIONS (approve/problem/more + lock/unlock)
# =========================
async def on_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    admin_id = q.from_user.id
    logger.info(f"🔍 Admin action: admin_id={admin_id}, data={q.data}")
    
    if not is_admin(admin_id):
        logger.warning(f"⚠️ User {admin_id} not in ADMIN_USER_IDS")
        await q.answer("אין הרשאה", show_alert=True)
        return

    await q.answer()
    parts = q.data.split(":")
    logger.info(f"📊 Parsed data: parts={parts}")

    # ad:unlock:<user_id> / ad:block:<user_id>
    if parts[1] in ("unlock", "block"):
        logger.info(f"✅ Processing unlock/block: {parts[1]}")
        uid = int(parts[2])
        if parts[1] == "unlock":
            set_locked(uid, False)
            try:
                await context.bot.send_message(chat_id=uid, text="🔓 שוחררת. אפשר להתחיל הפקדה מחדש עם /start")
            except Exception:
                pass
            if q.message.caption:
                await q.edit_message_caption((q.message.caption or "") + "\n\n🔓 שוחרר נעילה")
            else:
                await q.edit_message_text((q.message.text or "") + "\n\n🔓 שוחרר נעילה")
        else:
            set_locked(uid, True)
            if q.message.caption:
                await q.edit_message_caption((q.message.caption or "") + "\n\n🚫 המשתמש ננעל/נחסם")
            else:
                await q.edit_message_text((q.message.text or "") + "\n\n🚫 המשתמש ננעל/נחסם")
        return

    # ad:<action>:<rid>:<user_id>
    action = parts[1]
    rid = parts[2]
    uid = int(parts[3])
    logger.info(f"📢 Admin action: {action}, rid={rid}, user_id={uid}")

    if action == "ok":
        logger.info(f"✅ Approving deposit for user {uid}")
        set_locked(uid, False)
        cancel_jobs_by_name(context.job_queue, f"rem_{uid}")

        await context.bot.send_message(chat_id=uid, text=SUCCESS_TEXT)
        schedule_return_to_menu(context, uid, uid)

        if q.message.caption:
            await q.edit_message_caption((q.message.caption or "") + "\n\n✅ סטטוס: בוצע בהצלחה")
        else:
            await q.edit_message_text((q.message.text or "") + "\n\n✅ סטטוס: בוצע בהצלחה")
        return

    if action == "problem":
        set_locked(uid, True)
        cancel_jobs_by_name(context.job_queue, f"rem_{uid}")

        await context.bot.send_message(chat_id=uid, text=PROBLEM_TEXT)

        if q.message.caption:
            await q.edit_message_caption((q.message.caption or "") + "\n\n❌ סטטוס: בעיה (ננעל עד שחרור)")
        else:
            await q.edit_message_text((q.message.text or "") + "\n\n❌ סטטוס: בעיה (ננעל עד שחרור)")
        return

    if action == "more":
        # ask for another photo
        cancel_jobs_by_name(context.job_queue, f"rem_{uid}")
        await context.bot.send_message(chat_id=uid, text=MORE_INFO_TEXT)

        # schedule reminder again for the new receipt
        schedule_receipt_reminder(context, uid, uid)

        if q.message.caption:
            await q.edit_message_caption((q.message.caption or "") + "\n\n🔄 סטטוס: ביקשנו אסמכתא חדשה")
        else:
            await q.edit_message_text((q.message.text or "") + "\n\n🔄 סטטוס: ביקשנו אסמכתא חדשה")
        return
>>>>>>> Stashed changes

# =========================
# MAIN
# =========================
<<<<<<< Updated upstream
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling update: %s", context.error, exc_info=context.error)
    if update and isinstance(update, Update):
        try:
            if update.effective_message:
                await update.effective_message.reply_text(
                    "אירעה שגיאה. נסה שוב או לחץ /start להתחלה מחדש."
                )
        except Exception:
            pass

=======
>>>>>>> Stashed changes
def main():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN missing in .env")
    if ADMIN_CHAT_ID == 0:
        raise SystemExit("ADMIN_CHAT_ID missing in .env")

<<<<<<< Updated upstream
    async def _check_admin_chat():
        """Verify we can send messages to ADMIN_CHAT_ID before accepting clients."""
        bot = Bot(BOT_TOKEN)
        try:
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text="✅ הבוט עלה. ערוץ הנציג מחובר.",
            )
        except Exception as e:
            err = str(e).strip() or type(e).__name__
            logger.error("Cannot send to ADMIN_CHAT_ID=%s: %s", ADMIN_CHAT_ID, err)
            raise SystemExit(
                "לא ניתן לשלוח הודעות לנציג (ADMIN_CHAT_ID).\n"
                "תקן את הקובץ .env:\n"
                "• הנציג חייב לפתוח את הבוט ולשלוח /start פעם אחת.\n"
                "• ADMIN_CHAT_ID חייב להיות המספר של הצ'אט (לא @username).\n"
                "  לקבלת המספר: הנציג שולח /myid לבוט ומעתיק את המספר.\n"
                "• אם הנציג הוא קבוצה – הבוט חייב להיות בקבוצה וה-ID הוא מספר שלילי."
            )

    asyncio.run(_check_admin_chat())

    # אחרי asyncio.run() הלופ נסגר (Python 3.10+). run_polling() דורש לופ פעיל.
    asyncio.set_event_loop(asyncio.new_event_loop())

    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_error_handler(error_handler)

    # Commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("myid", cmd_myid))
    app.add_handler(CommandHandler("unlock", cmd_unlock))
    app.add_handler(CommandHandler("block", cmd_block))
    app.add_handler(CommandHandler("bit", cmd_bit))
    app.add_handler(CommandHandler("bit_free", cmd_bit_free))
    app.add_handler(CommandHandler("bank", cmd_bank))
    app.add_handler(CommandHandler("cancelpay", cmd_cancelpay))

    # Callbacks
    app.add_handler(CallbackQueryHandler(on_client_callback))

    # Admin: טקסט בקבוצה בלבד
    admin_chat_filter = filters.Chat(ADMIN_CHAT_ID)
    app.add_handler(MessageHandler(admin_chat_filter & filters.TEXT & ~filters.COMMAND, on_admin_text), group=0)

    # Client: פרטי בלבד — /start גם כטקסט (לפני lock check)
    private_filter = filters.ChatType.PRIVATE
    app.add_handler(MessageHandler(private_filter & filters.Regex(re.compile(r"^(/start|start|התחל|התחלה)(\s|$)", re.I)), cmd_start), group=0)
    app.add_handler(MessageHandler(private_filter & (filters.PHOTO | filters.Document.IMAGE), on_client_photo), group=1)
    app.add_handler(MessageHandler(private_filter & filters.TEXT & ~filters.COMMAND, on_client_text), group=1)
=======
    init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # user
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("myid", cmd_myid))

    # admin shortcuts (optional)
    app.add_handler(CommandHandler("unlock", cmd_unlock))
    app.add_handler(CommandHandler("block", cmd_block))
    app.add_handler(CommandHandler("bit", cmd_bit))
    app.add_handler(CommandHandler("paybox", cmd_paybox))
    app.add_handler(CommandHandler("bank", cmd_bank))
    app.add_handler(CommandHandler("cancelpay", cmd_cancelpay))

    # callbacks
    app.add_handler(CallbackQueryHandler(on_callback))

    # admin guided: non-command text in admin chat
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.SUPERGROUP, on_admin_text), group=0)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUP, on_admin_text), group=0)

    # messages (פרטי + קבוצות, מלבד צ'אט אדמין)
    app.add_handler(MessageHandler(filters.PHOTO & USER_CHAT_FILTER, on_user_photo), group=1)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & USER_CHAT_FILTER, on_user_text), group=1)
>>>>>>> Stashed changes

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
<<<<<<< Updated upstream
    main()
=======
    main()
>>>>>>> Stashed changes
