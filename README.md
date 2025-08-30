# Modular Telegram Bot

A production-ready Python Telegram bot that dynamically loads modules from the `/modules` directory.

## Features

- Dynamic module loading - just add Python files to the `/modules` directory
- Persistence across restarts using PicklePersistence
- Comprehensive error handling and logging
- Conversation handling for multi-step interactions
- Clean, extensible architecture

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
 Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a .env file with your bot token:
   ```
   BOT_TOKEN=your_bot_token_here
   ```
3. Run the bot:
   ```bash
   python main.py
   ```

Adding Modules

1. Create a new Python file in the /modules directory
2. Implement the required variables and functions:
   · NAME: Display name for the button
   · CALLBACK: Unique callback string
   · get_button(): Returns (NAME, CALLBACK)
   · handle_callback(update, context): Handles the button click
   · register_handlers(application, module_manager): Registers any additional handlers
3. The bot will automatically detect and load the new module on restart

Included Modules

· Example Module: Demonstrates the module structure
· Zip Extractor: Handles ZIP file extraction, including password-protected files
· Mega Downloader: Handles Mega.nz links (stub implementation)

Production Considerations

· Error handling is implemented throughout the code
· All file operations use temporary directories for security
· Comprehensive logging to both file and console
· Persistence ensures user state is maintained across restarts

```

## Key Features

1. **Dynamic Module Loading**: Automatically discovers and loads all valid modules from the `/modules` directory
2. **Persistence**: Uses PicklePersistence to maintain user data across restarts
3. **Comprehensive Error Handling**: All operations are wrapped in try-catch blocks with proper logging
4. **Conversation Handling**: Supports multi-step interactions like password prompts
5. **Production Ready**: Includes logging, error handling, and proper resource cleanup
6. **Extensible Architecture**: Easy to add new functionality by creating new modules

## Usage

1. Start the bot with `/start` to see all available modules
2. Click on an inline button to execute the corresponding module
3. Add new functionality by creating new Python files in the `/modules` directory