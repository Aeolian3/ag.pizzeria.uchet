from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.future import select
from models import *

class DBUserMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(self, handler, event: TelegramObject, data: dict):
        async with self.session_pool() as session:
            data['db'] = session

            tg_user = None
            if hasattr(event, 'message') and event.message:
                tg_user = event.message.from_user
            elif hasattr(event, 'callback_query') and event.callback_query:
                tg_user = event.callback_query.from_user
            elif hasattr(event, 'inline_query') and event.inline_query:
                tg_user = event.inline_query.from_user

            if tg_user:
                result = await session.execute(select(User).where(User.telegram_id == tg_user.id))
                user = result.scalar_one_or_none()

                if user is None:
                    new_user = User(
                        telegram_id=tg_user.id,
                        first_name=tg_user.first_name or "",
                        last_name=tg_user.last_name or "",
                        role_id=1,
                        organization_id=1
                    )
                    session.add(new_user)
                    await session.commit()

            return await handler(event, data)
