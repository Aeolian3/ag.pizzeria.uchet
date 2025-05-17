import asyncio
from aiogram import Bot, Dispatcher
from dispatcher import register_handlers
from database.base import Base
from database.sessionmaker import engine
from config import Config
import logging
logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=Config.TOKEN)
    dp = Dispatcher()

    register_handlers(dp)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
