from aiogram import F , Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.future import select
from sqlalchemy import and_
from models.inv_session import InventoryStatus
from database.reposotory import  get_user_id_by_telegram_id, get_categories_by_organization
from models import InventorySession, InventoryUser, User
from states.states import InventoryStates
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

@router.callback_query(F.data == "join_inventory")
async def handle_join_session(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer("Введите PIN-код для подключения...")
    await state.set_state(InventoryStates.waiting_for_pin)



@router.message(InventoryStates.waiting_for_pin)
async def process_pin(message: Message, state: FSMContext, db: AsyncSession):
    pin = message.text.strip()

    try:
        pin_int = int(pin)
    except ValueError:
        await message.answer("❌ Неверный PIN-код. Введите только цифры.")
        return

    session = await db.scalar(
        select(InventorySession).where(InventorySession.pin_code == pin_int)
    )

    if not session:
        await message.answer("❌ Неверный PIN-код. Попробуйте ещё раз.")
        return

    session = await db.scalar(
        select(InventorySession).where(
            and_(
                InventorySession.pin_code == pin_int,
                InventorySession.status == InventoryStatus.active
            )
        )
    )

    if not session:
        await message.answer("❌ Сессия с таким PIN-кодом не найдена или уже завершена.")
        return

    telegram_id = message.from_user.id
    user_id = await get_user_id_by_telegram_id(db, telegram_id)

    already_joined = await db.scalar(
        select(InventoryUser).where(
            InventoryUser.session_id == session.id,
            InventoryUser.user_id == user_id
        )
    )

    if not already_joined:
        db.add(InventoryUser(session_id=session.id, user_id=user_id))
        await db.commit()

    await message.answer("Успешно присоединились к сессии.")

    await state.update_data(session_id=session.id)

    user = await db.scalar(select(User).where(User.id == user_id))
    categories = await get_categories_by_organization(db, user.organization_id)

    if not categories:
        await message.answer("❗ В вашей организации нет категорий продуктов.")
        await state.clear()
        return

    from handlers.menu import create_category_keyboard
    keyboard = await create_category_keyboard(categories, session.id)
    created_at_str = session.created_at.strftime("%d.%m.%Y %H:%M")
    session_number = str(session.id).zfill(5)

    message_text = (
        f"📦 Начата ревизия номер {session_number} от {created_at_str} "
        f"с кодом доступа {session.pin_code}, выберите категорию для учета:"
    )

    await message.answer(message_text, reply_markup=keyboard)
