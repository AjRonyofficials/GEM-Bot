import asyncio
from collections import Counter
from datetime import datetime, timedelta
import json
import logging
import random
import re
import sqlite3
import httpx
import telegram
from telegram import (
    BotCommand,
    BotCommandScopeChat,
    BotCommandScopeDefault,
    CopyTextButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TELEGRAM_BOT_TOKEN = "8780796806:AAHDpaKoTETjt9LZt6z9F2kE18RZoamGu1Y"
BOT_USERNAME = "GrowthEliteMarketing_bot"
PRIME_ADMIN_ID = 5017126108
PRIME_ADMIN_USERNAME = "IsmailIslamRony1"
DEV_SIGNATURE = "👨‍💻 **Developed by:** @IsmailIslamRony1"
ADMIN_DIRECT_URL = f"https://t.me/{PRIME_ADMIN_USERNAME}"

OTP_GROUP_ID = -1003996700234
OTP_GROUP_LINK = "https://t.me/+jl7p94sLx5JhMzFl"
OTP_REWARD = 0.50
MIN_WITHDRAW = 50.00

# HADI / CR API CONFIGURATION
CR_API_URL = "http://147.135.212.197/crapi/had/viewstats"
CR_API_TOKEN = "QlBYQklBUzRdV4hea5VzRXSJYnlDjGtKXWFmg4NoaGViYm2AX3eHZg=="

ALLOWED_SERVICES = ["facebook", "whatsapp", "instagram"]

SERVICE_ICONS = {
    "Facebook": "📘",
    "WhatsApp": "💬",
    "Instagram": "📸",
}

SERVICE_SHORT_NAMES = {
    "Facebook": "FB",
    "WhatsApp": "WA",
    "Instagram": "IG",
}

def match_allowed_service(text: str) -> str:
    if not text:
        return None
    t = str(text).lower()
    if "facebook" in t or "fb" in t:
        return "Facebook"
    if "whatsapp" in t or "wa" in t:
        return "WhatsApp"
    if "instagram" in t or "ig" in t:
        return "Instagram"
    return None

COUNTRY_PREFIX_DATABASE = {
    "1": ("USA / Canada", "🇺🇸", "US"),
    "7": ("Russia / Kazakhstan", "🇷🇺", "RU"),
    "20": ("Egypt", "🇪🇬", "EG"),
    "27": ("South Africa", "🇿🇦", "ZA"),
    "30": ("Greece", "🇬🇷", "GR"),
    "31": ("Netherlands", "🇳🇱", "NL"),
    "32": ("Belgium", "🇧🇪", "BE"),
    "33": ("France", "🇫🇷", "FR"),
    "34": ("Spain", "🇪🇸", "ES"),
    "36": ("Hungary", "🇭🇺", "HU"),
    "39": ("Italy", "🇮🇹", "IT"),
    "40": ("Romania", "🇷🇴", "RO"),
    "41": ("Switzerland", "🇨🇭", "CH"),
    "43": ("Austria", "🇦🇹", "AT"),
    "44": ("United Kingdom", "🇬🇧", "GB"),
    "45": ("Denmark", "🇩🇰", "DK"),
    "46": ("Sweden", "🇸🇪", "SE"),
    "47": ("Norway", "🇳🇴", "NO"),
    "48": ("Poland", "🇵🇱", "PL"),
    "49": ("Germany", "🇩🇪", "DE"),
    "51": ("Peru", "🇵🇪", "PE"),
    "52": ("Mexico", "🇲🇽", "MX"),
    "54": ("Argentina", "🇦🇷", "AR"),
    "55": ("Brazil", "🇧🇷", "BR"),
    "56": ("Chile", "🇨🇱", "CL"),
    "57": ("Colombia", "🇨🇴", "CO"),
    "58": ("Venezuela", "🇻🇪", "VE"),
    "60": ("Malaysia", "🇲🇾", "MY"),
    "61": ("Australia", "🇦🇺", "AU"),
    "62": ("Indonesia", "🇮🇩", "ID"),
    "63": ("Philippines", "🇵🇭", "PH"),
    "64": ("New Zealand", "🇳🇿", "NZ"),
    "65": ("Singapore", "🇸🇬", "SG"),
    "66": ("Thailand", "🇹🇭", "TH"),
    "81": ("Japan", "🇯🇵", "JP"),
    "82": ("South Korea", "🇰🇷", "KR"),
    "84": ("Vietnam", "🇻🇳", "VN"),
    "86": ("China", "🇨🇳", "CN"),
    "90": ("Turkey", "🇹🇷", "TR"),
    "91": ("India", "🇮🇳", "IN"),
    "92": ("Pakistan", "🇵🇰", "PK"),
    "93": ("Afghanistan", "🇦🇫", "AF"),
    "94": ("Sri Lanka", "🇱🇰", "LK"),
    "95": ("Myanmar", "🇲🇲", "MM"),
    "98": ("Iran", "🇮🇷", "IR"),
    "212": ("Morocco", "🇲🇦", "MA"),
    "213": ("Algeria", "🇩🇿", "DZ"),
    "216": ("Tunisia", "🇹🇳", "TN"),
    "218": ("Libya", "🇱🇾", "LY"),
    "220": ("Gambia", "🇬🇲", "GM"),
    "221": ("Senegal", "🇸🇳", "SN"),
    "222": ("Mauritania", "🇲🇷", "MR"),
    "223": ("Mali", "🇲🇱", "ML"),
    "224": ("Guinea", "🇬🇳", "GN"),
    "225": ("Ivory Coast", "🇨🇮", "CI"),
    "226": ("Burkina Faso", "🇧🇫", "BF"),
    "227": ("Niger", "🇳🇪", "NE"),
    "228": ("Togo", "🇹🇬", "TG"),
    "229": ("Benin", "🇧🇯", "BJ"),
    "230": ("Mauritius", "🇲🇺", "MU"),
    "231": ("Liberia", "🇱🇷", "LR"),
    "232": ("Sierra Leone", "🇸🇱", "SL"),
    "233": ("Ghana", "🇬🇭", "GH"),
    "234": ("Nigeria", "🇳🇬", "NG"),
    "235": ("Chad", "🇹🇩", "TD"),
    "236": ("Central African Rep.", "🇨🇫", "CF"),
    "237": ("Cameroon", "🇨🇲", "CM"),
    "238": ("Cape Verde", "🇨🇻", "CV"),
    "239": ("Sao Tome", "🇸🇹", "ST"),
    "240": ("Equatorial Guinea", "🇬🇶", "GQ"),
    "241": ("Gabon", "🇬🇦", "GA"),
    "242": ("Republic of the Congo", "🇨🇬", "CG"),
    "243": ("DR Congo", "🇨🇩", "CD"),
    "244": ("Angola", "🇦🇴", "AO"),
    "245": ("Guinea-Bissau", "🇬🇼", "GW"),
    "248": ("Seychelles", "🇸🇨", "SC"),
    "249": ("Sudan", "🇸🇩", "SD"),
    "250": ("Rwanda", "🇷🇼", "RW"),
    "251": ("Ethiopia", "🇪🇹", "ET"),
    "252": ("Somalia", "🇸🇴", "SO"),
    "253": ("Djibouti", "🇩🇯", "DJ"),
    "254": ("Kenya", "🇰🇪", "KE"),
    "255": ("Tanzania", "🇹🇿", "TZ"),
    "256": ("Uganda", "🇺🇬", "UG"),
    "257": ("Burundi", "🇧🇮", "BI"),
    "258": ("Mozambique", "🇲🇿", "MZ"),
    "260": ("Zambia", "🇿🇲", "ZM"),
    "261": ("Madagascar", "🇲🇬", "MG"),
    "262": ("Reunion / Mayotte", "🇷🇪", "RE"),
    "263": ("Zimbabwe", "🇿🇼", "ZW"),
    "264": ("Namibia", "🇳🇦", "NA"),
    "265": ("Malawi", "🇲🇼", "MW"),
    "266": ("Lesotho", "🇱🇸", "LS"),
    "267": ("Botswana", "🇧🇼", "BW"),
    "268": ("Eswatini", "🇸🇿", "SZ"),
    "269": ("Comoros", "🇰🇲", "KM"),
    "351": ("Portugal", "🇵🇹", "PT"),
    "352": ("Luxembourg", "🇱🇺", "LU"),
    "353": ("Ireland", "🇮🇪", "IE"),
    "354": ("Iceland", "🇮🇸", "IS"),
    "355": ("Albania", "🇦🇱", "AL"),
    "356": ("Malta", "🇲🇹", "MT"),
    "357": ("Cyprus", "🇨🇾", "CY"),
    "358": ("Finland", "🇫🇮", "FI"),
    "359": ("Bulgaria", "🇧🇬", "BG"),
    "370": ("Lithuania", "🇱🇹", "LT"),
    "371": ("Latvia", "🇱🇻", "LV"),
    "372": ("Estonia", "🇪🇪", "EE"),
    "373": ("Moldova", "🇲🇩", "MD"),
    "374": ("Armenia", "🇦🇲", "AM"),
    "375": ("Belarus", "🇧🇾", "BY"),
    "376": ("Andorra", "🇦🇩", "AD"),
    "377": ("Monaco", "🇲🇨", "MC"),
    "378": ("San Marino", "🇸🇲", "SM"),
    "380": ("Ukraine", "🇺🇦", "UA"),
    "381": ("Serbia", "🇷🇸", "RS"),
    "382": ("Montenegro", "🇲🇪", "ME"),
    "383": ("Kosovo", "🇽🇰", "XK"),
    "385": ("Croatia", "🇭🇷", "HR"),
    "386": ("Slovenia", "🇸🇮", "SI"),
    "387": ("Bosnia and Herzegovina", "🇧🇦", "BA"),
    "389": ("North Macedonia", "🇲🇰", "MK"),
    "420": ("Czech Republic", "🇨🇿", "CZ"),
    "421": ("Slovakia", "🇸🇰", "SK"),
    "423": ("Liechtenstein", "🇱🇮", "LI"),
    "501": ("Belize", "🇧🇿", "BZ"),
    "502": ("Guatemala", "🇬🇹", "GT"),
    "503": ("El Salvador", "🇸🇻", "SV"),
    "504": ("Honduras", "🇭🇳", "HN"),
    "505": ("Nicaragua", "🇳🇮", "NI"),
    "506": ("Costa Rica", "🇨🇷", "CR"),
    "507": ("Panama", "🇵🇦", "PA"),
    "509": ("Haiti", "🇭🇹", "HT"),
    "591": ("Bolivia", "🇧🇴", "BO"),
    "592": ("Guyana", "🇬🇾", "GY"),
    "593": ("Ecuador", "🇪🇨", "EC"),
    "594": ("French Guiana", "🇬🇫", "GF"),
    "595": ("Paraguay", "🇵🇾", "PY"),
    "597": ("Suriname", "🇸🇷", "SR"),
    "598": ("Uruguay", "🇺🇾", "UY"),
    "852": ("Hong Kong", "🇭🇰", "HK"),
    "853": ("Macau", "🇲🇴", "MO"),
    "855": ("Cambodia", "🇰🇭", "KH"),
    "856": ("Laos", "🇱🇦", "LA"),
    "880": ("Bangladesh", "🇧🇩", "BD"),
    "886": ("Taiwan", "🇹🇼", "TW"),
    "960": ("Maldives", "🇲🇻", "MV"),
    "961": ("Lebanon", "🇱🇧", "LB"),
    "962": ("Jordan", "🇯🇴", "JO"),
    "963": ("Syria", "🇸🇾", "SY"),
    "964": ("Iraq", "🇮🇶", "IQ"),
    "965": ("Kuwait", "🇰🇼", "KW"),
    "966": ("Saudi Arabia", "🇸🇦", "SA"),
    "967": ("Yemen", "🇾🇪", "YE"),
    "968": ("Oman", "🇴🇲", "OM"),
    "970": ("Palestine", "🇵🇸", "PS"),
    "971": ("UAE", "🇦🇪", "AE"),
    "972": ("Israel", "🇮🇱", "IL"),
    "973": ("Bahrain", "🇧🇭", "BH"),
    "974": ("Qatar", "🇶🇦", "QA"),
    "975": ("Bhutan", "🇧🇹", "BT"),
    "976": ("Mongolia", "🇲🇳", "MN"),
    "977": ("Nepal", "🇳🇵", "NP"),
    "992": ("Tajikistan", "🇹🇯", "TJ"),
    "993": ("Turkmenistan", "🇹🇲", "TM"),
    "994": ("Azerbaijan", "🇦🇿", "AZ"),
    "995": ("Georgia", "🇬🇪", "GE"),
    "996": ("Kyrgyzstan", "🇰🇬", "KG"),
    "998": ("Uzbekistan", "🇺🇿", "UZ"),
}

def get_country_info(phone_or_range: str):
    clean_digits = re.sub(r"\D", "", str(phone_or_range))
    if not clean_digits:
        return "Global Route", "🌐", "GL"

    for length in (4, 3, 2, 1):
        if len(clean_digits) >= length:
            sub_pfx = clean_digits[:length]
            if sub_pfx in COUNTRY_PREFIX_DATABASE:
                return COUNTRY_PREFIX_DATABASE[sub_pfx]

    return "Global Route", "🌐", "GL"

def mask_phone_number(num: str) -> str:
    clean = re.sub(r"\D", "", str(num))
    if len(clean) <= 6 or "X" in str(num).upper() or "*" in str(num):
        prefix = clean[:4] if len(clean) >= 4 else (clean + "0000")[:4]
        return f"{prefix}•••••{random.randint(100, 999)}"
    return f"{clean[:4]}•••••{clean[-3:]}"

def format_range_as_stars(range_str: str) -> str:
    clean = str(range_str).replace("+", "").strip()
    clean = re.sub(r"[xX]+", "***", clean)
    if "***" not in clean and len(clean) >= 4:
        return f"{clean[:4]}***"
    return clean

PANEL_CONFIG = {
    "panel1": {
        "name": "Kop Engine 1",
        "active_ranges_url": "https://api.zenexnetwork.com/v1/active-ranges",
        "get_num_url": "https://api.zenexnetwork.com/v1/getnum",
        "get_sms_url": "https://api.zenexnetwork.com/v1/numsuccess/info",
        "console_url": "https://www.zenexnetwork.com/api/v1/global-broadcast",
        "headers": {
            "mapikey": "ZNX_SDY9RBKGG8DO84EWZOMWEH2S",
            "Content-Type": "application/json",
        },
        "panel_type": "zenex",
    },
    "panel2": {
        "name": "Kop Engine 2",
        "active_ranges_url": "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api/liveaccess",
        "get_num_url": "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api/getnum",
        "get_sms_url": "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api/success-otp",
        "console_url": "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api/console",
        "headers": {
            "mauthapi": "MVKG0O9RFM7",
            "Content-Type": "application/json",
        },
        "panel_type": "voltx",
    },
    "panel3": {
        "name": "Kop Engine 3",
        "active_ranges_url": "https://2eee7.com/@Access/@Bot/2eee7/@public/api/liveaccess",
        "get_num_url": "https://2eee7.com/@Access/@Bot/2eee7/@public/api/getnum",
        "get_sms_url": "https://2eee7.com/@Access/@Bot/2eee7/@public/api/success-otp-info",
        "console_url": "https://2eee7.com/@Access/@Bot/2eee7/@public/api/live-console",
        "headers": {
            "X-API-Key": "MURAD_FEDAB3D2B6E2DEF802C8A6D6",
            "Content-Type": "application/json",
        },
        "panel_type": "fastx",
    },
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

ACTIVE_SYNC_TASKS = {}
USER_STATES = {}
PENDING_WITHDRAWALS = {}
PROCESSED_CONSOLE_IDS = set()
CACHED_RANGES = {}
RANGE_HIT_TIMESTAMPS = {}

def get_db():
    return sqlite3.connect("bot_database.db", timeout=10.0)

def init_db():
    with get_db() as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance REAL DEFAULT 0.0,
            total_otp INTEGER DEFAULT 0,
            joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            added_by INTEGER,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS premium_numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE,
            service TEXT DEFAULT 'General',
            status TEXT DEFAULT 'available',
            assigned_user INTEGER DEFAULT NULL,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        db.execute(
            "INSERT OR IGNORE INTO admins (user_id, added_by) VALUES (?, ?)",
            (PRIME_ADMIN_ID, PRIME_ADMIN_ID),
        )
        db.commit()

init_db()

def is_admin(user_id: int, username: str = None) -> bool:
    if user_id == PRIME_ADMIN_ID:
        return True
    if username and username.replace("@", "").lower() == PRIME_ADMIN_USERNAME.lower():
        return True
    try:
        with get_db() as db:
            cur = db.cursor()
            cur.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,))
            return cur.fetchone() is not None
    except Exception:
        return False

