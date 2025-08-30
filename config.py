import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MODULES_DIR = "modules"
PERSISTENCE_FILE = "data/persistence.pickle"

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)