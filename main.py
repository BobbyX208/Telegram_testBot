import importlib
import logging
import os
import pkgutil
from typing import Dict, List, Tuple, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CallbackQueryHandler, 
    CommandHandler, 
    ContextTypes,
    CallbackContext,
    PicklePersistence
)

from config import BOT_TOKEN, MODULES_DIR, PERSISTENCE_FILE

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Module:
    """Base class for all bot modules"""
    def __init__(self, name: str, callback: str, handler, register_func):
        self.name = name
        self.callback = callback
        self.handler = handler
        self.register_func = register_func
    
    def get_button(self) -> Tuple[str, str]:
        return (self.name, self.callback)

class ModuleManager:
    """Manages loading and handling of modules"""
    def __init__(self):
        self.modules: Dict[str, Module] = {}
    
    def load_modules(self, application) -> List[Tuple[str, str]]:
        """Dynamically load all modules from the modules directory"""
        self.modules.clear()
        buttons = []
        
        # Ensure modules directory exists
        if not os.path.exists(MODULES_DIR):
            os.makedirs(MODULES_DIR)
            logger.warning(f"Created {MODULES_DIR} directory. Add modules there.")
            return buttons
        
        # Import all Python files in the modules directory
        for _, module_name, _ in pkgutil.iter_modules([MODULES_DIR]):
            try:
                # Import the module
                spec = importlib.util.spec_from_file_location(
                    module_name, 
                    os.path.join(MODULES_DIR, f"{module_name}.py")
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Check if module has required attributes
                if (hasattr(module, "NAME") and 
                    hasattr(module, "CALLBACK") and 
                    hasattr(module, "get_button") and 
                    hasattr(module, "handle_callback") and
                    hasattr(module, "register_handlers")):
                    
                    # Create module instance
                    mod = Module(
                        name=module.NAME,
                        callback=module.CALLBACK,
                        handler=module.handle_callback,
                        register_func=module.register_handlers
                    )
                    
                    # Store module and button
                    self.modules[module.CALLBACK] = mod
                    buttons.append(mod.get_button())
                    
                    # Register module-specific handlers
                    mod.register_func(application, self)
                    
                    logger.info(f"Loaded module: {module.NAME}")
                else:
                    logger.warning(f"Module {module_name} is missing required attributes")
            except Exception as e:
                logger.error(f"Failed to load module {module_name}: {e}")
        
        return buttons
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Route callback to the appropriate module handler"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        if callback_data in self.modules:
            try:
                await self.modules[callback_data].handler(update, context)
            except Exception as e:
                logger.error(f"Error in module {callback_data}: {e}")
                await query.edit_message_text(text="An error occurred while processing your request.")
        else:
            logger.warning(f"Unknown callback data: {callback_data}")
            await query.edit_message_text(text="Unknown module selected.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with inline buttons for each loaded module"""
    # Load modules and get buttons
    module_manager = context.application.module_manager
    buttons = module_manager.load_modules(context.application)
    
    if not buttons:
        await update.message.reply_text("No modules available. Add modules to the modules directory.")
        return
    
    # Create inline keyboard with 2 buttons per row
    keyboard = []
    for i in range(0, len(buttons), 2):
        row = buttons[i:i+2]
        keyboard.append([
            InlineKeyboardButton(text, callback_data=callback) 
            for text, callback in row
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send message with keyboard
    await update.message.reply_text(
        "Please choose a module:", 
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with information about how to use the bot"""
    await update.message.reply_text(
        "Welcome to the Modular Telegram Bot!\n\n"
        "Use /start to see available modules.\n"
        "Each module provides different functionality through inline buttons."
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by Updates"""
    logger.error(f"Update {update} caused error {context.error}")

def main() -> None:
    """Start the bot"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found. Please set it in your environment variables or .env file")
        return
    
    # Set up persistence
    persistence = PicklePersistence(filepath=PERSISTENCE_FILE)
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).persistence(persistence).build()
    
    # Create module manager and attach to application
    module_manager = ModuleManager()
    application.module_manager = module_manager
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(module_manager.handle_callback))
    
    # Load modules initially
    module_manager.load_modules(application)
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot
    logger.info("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()