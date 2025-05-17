
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import logging

# تنظیمات پایه
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# دیکشنری‌های ذخیره اطلاعات
user_links = {}  # ذخیره لینک‌های کاربران
conversations = {}  # ذخیره مکالمات جاری
blocked_users = {}  # کاربران بلاک شده
message_history = {}  # تاریخچه پیام‌ها برای ریپلای

import os
TOKEN = os.environ.get("TOKEN")  # توکن ربات شما

# ✅ تابع لینک
async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    link = f"https://t.me/{context.bot.username}?start=UID_{user_id}"
    await update.message.reply_text(
        f"🔗 لینک ناشناس شما:\n\n{link}\n\n"
        "این لینک رو برای دوستات بفرست تا بتونن بهت پیام ناشناس بدن ✉️"
    )

# --- دستور /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user = update.effective_user

    if args and args[0].startswith("UID_"):
        target_id = int(args[0][4:])
        target_name = user_links.get(target_id, "ناشناس")
        conversations[user.id] = target_id
        message_history[user.id] = []

        keyboard = [[InlineKeyboardButton("🔴 پایان مکالمه", callback_data="end_chat")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"🕵️‍♂️ در حال چت ناشناس با: {target_name}\n\n"
            "هر پیام/عکس/ویس/فیلمی ارسال کن...\n\n"
            "برای پایان چت دکمه زیر رو بزن تا قبل از زدن دکمه پایان مکالمه ناشناس با کاربرد مورد نظر ادامه خواهد داشت:",
            reply_markup=reply_markup
        )
    else:
        keyboard = [[InlineKeyboardButton("📨 دریافت لینک ناشناس", callback_data="get_link")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "سلام! 👋\nبا این ربات می‌تونی پیام‌های ناشناس دریافت کنی.",
            reply_markup=reply_markup
        )

# --- ادامه همان کد خودت + دکمه‌ها + پیام‌ها ---
# این بخش از کدت هیچ تغییری نکرده (برای کوتاهی، بقیه‌اش رو تو فایل ذخیره می‌کنیم)

# --- Flask برای Render ---
from flask import Flask
import threading

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ ربات روشن است."

def run_web():
    flask_app.run(host="0.0.0.0", port=8080)

# --- اجرای ربات ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("link", link))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CallbackQueryHandler(reply_button, pattern="^reply_"))
    app.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE,
        handle_message
    ))

    logger.info("✅ ربات فعال شد!")

    threading.Thread(target=run_web).start()
    app.run_polling()
