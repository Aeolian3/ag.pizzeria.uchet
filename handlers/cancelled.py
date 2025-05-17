from datetime import datetime
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.reposotory import get_user_id_by_telegram_id
from models import *
from utils.render import render_inventory_status_message

router = Router()

@router.callback_query(F.data == "cancelled_inventory")
async def show_cancelled_months(callback: CallbackQuery, db: AsyncSession, state: FSMContext):
    now = datetime.now()
    current_month = now.month

    keyboard = []
    for month in range(1, current_month + 1):
        month_name = datetime(1900, month, 1).strftime("%B")
        keyboard.append([InlineKeyboardButton(
            text=month_name.capitalize(),
            callback_data=f"cancelled_month_{month}"
        )])

    keyboard.append([InlineKeyboardButton(text="Назад", callback_data="main_menu_kb")])
    await callback.message.edit_text("Выберите месяц:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@router.callback_query(F.data.startswith("cancelled_month_"))
async def show_cancelled_sessions_for_month(callback: CallbackQuery, db: AsyncSession, state: FSMContext):
    month = int(callback.data.split("_")[-1])
    telegram_id = callback.from_user.id

    user_id = await get_user_id_by_telegram_id(db, telegram_id)
    if not user_id:
        await callback.message.edit_text("❌ Пользователь не найден.")
        return

    filters = [
        User.id == user_id,
        InventorySession.finished_at.isnot(None),
        InventorySession.status == "cancelled",
        extract('month', InventorySession.finished_at) == month
    ]
    stmt = select(InventorySession).join(User, InventorySession.organization_id == User.organization_id).where(
        *filters).order_by(InventorySession.finished_at.desc())

    result = await db.execute(stmt)
    sessions = result.scalars().all()

    if not sessions:
        await callback.message.edit_text(
            "Нет отменённых сессий за выбранный месяц.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Назад", callback_data="cancelled_inventory")]
            ])
        )
        return

    buttons = [
        [InlineKeyboardButton(text=f"Сессия #{s.id}", callback_data=f"view_cancelled_{s.id}")]
        for s in sessions
    ]
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="cancelled_inventory")])

    await callback.message.edit_text(
        "📋 Отменённые сессии:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@router.callback_query(F.data.startswith("view_cancelled_"))
async def view_cancelled_session(callback: CallbackQuery, db: AsyncSession):
    session_id = int(callback.data.split("_")[-1])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать отчёт", callback_data=f"create_report_{session_id}")],
        [InlineKeyboardButton(text="Назад", callback_data="cancelled_inventory")]
    ])
    await callback.message.edit_text(f"Отменённая сессия #{session_id}", reply_markup=keyboard)


@router.callback_query(F.data == "cancel_inventory")
async def cancel_inventory(callback: CallbackQuery, state: FSMContext, db: AsyncSession):
    user_data = await state.get_data()
    session_id = user_data.get("session_id")

    session = await db.scalar(select(InventorySession).where(InventorySession.id == session_id))
    if session:
        session.status = "cancelled"
        session.finished_at = datetime.now()
        await db.commit()
        await callback.message.delete()
        await callback.message.answer(render_inventory_status_message(session, "cancelled"))
    else:
        await callback.message.answer("❗ Не удалось найти сессию.")

