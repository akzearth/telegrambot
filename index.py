from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import yt_dlp
import os
import tempfile

# Function to handle the /start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! لینک یوتیوب رو بفرستید تا فایل‌های دانلود رو براتون آماده کنم.")

# Function to handle incoming YouTube links
def handle_message(update: Update, context: CallbackContext):
    url = update.message.text
    if "youtube.com" in url or "youtu.be" in url:
        update.message.reply_text("در حال پردازش لینک، لطفاً منتظر بمانید...")
        list_formats(update, context, url)
    else:
        update.message.reply_text("لطفاً یک لینک معتبر یوتیوب ارسال کنید.")

# Function to list available formats
def list_formats(update: Update, context: CallbackContext, url: str):
    try:
        ydl_opts = {'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

            buttons = []
            for f in formats:
                if f.get('ext') in ['mp4', 'mp3']:
                    buttons.append(
                        [InlineKeyboardButton(f"{f['format_note']} - {f['ext']}", callback_data=f"download|{f['format_id']}|{url}")]
                    )

            if buttons:
                reply_markup = InlineKeyboardMarkup(buttons)
                update.message.reply_text("فرمت‌های موجود:", reply_markup=reply_markup)
            else:
                update.message.reply_text("فرمتی برای دانلود پیدا نشد.")

    except Exception as e:
        update.message.reply_text(f"خطایی رخ داد: {str(e)}")

# Function to handle download requests
def download_file(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    _, format_id, url = query.data.split('|')

    try:
        ydl_opts = {
            'format': format_id,
            'outtmpl': tempfile.mktemp(),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            filepath = ydl.prepare_filename(info)

            with open(filepath, 'rb') as f:
                query.message.reply_document(f, filename=os.path.basename(filepath))

        os.remove(filepath)

    except Exception as e:
        query.message.reply_text(f"خطایی در دانلود رخ داد: {str(e)}")

# Main function to set up the bot
def main():
    TOKEN = "7637033506:AAFz-m-Zdl9N3VOXbLriw68HS-o6647lv1A"
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_handler(CallbackQueryHandler(download_file, pattern=r"^download|"))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
