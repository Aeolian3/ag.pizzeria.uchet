from aiogram import Dispatcher
from handlers import start, join, finished, cancelled, start_session,products,category,inventory
from sqlalchemy.ext.asyncio import async_sessionmaker
from database.engine import engine
from middleware.db import DBUserMiddleware


def register_handlers(dp: Dispatcher):
    session_pool = async_sessionmaker(engine, expire_on_commit=False)

    dp.update.middleware(DBUserMiddleware(session_pool))

    dp.include_router(start.router)
    dp.include_router(join.router)
    dp.include_router(finished.router)
    dp.include_router(cancelled.router)
    dp.include_router(start_session.router)
    dp.include_router(products.router)
    dp.include_router(category.router)
    dp.include_router(inventory.router)
