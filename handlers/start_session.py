from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.reposotory import create_inventory_session
from handlers.menu import create_category_keyboard, main_menu_kb, frequency_keyboard
from models import *
from models.inv_session import InventoryFrequency
from states.states import InventoryStates

router = Router()


@router.callback_query(F.data == "start_inventory")
async def handle_start_session(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(InventoryStates.choose_frequency)
    await callback.message.edit_text(
        "Выберите тип ревизии:",
        reply_markup=frequency_keyboard
    )


@router.callback_query(F.data.startswith("frequency:"), InventoryStates.choose_frequency)
async def handle_frequency_choice(callback: CallbackQuery, state: FSMContext, db: AsyncSession):
    _, raw_frequency = callback.data.split(":")

    raw_frequency = callback.data.split(":")[1]

    try:
        frequency = InventoryFrequency(raw_frequency)
    except ValueError:
        await callback.answer("❗ Неверный тип инвентаризации", show_alert=True)
        return

    telegram_id = callback.from_user.id

    try:
        session = await create_inventory_session(db, telegram_id=telegram_id, frequency=frequency)
    except (ValueError, PermissionError) as e:
        await callback.answer(str(e), show_alert=True)
        return

    await state.update_data(session_id=session.id)

    user = await db.scalar(select(User).where(User.telegram_id == telegram_id))
    categories_result = await db.execute(
        select(Category).where(Category.organization_id == user.organization_id)
    )
    categories = categories_result.scalars().all()

    if not categories:
        await callback.message.answer("❗ В вашей организации нет категорий продуктов.")
        return

    category_kb = await create_category_keyboard(categories)

    created_at_str = session.created_at.strftime("%d.%m.%Y %H:%M")
    session_number = f"{session.id:05}"

    freq_text = {
        InventoryFrequency.daily: "дневная",
        InventoryFrequency.weekly: "недельная",
        InventoryFrequency.monthly: "месячная"
    }.get(frequency, str(frequency))

    message_text = (
        f"📦 Начата *{freq_text}* ревизия номер {session_number} от {created_at_str} "
        f"с кодом доступа `{session.pin_code}`, выберите категорию для учета:"
    )

    await callback.message.edit_text(message_text, reply_markup=category_kb, parse_mode="Markdown")



@router.callback_query(F.data == "back_to_menu", InventoryStates.choose_frequency)
async def handle_back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Главное меню", reply_markup=main_menu_kb)



