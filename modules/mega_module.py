import logging
import re
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

logger = logging.getLogger(__name__)

NAME = "Mega Downloader"
CALLBACK = "mega_downloader"

def get_button():
    return (NAME, CALLBACK)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📥 Please send me a Mega.nz link to download.\n\n"
        "I’ll fetch the file and send it back to you."
    )
    context.user_data["awaiting_mega"] = True

async def handle_mega_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Mega.nz links"""
    if not context.user_data.get("awaiting_mega"):
        return

    text = update.message.text.strip()
    mega_pattern = r'https?://mega\.nz/(file|folder)/[^\s]+'

    if re.match(mega_pattern, text):
        # Placeholder: use mega.py for actual download
        await update.message.reply_text(
            f"✅ Received Mega.nz link:\n{text}\n\n"
            "Downloading... (placeholder, use mega.py in production)"
        )
        context.user_data["awaiting_mega"] = False
    else:
        await update.message.reply_text("⚠️ Please send a valid Mega.nz link.")

def register_handlers(application, module_manager):
    """Register handler for Mega.nz links"""
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex(r'https?://mega\.nz/'), handle_mega_link)
    )