import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

NAME = "Example Module"
CALLBACK = "example_module"

def get_button():
    return (NAME, CALLBACK)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.edit_message_text(
        text="You selected the example module!\n\n"
             "This is a demonstration of how modules work in the modular Telegram bot."
    )

def register_handlers(application, module_manager):
    # This module doesn't need any additional handlers
    pass