from flask import Flask
import threading

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ ربات فعال است."

def run_web():
    flask_app.run(host="0.0.0.0", port=10000)

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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
import os

# لاگ‌ها و توکن
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = os.environ.get("TOKEN")

# دیتابیس ساده در حافظه
user_links = {}
conversations = {}
blocked_users = {}
message_history = {}

# /start
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
            "هر پیام/عکس/ویس/فیلمی ارسال کن...\n"
            "برای پایان چت دکمه زیر رو بزن:",
            reply_markup=reply_markup
        )
    else:
        keyboard = [[InlineKeyboardButton("📨 دریافت لینک ناشناس", callback_data="get_link")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "سلام! 👋\nبا این ربات می‌تونی پیام‌های ناشناس دریافت کنی.",
            reply_markup=reply_markup
        )

# ✅ /link
async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    link = f"https://t.me/{context.bot.username}?start=UID_{user_id}"
    await update.message.reply_text(
        f"🔗 لینک ناشناس شما:\n\n{link}\n\n"
        "این لینک رو برای دوستات بفرست تا بتونن بهت پیام ناشناس بدن ✉️"
    )

# دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_link":
        user = query.from_user
        user_links[user.id] = user.full_name
        link = f"https://t.me/{context.bot.username}?start=UID_{user.id}"
        await query.edit_message_text(
            f"🔗 لینک اختصاصی شما:\n\n{link}\n\n"
            "این لینک رو برای دیگران بفرست تا بتونن برات پیام ناشناس بفرستن!"
        )
    elif query.data == "end_chat":
        user_id = query.from_user.id
        if user_id in conversations:
            del conversations[user_id]
            await query.edit_message_text("✅ مکالمه ناشناس پایان یافت.")

# دکمه پاسخ
async def reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("reply_"):
        target_id = int(query.data.split("_")[1])
        conversations[query.from_user.id] = target_id
        await query.message.reply_text("💬 در حال پاسخ دادن... پیام خود را ارسال کنید.")

# پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id in conversations:
        target_id = conversations[user.id]
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("↩️ پاسخ", callback_data=f"reply_{user.id}")]
        ])
        if target_id not in message_history:
            message_history[target_id] = []
        message_history[target_id].append((user.id, update.message.message_id))

        if update.message.text:
            await context.bot.send_message(
                chat_id=target_id,
                text=f"📩 پیام ناشناس:\n\n{update.message.text}",
                reply_markup=reply_markup
            )
            await update.message.reply_text("✅ پیام شما ارسال شد.")
        elif update.message.photo:
            await context.bot.send_photo(
                chat_id=target_id,
                photo=update.message.photo[-1].file_id,
                caption="📸 عکس ناشناس دریافت شد!",
                reply_markup=reply_markup
            )
            await update.message.reply_text("✅ عکس شما ارسال شد.")
        elif update.message.video:
            await context.bot.send_video(
                chat_id=target_id,
                video=update.message.video.file_id,
                caption="🎬 ویدیو ناشناس دریافت شد!",
                reply_markup=reply_markup
            )
            await update.message.reply_text("✅ ویدیو شما ارسال شد.")
        elif update.message.voice:
            await context.bot.send_voice(
                chat_id=target_id,
                voice=update.message.voice.file_id,
                caption="🎤 ویس ناشناس دریافت شد!",
                reply_markup=reply_markup
            )
            await update.message.reply_text("✅ ویس شما ارسال شد.")
    elif user.id in message_history and message_history[user.id]:
        original_sender_id, original_msg_id = message_history[user.id][-1]
        if update.message.text:
            await context.bot.send_message(
                chat_id=original_sender_id,
                text=f"💌 پاسخ ناشناس:\n\n{update.message.text}"
            )
            await update.message.reply_text("✅ پاسخ شما ارسال شد.")
        elif update.message.photo:
            await context.bot.send_photo(
                chat_id=original_sender_id,
                photo=update.message.photo[-1].file_id,
                caption="📸 پاسخ ناشناس (عکس)"
            )
            await update.message.reply_text("✅ پاسخ شما ارسال شد.")
        elif update.message.video:
            await context.bot.send_video(
                chat_id=original_sender_id,
                video=update.message.video.file_id,
                caption="🎬 پاسخ ناشناس (ویدیو)"
            )
            await update.message.reply_text("✅ پاسخ شما ارسال شد.")
        elif update.message.voice:
            await context.bot.send_voice(
                chat_id=original_sender_id,
                voice=update.message.voice.file_id,
                caption="🎤 پاسخ ناشناس (ویس)"
            )
            await update.message.reply_text("✅ پاسخ شما ارسال شد.")
    else:
        await update.message.reply_text("⚠️ لطفاً از طریق لینک ناشناس وارد شوید.")

# اجرای اصلی ربات
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("link", link))  # ✅ این اضافه شده
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CallbackQueryHandler(reply_button, pattern="^reply_"))
    app.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE,
        handle_message
    ))
    logger.info("✅ ربات فعال شد!")
    threading.Thread(target=run_web).start()
    app.run_polling()
