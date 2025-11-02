import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

# === الإعدادات ===
TELEGRAM_TOKEN = os.getenv("7411254867:AAE9imYxBxIrkL9TAxM3ti9ceO-p-HNkfTo")
IG_USERNAME = os.getenv("fahlkm86")
IG_PASSWORD = os.getenv("123456789asdASD#")

# === تسجيل الدخول إلى إنستجرام ===
cl = Client()
session_file = "session.json"

def login_to_instagram():
    try:
        if os.path.exists(session_file):
            cl.load_settings(session_file)
        cl.login(IG_USERNAME, IG_PASSWORD)
        cl.dump_settings(session_file)
        print("✅ تم تسجيل الدخول إلى إنستجرام")
    except Exception as e:
        print(f"❌ فشل تسجيل الدخول: {e}")
        exit(1)

# === الأوامر ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا! أرسل لي:\n"
        "📹 فيديو لأرفعه كـ Reel\n"
        "📊 /stats لعرض الإحصائيات"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = cl.user_id_from_username(IG_USERNAME)
        info = cl.user_info(user_id)
        msg = (
            f"👤 الحساب: @{info.username}\n"
            f"👥 المتابعين: {info.follower_count:,}\n"
            f"🫂 المتابعون: {info.following_count:,}\n"
            f"📈 المنشورات: {info.media_count}"
        )
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في جلب الإحصائيات: {str(e)}")

async def upload_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.video:
        await update.message.reply_text("يرجى إرسال فيديو فقط.")
        return

    status_msg = await update.message.reply_text("جاري تحميل الفيديو...")

    try:
        # تحميل الفيديو
        file = await update.message.video.get_file()
        file_path = "video_to_upload.mp4"
        await file.download_to_drive(file_path)

        await status_msg.edit_text("جاري الرفع على إنستجرام (Reel)...")

        # رفع كـ Reel
        cl.clip_upload(file_path, caption="تم الرفع عبر بوت التليجرام 🤖")

        await status_msg.edit_text("✅ تم رفع الفيديو كـ Reel بنجاح!")
    except Exception as e:
        await status_msg.edit_text(f"❌ فشل الرفع: {str(e)}")
    finally:
        # تنظيف الملف
        if os.path.exists(file_path):
            os.remove(file_path)

# === التشغيل ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # تسجيل الدخول أول مرة
    login_to_instagram()

    # تشغيل بوت التليجرام
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.VIDEO, upload_video))

    print("🚀 البوت شغال...")
    app.run_polling()
