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