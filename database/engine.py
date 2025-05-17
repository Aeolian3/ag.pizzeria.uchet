from config import Config
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(Config.DB_URL, echo=False)
