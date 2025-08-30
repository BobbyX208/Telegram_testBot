import os
import zipfile
import tempfile
import shutil
import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler
)

logger = logging.getLogger(__name__)

NAME = "Zip Extractor"
CALLBACK = "zip_extractor"

# Conversation states
AWAITING_ZIP, AWAITING_PASSWORD = range(2)

def get_button():
    return (NAME, CALLBACK)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Please send me a ZIP file to extract.\n\n"
        "I will extract it and then delete the original file from the cloud."
    )
    
    # Set state to awaiting zip file
    return AWAITING_ZIP

async def handle_zip_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming ZIP files"""
    if not update.message.document:
        await update.message.reply_text("Please send a ZIP file.")
        return AWAITING_ZIP
    
    doc = update.message.document
    if not doc.file_name.endswith('.zip'):
        await update.message.reply_text("Please send a valid ZIP file.")
        return AWAITING_ZIP
    
    # Create temp directory for extraction
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, doc.file_name)
    
    # Download file
    file = await doc.get_file()
    await file.download_to_drive(zip_path)
    
    # Store path in context for later use
    context.user_data['zip_path'] = zip_path
    context.user_data['temp_dir'] = temp_dir
    
    # Try to extract without password
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.testzip()  # Test the zip file
            extract_path = os.path.join(temp_dir, 'extracted')
            os.makedirs(extract_path, exist_ok=True)
            zf.extractall(extract_path)
            
            # Send extracted files
            extracted_files = os.listdir(extract_path)
            if extracted_files:
                await update.message.reply_text(
                    f"Successfully extracted {len(extracted_files)} files."
                )
                
                # Send each file (simplified example)
                for file_name in extracted_files[:5]:  # Limit to 5 files
                    file_path = os.path.join(extract_path, file_name)
                    if os.path.isfile(file_path):
                        await update.message.reply_document(document=open(file_path, 'rb'))
                
                if len(extracted_files) > 5:
                    await update.message.reply_text(
                        f"... and {len(extracted_files) - 5} more files."
                    )
            else:
                await update.message.reply_text("The ZIP file is empty.")
            
            # Clean up
            shutil.rmtree(temp_dir)
            return ConversationHandler.END
            
    except RuntimeError as e:
        if 'password' in str(e).lower() or 'encrypted' in str(e).lower():
            await update.message.reply_text(
                "This ZIP file is password protected. Please send the password."
            )
            return AWAITING_PASSWORD
        else:
            await update.message.reply_text(f"Error processing ZIP file: {e}")
            # Clean up on error
            if 'temp_dir' in context.user_data:
                shutil.rmtree(context.user_data['temp_dir'])
            return ConversationHandler.END
    
    except Exception as e:
        await update.message.reply_text(f"Error processing ZIP file: {e}")
        # Clean up on error
        if 'temp_dir' in context.user_data:
            shutil.rmtree(context.user_data['temp_dir'])
        return ConversationHandler.END

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle password for encrypted ZIP files"""
    password = update.message.text
    zip_path = context.user_data.get('zip_path')
    temp_dir = context.user_data.get('temp_dir')
    
    if not zip_path or not temp_dir:
        await update.message.reply_text("Something went wrong. Please try again.")
        return ConversationHandler.END
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.setpassword(password.encode())
            zf.testzip()  # Test the zip file
            
            extract_path = os.path.join(temp_dir, 'extracted')
            os.makedirs(extract_path, exist_ok=True)
            zf.extractall(extract_path)
            
            # Send extracted files
            extracted_files = os.listdir(extract_path)
            if extracted_files:
                await update.message.reply_text(
                    f"Successfully extracted {len(extracted_files)} files with the provided password."
                )
                
                # Send each file (simplified example)
                for file_name in extracted_files[:5]:  # Limit to 5 files
                    file_path = os.path.join(extract_path, file_name)
                    if os.path.isfile(file_path):
                        await update.message.reply_document(document=open(file_path, 'rb'))
                
                if len(extracted_files) > 5:
                    await update.message.reply_text(
                        f"... and {len(extracted_files) - 5} more files."
                    )
            else:
                await update.message.reply_text("The ZIP file is empty.")
    
    except Exception as e:
        await update.message.reply_text(
            f"Failed to extract with the provided password: {e}\n\n"
            "Please try again with a different password or send a new ZIP file."
        )
        return AWAITING_ZIP
    
    finally:
        # Clean up
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the current operation"""
    await update.message.reply_text("Operation cancelled.")
    
    # Clean up any temporary files
    if 'temp_dir' in context.user_data:
        temp_dir = context.user_data['temp_dir']
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    return ConversationHandler.END

def register_handlers(application, module_manager):
    """Register conversation handler for ZIP extraction"""
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_callback, pattern=f"^{CALLBACK}$")],
        states={
            AWAITING_ZIP: [
                MessageHandler(filters.Document.ALL, handle_zip_file),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_zip_file)
            ],
            AWAITING_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_user=True
    )
    
    application.add_handler(conv_handler)