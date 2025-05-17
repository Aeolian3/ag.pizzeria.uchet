import dotenv

load_dotenv = dotenv.load_dotenv()

class Config:
 TOKEN = dotenv.get_key(".env", "BOT_TOKEN")
 DB_URL = dotenv.get_key(".env", "DATABASE_URL")