def is_prime_admin(user_id: int, username: str = None) -> bool:
    if user_id == PRIME_ADMIN_ID:
        return True
    if username and username.replace("@", "").lower() == PRIME_ADMIN_USERNAME.lower():
        return True
    return False

def db_get_or_create_user(user_id: int, username: str, full_name: str):
    with get_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            cur.execute(
                "INSERT INTO users (user_id, username, full_name, balance, total_otp) VALUES (?, ?, ?, 0.0, 0)",
                (user_id, username or "", full_name or ""),
            )
            db.commit()
            cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
        else:
            cur.execute(
                "UPDATE users SET username = ?, full_name = ? WHERE user_id = ?",
                (username or "", full_name or "", user_id),
            )
            db.commit()
        return row

def db_add_otp_reward(user_id: int, reward: float = OTP_REWARD, username: str = None, full_name: str = None):
    with get_db() as db:
        if username or full_name:
            db.execute(
                "UPDATE users SET balance = balance + ?, total_otp = total_otp + 1, username = COALESCE(?, username), full_name = COALESCE(?, full_name) WHERE user_id = ?",
                (reward, username, full_name, user_id),
            )
        else:
            db.execute(
                "UPDATE users SET balance = balance + ?, total_otp = total_otp + 1 WHERE user_id = ?",
                (reward, user_id),
            )
        db.commit()

def db_deduct_balance(user_id: int, amount: float):
    with get_db() as db:
        db.execute(
            "UPDATE users SET balance = MAX(0.0, balance - ?) WHERE user_id = ?",
            (amount, user_id),
        )
        db.commit()

def db_refund_balance(user_id: int, amount: float):
    with get_db() as db:
        db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id),
        )
        db.commit()

def db_set_user_balance(user_id: int, new_balance: float):
    with get_db() as db:
        db.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        db.commit()

def db_set_user_otp_count(user_id: int, new_otps: int):
    with get_db() as db:
        db.execute("UPDATE users SET total_otp = ? WHERE user_id = ?", (new_otps, user_id))
        db.commit()

