from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from database.sessionmaker import AsyncSessionLocal
from handlers.menu import main_menu_kb
from models import *

router = Router()

@router.message(F.text == "/start")
async def start_handler(message: Message):
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            role_stmt = select(Role).where(Role.id == 1)
            role_result = await session.execute(role_stmt)
            default_role = role_result.scalar_one()

            new_user = User(
                telegram_id=message.from_user.id,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                role=default_role,
                organization_id=1
            )

            session.add(new_user)
            await session.commit()
            await message.answer(f"Ты зарегистрирован, {message.from_user.first_name}!")

        await message.answer("Главное меню:", reply_markup=main_menu_kb)


@router.callback_query(F.data == "main_menu_kb")
async def show_main_menu(callback: CallbackQuery):
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu_kb)