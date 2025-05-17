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

TOKEN = "7494780039:AAFMIPf6xDp732C1ABKhxxYv9K79CeG2TuY"  # توکن ربات شما

# --- دستور /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user = update.effective_user

    if args and args[0].startswith("UID_"):
        target_id = int(args[0][4:])
        target_name = user_links.get(target_id, "ناشناس")

        # ذخیره ارتباط بین کاربران
        conversations[user.id] = target_id
        message_history[user.id] = []

        keyboard = [
            [InlineKeyboardButton("🔴 پایان مکالمه", callback_data="end_chat")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"🕵️‍♂️ در حال چت ناشناس با: {target_name}\n\n"
            "هر پیام/عکس/ویس/فیلمی ارسال کن...\n\n"
            "برای پایان چت دکمه زیر رو بزن تا قبل از زدن دکمه پایان مکالمه ناشناس با کاربرد مورد نظر ادامه خواهد داشت:",
            reply_markup=reply_markup
        )
    else:
        keyboard = [
            [InlineKeyboardButton("📨 دریافت لینک ناشناس", callback_data="get_link")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "سلام! 👋\nبا این ربات می‌تونی پیام‌های ناشناس دریافت کنی.",
            reply_markup=reply_markup
        )

# --- دکمه دریافت لینک ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_link":
        user = query.from_user
        user_links[user.id] = user.full_name
        link = f"https://t.me/SenderChtBot?start=UID_{user.id}"
        await query.edit_message_text(
            f"🔗 لینک اختصاصی شما:\n\n{link}\n\n"
            "این لینک رو برای دیگران بفرست تا بتونن برات پیام ناشناس بفرستن!",
            reply_markup=None
        )
    elif query.data == "end_chat":
        user_id = query.from_user.id
        if user_id in conversations:
            del conversations[user_id]
            await query.edit_message_text(
                "✅ مکالمه ناشناس با موفقیت پایان یافت.",
                reply_markup=None
            )

# --- پردازش تمام انواع پیام‌ها ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.message.chat_id

    # اگر کاربر در حال مکالمه است
    if user.id in conversations:
        target_id = conversations[user.id]
        
        # ایجاد دکمه پاسخ
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("↩️ پاسخ", callback_data=f"reply_{user.id}")]
        ])

        # ذخیره تاریخچه پیام
        if target_id not in message_history:
            message_history[target_id] = []
        message_history[target_id].append((user.id, update.message.message_id))

        # ارسال متن
        if update.message.text:
            await context.bot.send_message(
                chat_id=target_id,
                text=f"📩 پیام ناشناس:\n\n{update.message.text}",
                reply_markup=reply_markup
            )
            await update.message.reply_text("✅ پیام شما ارسال شد.")

        # ارسال عکس
        elif update.message.photo:
            await context.bot.send_photo(
                chat_id=target_id,
                photo=update.message.photo[-1].file_id,
                caption="📸 عکس ناشناس دریافت شد!",
                reply_markup=reply_markup
            )
            await update.message.reply_text("✅ عکس شما ارسال شد.")

        # ارسال ویدیو
        elif update.message.video:
            await context.bot.send_video(
                chat_id=target_id,
                video=update.message.video.file_id,
                caption="🎬 ویدیوی ناشناس دریافت شد!",
                reply_markup=reply_markup
            )
            await update.message.reply_text("✅ ویدیوی شما ارسال شد.")

        # ارسال ویس
        elif update.message.voice:
            await context.bot.send_voice(
                chat_id=target_id,
                voice=update.message.voice.file_id,
                caption="🎤 ویس ناشناس دریافت شد!",
                reply_markup=reply_markup
            )
            await update.message.reply_text("✅ ویس شما ارسال شد.")

    # اگر کاربر در حال پاسخ دادن است
    elif user.id in message_history and message_history[user.id]:
        original_sender_id, original_msg_id = message_history[user.id][-1]
        
        # ارسال پاسخ به کاربر اصلی
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
        await update.message.reply_text(
            "⚠️ لطفاً اول از طریق لینک ناشناس وارد شو!",
            reply_markup=ReplyKeyboardRemove()
        )

# --- دکمه پاسخ ---
async def reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("reply_"):
        target_id = int(query.data.split("_")[1])
        conversations[query.from_user.id] = target_id
        await query.message.reply_text(
            "💬 در حال پاسخ به پیام ناشناس...\n\n"
            "پیام/عکس/ویس خود را ارسال کنید:"
        )

# --- اجرای ربات ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CallbackQueryHandler(reply_button, pattern="^reply_"))
    app.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE,
        handle_message
    ))

    logger.info("✅ ربات فعال شد!")
    app.run_polling()