def db_add_premium_numbers_bulk(numbers: list, service: str = "Facebook") -> tuple:
    added, skipped = 0, 0
    with get_db() as db:
        for num in numbers:
            clean = str(num).strip().replace("+", "").replace(" ", "").replace("-", "")
            if len(clean) >= 6:
                try:
                    db.execute(
                        "INSERT INTO premium_numbers (phone_number, service, status) VALUES (?, ?, 'available')",
                        (clean, service),
                    )
                    added += 1
                except sqlite3.IntegrityError:
                    skipped += 1
        db.commit()
    return added, skipped

def db_get_available_premium_numbers(user_id: int, service: str = "General", count: int = 3):
    with get_db() as db:
        cur = db.cursor()
        cur.execute(
            "SELECT id, phone_number FROM premium_numbers WHERE status = 'available' AND service = ? LIMIT ?",
            (service, count),
        )
        rows = cur.fetchall()
        if len(rows) < count:
            cur.execute(
                "SELECT id, phone_number FROM premium_numbers WHERE status = 'available' LIMIT ?",
                (count,),
            )
            rows = cur.fetchall()
        
        if rows:
            ids = [r[0] for r in rows]
            phone_numbers = [r[1] for r in rows]
            placeholders = ','.join(['?'] * len(ids))
            db.execute(
                f"UPDATE premium_numbers SET status = 'in_use', assigned_user = ? WHERE id IN ({placeholders})",
                [user_id] + ids
            )
            db.commit()
            return phone_numbers
    return []

def extract_pure_code(text):
    clean_text = re.sub(r"<#[^>]*>|[@#$:]", " ", str(text))
    match = re.search(r"\b\d{4,8}\b", clean_text)
    if match:
        return match.group(0)
    digits_only = re.sub(r"\D", "", str(text))
    return digits_only if digits_only else str(text)

def safe_json_parse(response_text: str):
    try:
        return json.loads(response_text)
    except Exception:
        return None

