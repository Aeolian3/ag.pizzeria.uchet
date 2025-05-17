from dotenv import load_dotenv
import os

load_dotenv()
class Config:
    TOKEN = os.getenv("BOT_TOKEN")
    DB_URL = os.getenv("DATABASE_URL")

