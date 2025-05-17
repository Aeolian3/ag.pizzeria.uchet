from datetime import datetime
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.reposotory import get_user_id_by_telegram_id
from models import *
from template.report import create_inventory_report
from utils.render import render_inventory_status_message

router = Router()

@router.callback_query(F.data == "finished_inventory")
async def show_finished_months(callback: CallbackQuery, db: AsyncSession, state: FSMContext):
    now = datetime.now()
    current_month = now.month

    keyboard = []
    for month in range(1, current_month + 1):
        month_name = datetime(1900, month, 1).strftime("%B")
        keyboard.append([InlineKeyboardButton(
            text=month_name.capitalize(),
            callback_data=f"inventory_month_{month}"
        )])
    keyboard.append([InlineKeyboardButton(text="Назад", callback_data="main_menu_kb")])
    await callback.message.edit_text("Выберите месяц:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@router.callback_query(F.data.startswith("inventory_month_"))
async def show_sessions_for_month(callback: CallbackQuery, db: AsyncSession, state: FSMContext):
    month = int(callback.data.split("_")[-1])
    telegram_id = callback.from_user.id

    user_id = await get_user_id_by_telegram_id(db, telegram_id)
    if not user_id:
        await callback.message.edit_text("❌ Пользователь не найден.")
        return

    filters = [
        User.id == user_id,
        InventorySession.finished_at.isnot(None),
        InventorySession.status == "finished",
        extract('month', InventorySession.finished_at) == month
    ]
    stmt = select(InventorySession).join(User, InventorySession.organization_id == User.organization_id).where(
        *filters).order_by(InventorySession.finished_at.desc())

    result = await db.execute(stmt)
    sessions = result.scalars().all()

    if not sessions:
        await callback.message.edit_text(
            "Нет завершенных сессий за выбранный месяц.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Назад", callback_data="finished_inventory")]
            ])
        )
        return

    buttons = [
        [InlineKeyboardButton(text=f"Сессия #{s.id}", callback_data=f"view_session_{s.id}")]
        for s in sessions
    ]
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="finished_inventory")])

    await callback.message.edit_text(
        "📋 Завершенные сессии:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("view_session_"))
async def view_session(callback: CallbackQuery, db: AsyncSession):
    session_id = int(callback.data.split("_")[-1])


    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать ведомость", callback_data=f"create_report_{session_id}")],
        [InlineKeyboardButton(text="Назад", callback_data="finished_inventory")]
    ])
    await callback.message.edit_text(f"📌 Сессия #{session_id}", reply_markup=keyboard)



@router.callback_query(F.data.startswith("create_report_"))
async def export_report(callback: CallbackQuery, db: AsyncSession):
    session_id = int(callback.data.split("_")[-1])
    await callback.answer("Создаём отчёт...")

    try:
        file = await create_inventory_report(session_id, db)  # это BytesIO
        file.seek(0)

        input_file = BufferedInputFile(
            file.read(),
            filename=f"ревизия_{session_id}.xlsx"
        )
        await callback.message.answer_document(document=input_file, caption="Отчёт готов")
    except Exception as e:
        await callback.message.answer("⚠️ Ошибка при создании отчёта.")
        raise e





@router.callback_query(F.data == "finish_inventory")
async def finish_inventory(callback: CallbackQuery, state: FSMContext, db: AsyncSession):
    user_data = await state.get_data()
    session_id = user_data.get("session_id")
    print(f"session_id из state: {session_id!r}")

    if not session_id:
        await callback.message.answer("❗ session_id не найден в состоянии.")
        return

    result = await db.execute(select(InventorySession).where(InventorySession.id == session_id))
    session = result.scalars().first()
    if session:
        session.status = "finished"
        session.finished_at = datetime.utcnow()
        await db.commit()
        await callback.message.delete()
        await callback.message.answer(render_inventory_status_message(session, "finished"))
    else:
        await callback.message.answer(f"❗ Сессия с id={session_id} не найдена.")