def get_main_reply_keyboard(user_id: int = None, username: str = None):
    keyboard = [
        [KeyboardButton("📱 Get Number"), KeyboardButton("💎 Premium Strong Number")],
        [KeyboardButton("💳 My Account"), KeyboardButton("💰 Withdraw")],
        [KeyboardButton("📊 Status"), KeyboardButton("☎️ Support")],
    ]
    if user_id and is_admin(user_id, username):
        keyboard.append([KeyboardButton("👑 Admin Panel"), KeyboardButton("📢 Broadcast")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def send_group_styled_otp(app, panel_name: str, service_name: str, raw_number: str, pure_code: str, full_msg: str):
    _, flag_emoji, iso_code = get_country_info(raw_number)
    masked_num = mask_phone_number(raw_number)
    srv_icon = SERVICE_ICONS.get(service_name, "🌐")
    srv_short = SERVICE_SHORT_NAMES.get(service_name, service_name[:2].upper())

    group_text = f"⚡ {panel_name} | {srv_icon} {flag_emoji} {iso_code} | {masked_num} {srv_short}"

    keyboard = [
        [
            InlineKeyboardButton(f"🔑 📋 {pure_code}", copy_text=CopyTextButton(text=pure_code)),
            InlineKeyboardButton("📝 📋 Full Msg", copy_text=CopyTextButton(text=full_msg)),
        ],
        [
            InlineKeyboardButton("📞 Number BOT ↗", url=f"https://t.me/{BOT_USERNAME}"),
        ]
    ]

    max_retries = 3
    for attempt in range(max_retries):
        try:
            await app.bot.send_message(
                chat_id=OTP_GROUP_ID,
                text=group_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                disable_web_page_preview=True
            )
            break
        except telegram.error.RetryAfter as e:
            wait_time = e.retry_after + 1
            await asyncio.sleep(wait_time)
        except Exception:
            break

async def fetch_optimized_ranges(client: httpx.AsyncClient, config: dict, service_name: str, mode: str = "hit") -> list:
    hit_counter = Counter()
    discovered_ranges = set()
    now = datetime.now()

    try:
        res_console = await client.get(CR_API_URL, params={"token": CR_API_TOKEN, "records": 50}, timeout=6.0)
        if res_console.status_code == 200:
            data = safe_json_parse(res_console.text)
            if isinstance(data, dict) and data.get("status") == "success":
                for row in data.get("data", []):
                    sender_cli = str(row.get("cli", ""))
                    full_msg = str(row.get("message", ""))
                    if match_allowed_service(sender_cli) or match_allowed_service(full_msg):
                        raw_num = str(row.get("num", "")).replace("+", "").strip()
                        if len(raw_num) >= 5:
                            r_key = f"{raw_num[:5]}***"
                            discovered_ranges.add(r_key)
                            hit_counter[r_key] += 20
                            RANGE_HIT_TIMESTAMPS[r_key] = now
    except Exception:
        pass

    try:
        res_console = await client.get(config["console_url"], headers=config["headers"], timeout=6.0)
        if res_console.status_code == 200:
            data_console = safe_json_parse(res_console.text)
            feed_items = []
            if config["panel_type"] == "zenex":
                feed_items = data_console.get("data", []) if isinstance(data_console, dict) else (data_console if isinstance(data_console, list) else [])
            elif config["panel_type"] == "voltx":
                feed_items = data_console.get("data", {}).get("hits", []) or data_console.get("hits", [])
            elif config["panel_type"] == "fastx":
                feed_items = data_console.get("data", {}).get("otps", []) or data_console.get("otps", [])

            if isinstance(feed_items, list):
                for item in feed_items:
                    srv = str(item.get("service") or item.get("platform") or item.get("sid") or "")
                    if service_name.lower() in srv.lower() or not srv:
                        raw_num = str(item.get("number") or item.get("range") or item.get("phone", "")).replace("+", "").strip()
                        if "XXX" in raw_num.upper() or "***" in raw_num:
                            r_key = raw_num.upper().replace("XXX", "***")
                            discovered_ranges.add(r_key)
                            hit_counter[r_key] += 15
                            RANGE_HIT_TIMESTAMPS[r_key] = now
                        elif len(raw_num) >= 5:
                            r_key = f"{raw_num[:5]}***"
                            discovered_ranges.add(r_key)
                            hit_counter[r_key] += 10
                            RANGE_HIT_TIMESTAMPS[r_key] = now
    except Exception:
        pass

    try:
        res_ranges = await client.get(config["active_ranges_url"], headers=config["headers"], timeout=6.0)
        if res_ranges.status_code == 200:
            data_ranges = safe_json_parse(res_ranges.text)
            active_list = data_ranges.get("data", {}).get("active_ranges", []) or data_ranges.get("active_ranges", []) or data_ranges.get("services", [])
            if isinstance(active_list, list):
                for item in active_list:
                    srv = str(item.get("service", "") or item.get("sid", ""))
                    if service_name.lower() in srv.lower() or not srv:
                        r = item.get("range") or item.get("ranges", [])
                        if isinstance(r, list):
                            for sub_r in r:
                                starred_r = format_range_as_stars(sub_r)
                                discovered_ranges.add(starred_r)
                                hit_counter[starred_r] += 8
                                RANGE_HIT_TIMESTAMPS[starred_r] = now
                        elif r:
                            starred_r = format_range_as_stars(r)
                            discovered_ranges.add(starred_r)
                            try:
                                hits_val = int(item.get("hits", item.get("count", 10)))
                            except Exception:
                                hits_val = 10
                            hit_counter[starred_r] += hits_val
                            RANGE_HIT_TIMESTAMPS[starred_r] = now
    except Exception:
        pass

    if not discovered_ranges:
        return []

    cleaned_ranges = []
    for r in discovered_ranges:
        last_hit = RANGE_HIT_TIMESTAMPS.get(r)
        if mode == "hit" and last_hit:
            if (now - last_hit) > timedelta(minutes=6):
                continue
        cleaned_ranges.append(r)

    if mode == "recent":
        hit_list_tmp = [r for r in cleaned_ranges if RANGE_HIT_TIMESTAMPS.get(r) and (now - RANGE_HIT_TIMESTAMPS.get(r)) <= timedelta(minutes=6)]
        high_hit_set = set(hit_list_tmp)
        cleaned_ranges = [r for r in cleaned_ranges if r not in high_hit_set]
        sorted_ranges = cleaned_ranges[::-1]
    else:
        sorted_ranges = sorted(cleaned_ranges, key=lambda x: hit_counter.get(x, 1), reverse=True)

    country_count = Counter()
    final_filtered_ranges = []
    
    for r in sorted_ranges:
        _, _, country_code = get_country_info(r)
        if country_count[country_code] < 2:
            country_count[country_code] += 1
            final_filtered_ranges.append(r)
        if len(final_filtered_ranges) >= 8:
            break

    return [(r, hit_counter.get(r, 1)) for r in final_filtered_ranges]

async def sync_ranges_every_minute():
    await asyncio.sleep(2)
    logger.info("⚡ Background Range Sync & Self-Cleaning Task Started (3-5 min interval)...")
    while True:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                for p_key, config in PANEL_CONFIG.items():
                    if p_key not in CACHED_RANGES:
                        CACHED_RANGES[p_key] = {}
                    
                    for srv in ["Facebook", "WhatsApp", "Instagram"]:
                        try:
                            hit_ranges = await fetch_optimized_ranges(client, config, srv, mode="hit")
                            recent_ranges = await fetch_optimized_ranges(client, config, srv, mode="recent")
                            CACHED_RANGES[p_key][srv] = {
                                "hit": hit_ranges,
                                "recent": recent_ranges
                            }
                        except Exception:
                            pass
        except Exception:
            pass
        
        await asyncio.sleep(240)

async def global_console_broadcaster(app):
    await asyncio.sleep(5)
    logger.info("⚡ Background Filtered Live Streamer Started...")

    async with httpx.AsyncClient(timeout=10.0) as client:
        while True:
            try:
                hadi_res = await client.get(
                    CR_API_URL,
                    params={"token": CR_API_TOKEN, "records": 25},
                    timeout=8.0
                )
                if hadi_res.status_code == 200:
                    hadi_data = safe_json_parse(hadi_res.text)
                    if isinstance(hadi_data, dict) and hadi_data.get("status") == "success":
                        for row in hadi_data.get("data", []):
                            sender_cli = str(row.get("cli", ""))
                            full_msg = str(row.get("message", ""))
                            matched_service = match_allowed_service(sender_cli) or match_allowed_service(full_msg)

                            if not matched_service:
                                continue

                            row_num = str(row.get("num", "")).replace("+", "").strip()
                            unique_id = f"hadi_{row_num}_{row.get('dt', '')}_{full_msg}"

                            if unique_id in PROCESSED_CONSOLE_IDS:
                                continue

                            PROCESSED_CONSOLE_IDS.add(unique_id)
                            if len(PROCESSED_CONSOLE_IDS) > 3000:
                                PROCESSED_CONSOLE_IDS.clear()

                            if len(row_num) >= 5:
                                r_key = f"{row_num[:5]}***"
                                RANGE_HIT_TIMESTAMPS[r_key] = datetime.now()

                            active_user_numbers = []
                            for task_nums in ACTIVE_SYNC_TASKS.values():
                                if isinstance(task_nums, list):
                                    active_user_numbers.extend(task_nums)
                                else:
                                    active_user_numbers.append(task_nums)

                            if row_num in active_user_numbers:
                                continue

                            pure_code = extract_pure_code(full_msg)
                            await send_group_styled_otp(app, "Hadi Panel", matched_service, row_num, pure_code, full_msg)
                            await asyncio.sleep(1.2)
            except Exception:
                pass

            for p_key, config in PANEL_CONFIG.items():
                c_url = config.get("console_url")
                if not c_url:
                    continue

                try:
                    res = await client.get(c_url, headers=config["headers"])
                    if res.status_code != 200:
                        continue

                    res_json = safe_json_parse(res.text)
                    if not res_json:
                        continue

                    feed_items = []
                    if config["panel_type"] == "zenex":
                        feed_items = res_json.get("data", []) or res_json.get("active_ranges", [])
                    elif config["panel_type"] == "voltx":
                        feed_items = res_json.get("data", {}).get("hits", []) or res_json.get("hits", [])
                    elif config["panel_type"] == "fastx":
                        feed_items = res_json.get("data", {}).get("otps", []) or res_json.get("otps", [])

                    if isinstance(feed_items, list):
                        for item in feed_items:
                            service_raw = str(item.get("service") or item.get("platform") or item.get("sid") or "")
                            full_msg = str(item.get("otp") or item.get("message") or "")
                            matched_service = match_allowed_service(service_raw) or match_allowed_service(full_msg)

                            if not matched_service:
                                continue

                            unique_id = str(
                                item.get("id")
                                or item.get("otp_id")
                                or f"{item.get('range', '')}_{full_msg}_{item.get('time', '')}"
                            )

                            if unique_id in PROCESSED_CONSOLE_IDS:
                                continue

                            PROCESSED_CONSOLE_IDS.add(unique_id)
                            if len(PROCESSED_CONSOLE_IDS) > 3000:
                                PROCESSED_CONSOLE_IDS.clear()

                            raw_num = str(item.get("number") or item.get("range") or "").replace("+", "")
                            if len(raw_num) >= 5:
                                r_key = f"{raw_num[:5]}***"
                                RANGE_HIT_TIMESTAMPS[r_key] = datetime.now()

                            active_user_numbers = []
                            for task_nums in ACTIVE_SYNC_TASKS.values():
                                if isinstance(task_nums, list):
                                    active_user_numbers.extend(task_nums)
                                else:
                                    active_user_numbers.append(task_nums)

                            if raw_num in active_user_numbers:
                                continue

                            pure_code = extract_pure_code(full_msg)
                            await send_group_styled_otp(app, config["name"], matched_service, raw_num, pure_code, full_msg)
                            await asyncio.sleep(1.2)

                except Exception:
                    pass

            await asyncio.sleep(4.0)

async def check_cr_api_for_otp(client: httpx.AsyncClient, target_number: str, service_name: str = None) -> tuple:
    try:
        params = {
            "token": CR_API_TOKEN,
            "records": 50,
            "filternum": target_number,
        }
        if service_name:
            params["filtercli"] = service_name

        res = await client.get(CR_API_URL, params=params, timeout=8.0)
        if res.status_code == 200:
            res_data = safe_json_parse(res.text)
            if isinstance(res_data, dict) and res_data.get("status") == "success":
                data_rows = res_data.get("data", [])
                if isinstance(data_rows, list):
                    for row in data_rows:
                        num_in_row = str(row.get("num", "")).replace("+", "").strip()
                        if num_in_row == target_number or target_number in num_in_row:
                            msg_body = str(row.get("message", "No text received"))
                            pure_code = extract_pure_code(msg_body)
                            sender_cli = str(row.get("cli", "CR Dedicated Stream"))
                            return str(pure_code), msg_body, f"Hadi / CR Engine ({sender_cli})"
    except Exception:
        pass

    for p_key, config in PANEL_CONFIG.items():
        try:
            response = await client.get(config["get_sms_url"], headers=config["headers"], timeout=5.0)
            if response.status_code == 200:
                res_data = safe_json_parse(response.text) or {}
                otp_list = res_data.get("data", {}).get("otps", []) or res_data.get("otps", [])
                matched_otps = [
                    item for item in otp_list
                    if str(item.get("number", "")).replace("+", "") == target_number
                ]
                if matched_otps:
                    latest = matched_otps[-1]
                    full_sms = latest.get("sms") or latest.get("message") or latest.get("otp", "No text received")
                    pure_code = extract_pure_code(latest.get("otp") or full_sms)
                    return str(pure_code), str(full_sms), config["name"]
        except Exception:
            continue
    return None, None, None

async def allocate_and_send_next_numbers(context: ContextTypes.DEFAULT_TYPE, chat_id: int, panel_id: str, service_name: str, selected_range: str, range_type: str):
    config = PANEL_CONFIG.get(panel_id, PANEL_CONFIG["panel1"])
    clean_base = selected_range.replace("***", "").replace("XXX", "").strip()
    allocated_numbers = []

    async with httpx.AsyncClient(timeout=8.0) as client:
        for _ in range(3):
            variant_range = clean_base + str(random.randint(0, 999)).zfill(3)
            clean_for_api = variant_range + "XXX"

            if config["panel_type"] == "zenex":
                payload = {"range": clean_for_api, "is_national": False, "remove_plus": False}
            elif config["panel_type"] == "voltx":
                clean_range_for_rid = clean_for_api.replace("XXX", "").replace("xx", "")
                payload = {"rid": clean_range_for_rid}
            elif config["panel_type"] == "fastx":
                payload = {"range": clean_for_api}
            else:
                payload = {"range": clean_for_api}

            try:
                response = await client.post(config["get_num_url"], headers=config["headers"], json=payload)
                if response.status_code == 200:
                    res_data = safe_json_parse(response.text) or {}
                    number_data = res_data.get("data", {})
                    phone_number = number_data.get("full_number") or number_data.get("number")
                    if phone_number:
                        clean_num = str(phone_number).replace("+", "")
                        if clean_num not in allocated_numbers:
                            allocated_numbers.append(clean_num)
            except Exception:
                pass

        if not allocated_numbers:
            for _ in range(3):
                fallback_api_range = selected_range.replace("***", "XXX")
                if config["panel_type"] == "zenex":
                    payload = {"range": fallback_api_range, "is_national": False, "remove_plus": False}
                elif config["panel_type"] == "voltx":
                    payload = {"rid": fallback_api_range.replace("XXX", "")}
                else:
                    payload = {"range": fallback_api_range}

                try:
                    response = await client.post(config["get_num_url"], headers=config["headers"], json=payload)
                    if response.status_code == 200:
                        res_data = safe_json_parse(response.text) or {}
                        number_data = res_data.get("data", {})
                        phone_number = number_data.get("full_number") or number_data.get("number")
                        if phone_number:
                            clean_num = str(phone_number).replace("+", "")
                            if clean_num not in allocated_numbers:
                                allocated_numbers.append(clean_num)
                except Exception:
                    pass

    if not allocated_numbers:
        return

    ACTIVE_SYNC_TASKS[chat_id] = allocated_numbers

    keyboard = [
        [
            InlineKeyboardButton("🎲 Change Numbers", callback_data=f"buy_{panel_id}_{service_name}_{selected_range}_{range_type}"),
            InlineKeyboardButton("🌐 Change Range", callback_data=f"ranges_{panel_id}_{service_name}_{range_type}"),
        ],
        [InlineKeyboardButton("🚀 OTP Group ↗", url=OTP_GROUP_LINK)],
        [InlineKeyboardButton("🔙 « Select Panels", callback_data="open_panels")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    numbers_display = ""
    for idx, num in enumerate(allocated_numbers, 1):
        formatted_num = f"+{num}"
        c_name, c_flag, c_prefix = get_country_info(formatted_num)
        numbers_display += f"{idx}️⃣ `{formatted_num}` ({c_prefix} {c_name} {c_flag})\n"

    msg_text = (
        f"🎯 **3 NUMBERS ASSIGNED SUCCESSFULLY!**\n\n"
        f"{numbers_display}\n"
        "⏳ WAITING FOR OTPS ON ALL 3 LINES..........\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"{DEV_SIGNATURE}"
    )

    sent_msg = await context.bot.send_message(
        chat_id=chat_id,
        text=msg_text,
        parse_mode="Markdown",
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )

    for target_num in allocated_numbers:
        asyncio.create_task(
            auto_sync_otp_task_for_number(
                context=context,
                chat_id=chat_id,
                message_id=sent_msg.message_id,
                panel_id=panel_id,
                service_name=service_name,
                target_number=target_num,
                selected_range=selected_range,
                range_type=range_type,
            )
        )

async def auto_sync_otp_task_for_number(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    message_id: int,
    panel_id: str,
    service_name: str,
    target_number: str,
    selected_range: str,
    range_type: str,
):
    formatted_num = f"+{target_number}"
    poll_count = 0
    max_polls = 360
    config = PANEL_CONFIG.get(panel_id, PANEL_CONFIG["panel1"])
    _, flag_emoji, _ = get_country_info(formatted_num)

    async with httpx.AsyncClient(timeout=8.0) as client:
        while poll_count < max_polls:
            await asyncio.sleep(random.uniform(2.0, 3.0))
            poll_count += 1

            current_tasks = ACTIVE_SYNC_TASKS.get(chat_id)
            if not current_tasks or target_number not in current_tasks:
                break

            pure_code, full_sms, found_panel = None, None, config["name"]
            
            pure_code, full_sms, found_panel = await check_cr_api_for_otp(client, target_number, service_name)
            
            if not pure_code and panel_id != "premium":
                try:
                    response = await client.get(config["get_sms_url"], headers=config["headers"], timeout=5.0)
                    if response.status_code == 200:
                        res_data = safe_json_parse(response.text) or {}
                        otp_list = res_data.get("data", {}).get("otps", []) or res_data.get("otps", []) or res_data.get("data", [])
                        if isinstance(otp_list, list):
                            matched_otps = [
                                item for item in otp_list
                                if str(item.get("number", "")).replace("+", "") == target_number or target_number in str(item.get("number", ""))
                            ]
                            if matched_otps:
                                latest_otp = matched_otps[-1]
                                full_sms = latest_otp.get("sms") or latest_otp.get("message") or latest_otp.get("otp", "No text received")
                                pure_code = extract_pure_code(latest_otp.get("otp") or full_sms)
                                found_panel = config["name"]
                except Exception:
                    pass

            if not pure_code:
                for alt_p_key, alt_config in PANEL_CONFIG.items():
                    if alt_p_key == panel_id:
                        continue
                    try:
                        alt_res = await client.get(alt_config["get_sms_url"], headers=alt_config["headers"], timeout=4.0)
                        if alt_res.status_code == 200:
                            alt_data = safe_json_parse(alt_res.text) or {}
                            alt_list = alt_data.get("data", {}).get("otps", []) or alt_data.get("otps", []) or alt_data.get("data", [])
                            if isinstance(alt_list, list):
                                alt_matched = [
                                    item for item in alt_list
                                    if str(item.get("number", "")).replace("+", "") == target_number or target_number in str(item.get("number", ""))
                                ]
                                if alt_matched:
                                    latest_otp = alt_matched[-1]
                                    full_sms = latest_otp.get("sms") or latest_otp.get("message") or latest_otp.get("otp", "No text received")
                                    pure_code = extract_pure_code(latest_otp.get("otp") or full_sms)
                                    found_panel = alt_config["name"]
                                    break
                    except Exception:
                        continue

            if pure_code:
                try:
                    chat_member = await context.bot.get_chat(chat_id)
                    db_add_otp_reward(chat_id, OTP_REWARD, username=chat_member.username, full_name=chat_member.full_name)
                except Exception:
                    db_add_otp_reward(chat_id, OTP_REWARD)
                
                with get_db() as db:
                    cur = db.cursor()
                    cur.execute("SELECT balance FROM users WHERE user_id = ?", (chat_id,))
                    row = cur.fetchone()
                    current_bal = row[0] if row else 0.0

                matched_srv_name = service_name if service_name in SERVICE_ICONS else "Facebook"
                await send_group_styled_otp(context, found_panel, matched_srv_name, target_number, pure_code, full_sms)

                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=(
                            f"{flag_emoji} ☎️ OTP RECEIVED ON {formatted_num}\n\n"
                            f"🗝 OTP : `{pure_code}`\n"
                            f"💰 Earned: +${OTP_REWARD:.4f}\n\n"
                            f"💲 Total Balance: ${current_bal:.4f}\n\n"
                            f"{DEV_SIGNATURE}"
                        ),
                        parse_mode="Markdown",
                        disable_web_page_preview=True,
                    )
                except BadRequest:
                    pass

                break

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_get_or_create_user(user.id, user.username, user.full_name)

    text = (
        f"👋 **Welcome, {user.first_name}!**\n\n"
        "⚡ **Earn money per OTP auto-verified!**\n"
        f"💰 **Rate:** `{OTP_REWARD:.2f} BDT / OTP`\n"
        f"💳 **Min Withdrawal:** `{MIN_WITHDRAW:.2f} BDT` (Bkash/Nagad/Binance)\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"{DEV_SIGNATURE}"
    )
    await update.message.reply_text(
        text,
        reply_markup=get_main_reply_keyboard(user.id, user.username),
        parse_mode="Markdown",
    )

async def getnumber_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_panels_menu(update, context)

async def send_premium_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_db() as db:
        cur = db.cursor()
        cur.execute("SELECT service, COUNT(*) FROM premium_numbers WHERE status = 'available' GROUP BY service")
        available_services = cur.fetchall()

    keyboard = []
    for srv, count in available_services:
        icon = SERVICE_ICONS.get(srv, "💎")
        keyboard.append([
            InlineKeyboardButton(f"{icon} {srv} ({count})", callback_data=f"prem_buy_{srv}")
        ])

    keyboard.append([InlineKeyboardButton("🔙 « Main Menu", callback_data="open_panels")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    total_avail = sum([c for _, c in available_services])
    text = (
        "💎 **PREMIUM STRONG NUMBER PORTAL**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 **Available Exclusive Lines:** `{total_avail}`\n\n"
        "⚡ Select your desired service below:\n\n"
        f"{DEV_SIGNATURE}"
    )
    if update.callback_query:
        await update.callback_query.answer()
        try:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except BadRequest:
            pass
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def buy_premium_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    service_name = query.data.replace("prem_buy_", "")
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    assigned_numbers = db_get_available_premium_numbers(user_id, service_name, count=3)
    if not assigned_numbers:
        await query.answer("⚠️ No Premium Strong Numbers available for this service right now.", show_alert=True)
        keyboard = [[InlineKeyboardButton("🔙 « Back", callback_data="premium_menu")]]
        await query.edit_message_text(
            "⚠️ **No Premium Strong Numbers available for this service right now.**\nAdmin will upload new lines shortly.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )
        return

    ACTIVE_SYNC_TASKS[chat_id] = [str(n).replace("+", "").strip() for n in assigned_numbers]

    await query.answer(f"⏳ Allocating 3 Premium Strong lines...", show_alert=False)

    keyboard = [
        [
            InlineKeyboardButton("🎲 Change Numbers", callback_data=f"prem_buy_{service_name}"),
            InlineKeyboardButton("🌐 Change Service", callback_data="premium_menu"),
        ],
        [InlineKeyboardButton("🚀 OTP Group ↗", url=OTP_GROUP_LINK)],
        [InlineKeyboardButton("🔙 « Main Menu", callback_data="open_panels")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    numbers_display = ""
    for idx, num in enumerate(assigned_numbers, 1):
        formatted_num = f"+{str(num).replace('+', '').strip()}"
        country_name, flag_emoji, prefix_code = get_country_info(formatted_num)
        numbers_display += f"{idx}️⃣ `{formatted_num}` ({prefix_code} {country_name} {flag_emoji})\n"

    msg_text = (
        f"💎 **3 PREMIUM NUMBERS ASSIGNED!**\n\n"
        f"{numbers_display}\n"
        "⏳ WAITING FOR OTPS ON ALL 3 LINES..........\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"{DEV_SIGNATURE}"
    )

    edited_msg = await query.edit_message_text(
        msg_text,
        parse_mode="Markdown",
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )

    for num in assigned_numbers:
        clean_num = str(num).replace("+", "").strip()
        asyncio.create_task(
            auto_sync_otp_task_for_number(
                context=context,
                chat_id=chat_id,
                message_id=edited_msg.message_id,
                panel_id="premium",
                service_name=service_name,
                target_number=clean_num,
                selected_range="CRRoute",
                range_type="hit",
            )
        )

async def balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u_data = db_get_or_create_user(user.id, user.username, user.full_name)
    balance = u_data[3]

    await update.message.reply_text(
        "💰 **Your Balance Details**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 **Available Balance:** `{balance:.2f} BDT`\n"
        f"🎁 **Rate Per OTP:** `{OTP_REWARD:.2f} BDT`\n"
        f"💳 **Minimum Withdrawal:** `{MIN_WITHDRAW:.2f} BDT`\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"{DEV_SIGNATURE}",
        parse_mode="Markdown",
    )

async def myprofile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u_data = db_get_or_create_user(user.id, user.username, user.full_name)
    balance = u_data[3]
    total_otp = u_data[4]

    await update.message.reply_text(
        "👤 **User Account Profile**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"👤 **Name:** `{user.full_name}`\n"
        f"🌐 **Username:** @{user.username if user.username else 'N/A'}\n"
        f"💰 **Available Balance:** `{balance:.2f} BDT`\n"
        f"📥 **Total OTPs Received:** `{total_otp}`\n"
        f"🎁 **Earning Rate:** `{OTP_REWARD:.2f} BDT / OTP`\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"{DEV_SIGNATURE}",
        parse_mode="Markdown",
    )

async def supportadmin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💬 Direct Message Admin", url=ADMIN_DIRECT_URL)],
        [InlineKeyboardButton("🚀 OTP Group ↗", url=OTP_GROUP_LINK)],
    ]
    await update.message.reply_text(
        "☎️ **Need Assistance?**\n\n"
        "Tap the buttons below to directly message the admin:\n\n"
        f"{DEV_SIGNATURE}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id, user.username):
        await update.message.reply_text("⛔ **Access Denied:** Admin only area.")
        return

    with get_db() as db:
        cur = db.cursor()
        cur.execute("SELECT COUNT(*), SUM(balance), SUM(total_otp) FROM users")
        total_users, total_bal, total_otps = cur.fetchone()

        cur.execute("SELECT COUNT(*) FROM premium_numbers WHERE status = 'available'")
        avail_prem = cur.fetchone()[0]

        cur.execute("SELECT user_id FROM admins")
        admins_list = cur.fetchall()

    admin_tags = ", ".join([f"`{a[0]}`" for a in admins_list])

    admin_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📂 Upload Premium .TXT", callback_data="admin_upload_premium"),
            InlineKeyboardButton("🗑 Clear Premium", callback_data="admin_clear_premium"),
        ],
        [
            InlineKeyboardButton("💰 Edit User Balance", callback_data="admin_edit_balance"),
            InlineKeyboardButton("🔢 Edit User OTPs", callback_data="admin_edit_otps"),
        ],
        [
            InlineKeyboardButton("📢 Send Broadcast", callback_data="admin_start_broadcast"),
            InlineKeyboardButton("🔄 Refresh Stats", callback_data="admin_refresh_stats"),
        ]
    ])

    admin_msg = (
        "👑 **PRIME ADMIN CONTROL PANEL**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 **Prime Admin:** @{PRIME_ADMIN_USERNAME} (`{PRIME_ADMIN_ID}`)\n"
        f"👥 **Total Users:** `{total_users or 0}`\n"
        f"💰 **Total Balances:** `{total_bal or 0.0:.2f} BDT`\n"
        f"⚡ **Total OTPs Served:** `{total_otps or 0}`\n"
        f"💎 **Available Premium Strong Lines:** `{avail_prem}`\n"
        f"🛡 **Authorized Admins:** {admin_tags}\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"{DEV_SIGNATURE}"
    )
    if update.callback_query:
        await update.callback_query.answer()
        try:
            await update.callback_query.edit_message_text(
                admin_msg, reply_markup=admin_markup, parse_mode="Markdown"
            )
        except BadRequest:
            pass
    else:
        await update.message.reply_text(
            admin_msg, reply_markup=admin_markup, parse_mode="Markdown"
        )

async def setbalance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_prime_admin(user.id, user.username):
        await update.message.reply_text("⛔ Only Prime Admin can edit user balances.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: `/setbalance <User_ID> <Amount>`", parse_mode="Markdown")
        return

    try:
        target_uid = int(context.args[0])
        new_bal = float(context.args[1])
        db_set_user_balance(target_uid, new_bal)
        await update.message.reply_text(f"✅ **Balance Updated!**\nUser `{target_uid}` balance set to `{new_bal:.2f} BDT`.", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID or Amount format.")

async def setotp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_prime_admin(user.id, user.username):
        await update.message.reply_text("⛔ Only Prime Admin can edit OTP values.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: `/setotp <User_ID> <Count>`", parse_mode="Markdown")
        return

    try:
        target_uid = int(context.args[0])
        new_otps = int(context.args[1])
        db_set_user_otp_count(target_uid, new_otps)
        await update.message.reply_text(f"✅ **OTP Count Updated!**\nUser `{target_uid}` total OTPs set to `{new_otps}`.", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID or Count format.")

async def add_admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_prime_admin(user.id, user.username):
        await update.message.reply_text("⛔ Only Prime Admin can promote new admins.")
        return

    if not context.args:
        await update.message.reply_text("Usage: `/addadmin <User_ID>`", parse_mode="Markdown")
        return

    try:
        new_admin_id = int(context.args[0])
        with get_db() as db:
            db.execute(
                "INSERT OR IGNORE INTO admins (user_id, added_by) VALUES (?, ?)",
                (new_admin_id, PRIME_ADMIN_ID),
            )
            db.commit()
            await set_admin_commands_for_chat(context.bot, new_admin_id)
        await update.message.reply_text(f"✅ User `{new_admin_id}` is now registered as an Admin.", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID.")

async def remove_admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_prime_admin(user.id, user.username):
        await update.message.reply_text("⛔ Only Prime Admin can demote admins.")
        return

    if not context.args:
        await update.message.reply_text("Usage: `/removeadmin <User_ID>`", parse_mode="Markdown")
        return

    try:
        target_id = int(context.args[0])
        if target_id == PRIME_ADMIN_ID:
            await update.message.reply_text("⛔ Cannot remove Prime Super Admin.")
            return

        with get_db() as db:
            db.execute("DELETE FROM admins WHERE user_id = ?", (target_id,))
            db.commit()
        await update.message.reply_text(f"✅ User `{target_id}` was removed from Admins.", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID.")

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id, user.username):
        await update.message.reply_text("⛔ **Access Denied:** Admin only area.")
        return

    if not context.args:
        USER_STATES[user.id] = {"state": "AWAITING_BROADCAST_MSG"}
        await update.message.reply_text("📢 **Broadcast Mode Active**\n\nPlease send the announcement message:", parse_mode="Markdown")
        return

    broadcast_text = " ".join(context.args)
    await run_broadcast(context, update.effective_chat.id, broadcast_text)

async def run_broadcast(context: ContextTypes.DEFAULT_TYPE, admin_chat_id: int, broadcast_text: str):
    with get_db() as db:
        cur = db.cursor()
        cur.execute("SELECT user_id FROM users")
        users = cur.fetchall()

    sent, failed = 0, 0
    await context.bot.send_message(chat_id=admin_chat_id, text=f"📢 **Broadcasting message to {len(users)} users...**")

    for (uid,) in users:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"📢 **BROADCAST UPDATE**\n━━━━━━━━━━━━━━━━━━━━━\n{broadcast_text}\n━━━━━━━━━━━━━━━━━━━━━\n{DEV_SIGNATURE}",
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    await context.bot.send_message(
        chat_id=admin_chat_id,
        text=f"✅ **Broadcast Completed!**\n\n• Successfully Sent: `{sent}`\n• Failed: `{failed}`",
        parse_mode="Markdown",
    )

async def send_panels_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚡ Kop Engine 1", callback_data="services_panel1")],
        [InlineKeyboardButton("⚡ Kop Engine 2", callback_data="services_panel2")],
        [InlineKeyboardButton("⚡ Kop Engine 3", callback_data="services_panel3")],
        [InlineKeyboardButton("💎 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐒𝐓𝐑𝐎𝐍𝐆 𝐍𝐔𝐌𝐁𝐄𝐑𝐒", callback_data="premium_menu")],
        [InlineKeyboardButton("👥 𝐉𝐎𝐈𝐍 𝐎𝐓𝐏 𝐆𝐑𝐎𝐔𝐏 ↗", url=OTP_GROUP_LINK)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"🔥 *Select your desired SMS Server / Panel below:*\n\n{DEV_SIGNATURE}"

    if update.callback_query:
        await update.callback_query.answer()
        try:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except BadRequest:
            pass
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    panel_id = query.data.replace("services_", "")
    config = PANEL_CONFIG.get(panel_id, PANEL_CONFIG["panel1"])

    keyboard = [
        [InlineKeyboardButton("📘 Facebook", callback_data=f"range_type_{panel_id}_Facebook")],
        [InlineKeyboardButton("💬 WhatsApp", callback_data=f"range_type_{panel_id}_WhatsApp")],
        [InlineKeyboardButton("📸 Instagram", callback_data=f"range_type_{panel_id}_Instagram")],
        [InlineKeyboardButton("🔙 « Back to Panels", callback_data="open_panels")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await query.edit_message_text(
            f"🛠 **{config['name']}**\n\n🎯 *Select your desired service below:*\n\n{DEV_SIGNATURE}",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
    except BadRequest:
        pass

async def show_range_type_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    panel_id = parts[2]
    service_name = parts[3]

    keyboard = [
        [InlineKeyboardButton("🔥 High Hit Ranges", callback_data=f"ranges_{panel_id}_{service_name}_hit")],
        [InlineKeyboardButton("⚡ Most Recent Ranges", callback_data=f"ranges_{panel_id}_{service_name}_recent")],
        [InlineKeyboardButton("🔙 « Back to Services", callback_data=f"services_{panel_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await query.edit_message_text(
            f"🎯 **{service_name}**\n\n👇 *Choose your preferred range selection type:*\n\n{DEV_SIGNATURE}",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
    except BadRequest:
        pass

async def show_ranges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🔄 Real-time fetching live routes...")

    parts = query.data.split("_")
    panel_id = parts[1]
    service_name = parts[2]
    range_type = parts[3] if len(parts) > 3 else "hit"
    config = PANEL_CONFIG.get(panel_id, PANEL_CONFIG["panel1"])

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            matched_ranges_with_hits = await fetch_optimized_ranges(client, config, service_name, mode=range_type)

        if not matched_ranges_with_hits:
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh Ranges", callback_data=f"ranges_{panel_id}_{service_name}_{range_type}")],
                [InlineKeyboardButton("🔙 « Back", callback_data=f"range_type_{panel_id}_{service_name}")]
            ]
            try:
                await query.edit_message_text(
                    f"⚠️ *No active routes found for {service_name} right now.*\n\n{DEV_SIGNATURE}",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown",
                )
            except BadRequest:
                pass
            return

        keyboard = []
        for r, hits in matched_ranges_with_hits:
            country_name, flag_emoji, _ = get_country_info(r)
            hit_badge = f"🔥 {hits}+ Hits" if range_type == "hit" else "⚡ Recent"
            starred_r = format_range_as_stars(r)
            btn_text = f"{flag_emoji} {starred_r} ┃ {country_name} [{hit_badge}]"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"buy_{panel_id}_{service_name}_{r}_{range_type}")])

        keyboard.append([InlineKeyboardButton("🔄 Refresh Ranges", callback_data=f"ranges_{panel_id}_{service_name}_{range_type}")])
        keyboard.append([InlineKeyboardButton("🔙 « Select Range Type", callback_data=f"range_type_{panel_id}_{service_name}")])

        now_str = datetime.now().strftime("%I:%M:%S %p")
        try:
            await query.edit_message_text(
                f"🛠 **{config['name']} ┋ {service_name}**\n"
                f"📂 *Mode: {'High Hit' if range_type=='hit' else 'Most Recent'}*\n"
                f"🕒 *Last Refreshed: {now_str}*\n\n"
                f"{DEV_SIGNATURE}",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )
        except BadRequest:
            pass

    except Exception as e:
        keyboard = [
            [InlineKeyboardButton("🔄 Retry Refresh", callback_data=f"ranges_{panel_id}_{service_name}_{range_type}")],
            [InlineKeyboardButton("🔙 « Back", callback_data=f"range_type_{panel_id}_{service_name}")]
        ]
        try:
            await query.edit_message_text(
                f"❌ *Connection Error:* `{str(e)}`\n\n{DEV_SIGNATURE}",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )
        except BadRequest:
            pass

async def buy_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    parts = query.data.split("_")
    panel_id = parts[1]
    service_name = parts[2]
    selected_range = parts[3]
    range_type = parts[4] if len(parts) > 4 else "hit"
    config = PANEL_CONFIG.get(panel_id, PANEL_CONFIG["panel1"])
    country_name, flag_emoji, prefix_code = get_country_info(selected_range)

    await query.answer(f"⏳ Allocating 3 {country_name} lines...", show_alert=False)

    clean_base = selected_range.replace("***", "").replace("XXX", "").strip()
    allocated_numbers = []

    async with httpx.AsyncClient(timeout=8.0) as client:
        for _ in range(3):
            variant_range = clean_base + str(random.randint(0, 999)).zfill(3)
            clean_for_api = variant_range + "XXX"

            if config["panel_type"] == "zenex":
                payload = {"range": clean_for_api, "is_national": False, "remove_plus": False}
            elif config["panel_type"] == "voltx":
                clean_range_for_rid = clean_for_api.replace("XXX", "").replace("xx", "")
                payload = {"rid": clean_range_for_rid}
            elif config["panel_type"] == "fastx":
                payload = {"range": clean_for_api}
            else:
                payload = {"range": clean_for_api}

            try:
                response = await client.post(config["get_num_url"], headers=config["headers"], json=payload)
                if response.status_code == 200:
                    res_data = safe_json_parse(response.text) or {}
                    number_data = res_data.get("data", {})
                    phone_number = number_data.get("full_number") or number_data.get("number")
                    if phone_number:
                        clean_num = str(phone_number).replace("+", "")
                        if clean_num not in allocated_numbers:
                            allocated_numbers.append(clean_num)
            except Exception:
                pass

        if not allocated_numbers:
            for _ in range(3):
                fallback_api_range = selected_range.replace("***", "XXX")
                if config["panel_type"] == "zenex":
                    payload = {"range": fallback_api_range, "is_national": False, "remove_plus": False}
                elif config["panel_type"] == "voltx":
                    payload = {"rid": fallback_api_range.replace("XXX", "")}
                else:
                    payload = {"range": fallback_api_range}

                try:
                    response = await client.post(config["get_num_url"], headers=config["headers"], json=payload)
                    if response.status_code == 200:
                        res_data = safe_json_parse(response.text) or {}
                        number_data = res_data.get("data", {})
                        phone_number = number_data.get("full_number") or number_data.get("number")
                        if phone_number:
                            clean_num = str(phone_number).replace("+", "")
                            if clean_num not in allocated_numbers:
                                allocated_numbers.append(clean_num)
                except Exception:
                    pass

    if allocated_numbers:
        ACTIVE_SYNC_TASKS[chat_id] = allocated_numbers

        keyboard = [
            [
                InlineKeyboardButton("🎲 Change Numbers", callback_data=f"buy_{panel_id}_{service_name}_{selected_range}_{range_type}"),
                InlineKeyboardButton("🌐 Change Range", callback_data=f"ranges_{panel_id}_{service_name}_{range_type}"),
            ],
            [InlineKeyboardButton("🚀 OTP Group ↗", url=OTP_GROUP_LINK)],
            [InlineKeyboardButton("🔙 « Select Panels", callback_data="open_panels")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        numbers_display = ""
        for idx, num in enumerate(allocated_numbers, 1):
            formatted_num = f"+{num}"
            c_name, c_flag, c_prefix = get_country_info(formatted_num)
            numbers_display += f"{idx}️⃣ `{formatted_num}` ({c_prefix} {c_name} {c_flag})\n"

        msg_text = (
            f"🎯 **3 NUMBERS ASSIGNED SUCCESSFULLY!**\n\n"
            f"{numbers_display}\n"
            "⏳ WAITING FOR OTPS ON ALL 3 LINES..........\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"{DEV_SIGNATURE}"
        )
        edited_msg = await query.edit_message_text(
            msg_text,
            parse_mode="Markdown",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )

        for clean_num in allocated_numbers:
            asyncio.create_task(
                auto_sync_otp_task_for_number(
                    context=context,
                    chat_id=chat_id,
                    message_id=edited_msg.message_id,
                    panel_id=panel_id,
                    service_name=service_name,
                    target_number=clean_num,
                    selected_range=selected_range,
                    range_type=range_type,
                )
            )
    else:
        keyboard = [
            [
                InlineKeyboardButton("🔄 Retry", callback_data=f"buy_{panel_id}_{service_name}_{selected_range}_{range_type}"),
                InlineKeyboardButton("🔙 « Back", callback_data=f"ranges_{panel_id}_{service_name}_{range_type}")
            ]
        ]
        await query.edit_message_text(f"⚠️ *Number Allotment Failed ❌*\n\n{DEV_SIGNATURE}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_document_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id, user.username):
        return

    doc = update.message.document
    if doc.file_name and doc.file_name.endswith(".txt"):
        file = await context.bot.get_file(doc.file_id)
        content_bytes = await file.download_as_bytearray()
        text_data = content_bytes.decode("utf-8", errors="ignore")
        lines = [line.strip() for line in text_data.splitlines() if line.strip()]

        USER_STATES[user.id] = {"state": "AWAITING_PREMIUM_SERVICE_CHOICE", "numbers_lines": lines}

        keyboard = [
            [InlineKeyboardButton("📘 Facebook", callback_data="upload_srv_Facebook"), InlineKeyboardButton("💬 WhatsApp", callback_data="upload_srv_WhatsApp")],
            [InlineKeyboardButton("📸 Instagram", callback_data="upload_srv_Instagram")],
        ]
        await update.message.reply_text(f"📂 File received with `{len(lines)}` lines.\n\n👇 Select service:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_upload_service_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not is_admin(user_id, query.from_user.username):
        return

    service_name = query.data.replace("upload_srv_", "")
    state_data = USER_STATES.get(user_id, {})
    lines = state_data.get("numbers_lines", [])
    USER_STATES.pop(user_id, None)

    added, skipped = db_add_premium_numbers_bulk(lines, service=service_name)
    await query.edit_message_text(f"💎 **Imported:** `{added}` | **Skipped:** `{skipped}`", parse_mode="Markdown")

async def handle_bottom_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    u_data = db_get_or_create_user(user.id, user.username, user.full_name)

    if text == "📱 Get Number":
        await send_panels_menu(update, context)
    elif text == "💎 Premium Strong Number":
        await send_premium_menu(update, context)
    elif text == "📊 Status":
        with get_db() as db:
            cur = db.cursor()
            cur.execute("SELECT COUNT(*), SUM(total_otp) FROM users")
            total_users, all_otps = cur.fetchone()
            cur.execute("SELECT COUNT(*) FROM premium_numbers WHERE status = 'available'")
            prem_avail = cur.fetchone()[0]

        await update.message.reply_text(
            "📊 **Server Status & Live Stats**\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 **Total Registered Users:** `{total_users or 0}`\n"
            f"⚡ **Total Successful OTPs:** `{all_otps or 0}`\n"
            f"💎 **Available Premium Stock:** `{prem_avail}`\n"
            f"🟢 **Kop Engine 1-3:** `Operational`\n"
            f"🟢 **Hadi Engine:** `Operational`\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"{DEV_SIGNATURE}",
            parse_mode="Markdown",
        )
    elif text == "💳 My Account":
        await myprofile_cmd(update, context)
    elif text == "💰 Withdraw":
        balance = u_data[3]
        if balance < MIN_WITHDRAW:
            await update.message.reply_text(
                f"⚠️ **Insufficient Balance!**\n\nYour balance is `{balance:.2f} BDT`.\nMinimum withdrawal limit is `{MIN_WITHDRAW:.2f} BDT`.",
                parse_mode="Markdown",
            )
            return

        keyboard = [
            [InlineKeyboardButton("📱 Bkash", callback_data="wd_select_Bkash"), InlineKeyboardButton("📱 Nagad", callback_data="wd_select_Nagad")],
            [InlineKeyboardButton("🟡 Binance Pay ID/USDT", callback_data="wd_select_Binance")]
        ]
        await update.message.reply_text(
            f"💰 **Withdrawal Gateway**\n\nAvailable Balance: `{balance:.2f} BDT`\nMinimum Limit: `{MIN_WITHDRAW:.2f} BDT`\n\nSelect payout method:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )
    elif text == "☎️ Support":
        await supportadmin_cmd(update, context)
    elif text == "👑 Admin Panel" and is_admin(user.id, user.username):
        await admin_panel(update, context)
    elif text == "📢 Broadcast" and is_admin(user.id, user.username):
        USER_STATES[user.id] = {"state": "AWAITING_BROADCAST_MSG"}
        await update.message.reply_text("📢 **Broadcast Mode Active**\n\nPlease send the announcement message:", parse_mode="Markdown")

    elif USER_STATES.get(user.id, {}).get("state") == "AWAITING_BROADCAST_MSG":
        if text.strip().lower() == "cancel":
            USER_STATES.pop(user.id, None)
            await update.message.reply_text("❌ Broadcast cancelled.")
            return
        USER_STATES.pop(user.id, None)
        await run_broadcast(context, update.effective_chat.id, text.strip())

    elif USER_STATES.get(user.id, {}).get("state") == "AWAITING_WD_DETAILS":
        method = USER_STATES[user.id]["method"]
        input_text = text.strip().split()
        if len(input_text) < 2:
            await update.message.reply_text("❌ **Invalid Format!** Use: `<Number/ID> <Amount>`")
            return
        acc_number = input_text[0]
        try:
            amount = float(input_text[1])
        except ValueError:
            await update.message.reply_text("❌ Invalid amount.")
            return

        balance = u_data[3]
        if amount < MIN_WITHDRAW or amount > balance:
            await update.message.reply_text(f"⚠️ Invalid amount. Check min limit ({MIN_WITHDRAW} BDT) or balance.")
            return

        db_deduct_balance(user.id, amount)
        USER_STATES.pop(user.id, None)
        req_id = f"WD{random.randint(10000, 99999)}"
        PENDING_WITHDRAWALS[req_id] = {"user_id": user.id, "amount": amount, "method": method, "account": acc_number}

        withdraw_msg = f"🚨 **NEW WITHDRAWAL REQUEST**\nUser Id: `{user.id}`\nAmount: `{amount} BDT`\nMethod: `{method}`\nAccount: `{acc_number}`"
        admin_markup = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve", callback_data=f"wd_app_{req_id}"), InlineKeyboardButton("❌ Decline", callback_data=f"wd_dec_{req_id}")]])

        with get_db() as db:
            cur = db.cursor()
            cur.execute("SELECT user_id FROM admins")
            for (adm_id,) in cur.fetchall():
                try:
                    await context.bot.send_message(chat_id=adm_id, text=withdraw_msg, reply_markup=admin_markup, parse_mode="Markdown")
                except Exception:
                    pass

        await update.message.reply_text("✅ **Withdrawal Request Submitted Successfully!** Please wait for admin approval.", parse_mode="Markdown")

async def handle_withdraw_method_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    method = query.data.replace("wd_select_", "")
    USER_STATES[query.from_user.id] = {"state": "AWAITING_WD_DETAILS", "method": method}
    await query.edit_message_text(f"💳 **Selected Method:** `{method}`\n\nSend: `<Number/ID> <Amount>`", parse_mode="Markdown")

async def handle_withdraw_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id, query.from_user.username):
        return
    action, req_id = query.data.split("_")[1], query.data.split("_")[2]
    req_data = PENDING_WITHDRAWALS.get(req_id)
    if not req_data:
        await query.edit_message_text(f"{query.message.text}\n\n⚠️ Already processed.", parse_mode="Markdown")
        return

    target_uid, amount, method, account = req_data["user_id"], req_data["amount"], req_data["method"], req_data["account"]
    PENDING_WITHDRAWALS.pop(req_id, None)

    if action == "app":
        try:
            await context.bot.send_message(chat_id=target_uid, text=f"🎉 **Withdrawal Approved!** `{amount} BDT` via `{method}` sent to `{account}`.", parse_mode="Markdown")
        except Exception:
            pass
        await query.edit_message_text(f"{query.message.text}\n\n✅ **APPROVED**", parse_mode="Markdown")
    else:
        db_refund_balance(target_uid, amount)
        try:
            await context.bot.send_message(chat_id=target_uid, text=f"❌ **Withdrawal Declined!** `{amount} BDT` refunded.", parse_mode="Markdown")
        except Exception:
            pass
        await query.edit_message_text(f"{query.message.text}\n\n❌ **DECLINED & REFUNDED**", parse_mode="Markdown")

async def admin_callback_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id, query.from_user.username):
        return

    if query.data == "admin_refresh_stats":
        await admin_panel(update, context)
    elif query.data == "admin_start_broadcast":
        USER_STATES[query.from_user.id] = {"state": "AWAITING_BROADCAST_MSG"}
        await query.edit_message_text("📢 **Broadcast Mode Active**\n\nSend announcement message:", parse_mode="Markdown")
    elif query.data == "admin_upload_premium":
        await query.edit_message_text("📂 **Drop your numbers file (`.txt`) directly into this chat.**", parse_mode="Markdown")
    elif query.data == "admin_clear_premium":
        with get_db() as db:
            db.execute("DELETE FROM premium_numbers")
            db.commit()
        await query.answer("🗑 All premium lines cleared!", show_alert=True)
        await admin_panel(update, context)

async def set_admin_commands_for_chat(bot, chat_id: int):
    admin_commands = [
        BotCommand("start", "Start bot"),
        BotCommand("admin", "Admin Control Panel"),
        BotCommand("broadcast", "Broadcast message"),
        BotCommand("setbalance", "Set user balance"),
        BotCommand("setotp", "Set user total OTPs"),
        BotCommand("addadmin", "Add sub-admin"),
        BotCommand("removeadmin", "Remove sub-admin"),
    ]
    try:
        await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=chat_id))
    except Exception:
        pass

async def on_startup(app):
    await app.bot.set_my_commands([BotCommand("start", "Start bot")], scope=BotCommandScopeDefault())
    await set_admin_commands_for_chat(app.bot, PRIME_ADMIN_ID)
    with get_db() as db:
        cur = db.cursor()
        cur.execute("SELECT user_id FROM admins")
        for (adm_id,) in cur.fetchall():
            await set_admin_commands_for_chat(app.bot, adm_id)

    asyncio.create_task(global_console_broadcaster(app))
    asyncio.create_task(sync_ranges_every_minute())

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).post_init(on_startup).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("getnumber", getnumber_cmd))
    app.add_handler(CommandHandler("balance", balance_cmd))
    app.add_handler(CommandHandler("myprofile", myprofile_cmd))
    app.add_handler(CommandHandler("supportadmin", supportadmin_cmd))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("broadcast", broadcast_cmd))
    app.add_handler(CommandHandler("setbalance", setbalance_cmd))
    app.add_handler(CommandHandler("setotp", setotp_cmd))
    app.add_handler(CommandHandler("addadmin", add_admin_cmd))
    app.add_handler(CommandHandler("removeadmin", remove_admin_cmd))

    app.add_handler(CallbackQueryHandler(send_panels_menu, pattern="^open_panels$"))
    app.add_handler(CallbackQueryHandler(send_premium_menu, pattern="^premium_menu$"))
    app.add_handler(CallbackQueryHandler(buy_premium_number, pattern="^prem_buy_"))
    app.add_handler(CallbackQueryHandler(show_services, pattern="^services_"))
    app.add_handler(CallbackQueryHandler(show_range_type_menu, pattern="^range_type_"))
    app.add_handler(CallbackQueryHandler(show_ranges, pattern="^ranges_"))
    app.add_handler(CallbackQueryHandler(buy_number, pattern="^buy_"))
    app.add_handler(CallbackQueryHandler(handle_withdraw_method_selection, pattern="^wd_select_"))
    app.add_handler(CallbackQueryHandler(handle_withdraw_decision, pattern="^wd_(app|dec)_"))
    app.add_handler(CallbackQueryHandler(admin_callback_actions, pattern="^admin_(refresh_stats|start_broadcast|upload_premium|clear_premium)$"))
    app.add_handler(CallbackQueryHandler(handle_upload_service_choice, pattern="^upload_srv_"))

    app.add_handler(MessageHandler(filters.Document.ALL & ~filters.COMMAND, handle_document_upload))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bottom_menu))

    print(f"⚡ Bot Online. Automatic number re-allocation on OTP receipt removed.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
