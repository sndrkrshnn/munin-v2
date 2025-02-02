import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
