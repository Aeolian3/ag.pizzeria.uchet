import logging
from datetime import datetime
from decimal import Decimal
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from database.reposotory import get_categories_by_organization, get_user_id_by_telegram_id, check_product_in_session
from handlers.menu import create_category_keyboard
from models import *
from states.states import InventoryStates
from utils.page import send_product_page

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith("select_product_"))
async def handle_product_selection(callback_query: CallbackQuery, state: FSMContext, db: AsyncSession):
    try:
        product_id = int(callback_query.data.split("_")[-1])
        data = await state.get_data()
        session_id = data.get("session_id")
        telegram_id = callback_query.from_user.id
        user_id = await get_user_id_by_telegram_id(db, telegram_id)

        product = await db.scalar(
            select(Product)
            .options(joinedload(Product.unit))
            .where(Product.id == product_id)
        )
        if not product:
            await callback_query.answer("❗ Продукт не найден.", show_alert=True)
            return

        existing_entries = await check_product_in_session(db, session_id, product_id)

        if existing_entries:
            text_lines = [f"⚠️ Продукт *{product.name}* уже введен в этой ревизии:"]
            total = 0
            for entry, user in existing_entries:
                text_lines.append(f"{user.first_name} - {user.last_name} — {entry.quantity} шт.")
                total += entry.quantity
            text_lines.insert(1, f"Общее количество: {total} шт.")
            text_lines.append("\nЧто вы хотите сделать?")
            await state.update_data(
                selected_product_id=product_id,
                selected_product_name=product.name,
                selected_unit_name=product.unit.name if product.unit else "ед.",
                existing_entries=True
            )
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Добавить количество", callback_data="add_quantity")],
                [InlineKeyboardButton(text="Перезаписать", callback_data="overwrite_quantity")],
                [InlineKeyboardButton(text="Назад", callback_data="back_to_categories")]
            ])

            await callback_query.message.edit_text("\n".join(text_lines), reply_markup=keyboard, parse_mode="Markdown")
            await callback_query.answer()
            return

        await state.update_data(
            selected_product_id=product_id,
            selected_product_name=product.name,
            selected_unit_name=product.unit.name if product.unit else "ед.",
            existing_entries=False
        )
        await state.set_state(InventoryStates.waiting_for_quantity)

        await callback_query.message.edit_text(
            f"Введите количество продукта - {product.name} ({product.unit.name if product.unit else 'ед.'}):",
            reply_markup=None
        )
        await callback_query.answer()

    except Exception as e:
        logger.error(f"Error in product selection: {e}")
        await callback_query.answer("❗ Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "add_quantity")
async def handle_add_quantity(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(update_mode="add")
    await state.set_state(InventoryStates.waiting_for_quantity)
    data = await state.get_data()
    await callback_query.message.edit_text(
        f"Введите количество, которое нужно ДОБАВИТЬ к продукту - {data['selected_product_name']} ({data['selected_unit_name']}):"
    )
    await callback_query.answer()

@router.callback_query(F.data == "overwrite_quantity")
async def handle_overwrite_quantity(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(update_mode="overwrite")
    await state.set_state(InventoryStates.waiting_for_quantity)
    data = await state.get_data()
    await callback_query.message.edit_text(
        f"Введите НОВОЕ количество для продукта - {data['selected_product_name']} ({data['selected_unit_name']}):"
    )
    await callback_query.answer()

@router.callback_query(F.data == "page_prev")
async def handle_prev_page(callback_query: CallbackQuery, state: FSMContext, db: AsyncSession):
    data = await state.get_data()
    page = data.get("page", 1)
    if page > 1:
        await state.update_data(page=page - 1)
        await send_product_page(callback_query, state, db)
    await callback_query.answer()


@router.callback_query(F.data == "page_next")
async def handle_next_page(callback_query: CallbackQuery, state: FSMContext, db: AsyncSession):
    data = await state.get_data()
    await state.update_data(page=data.get("page", 1) + 1)
    await send_product_page(callback_query, state, db)
    await callback_query.answer()


@router.callback_query(F.data == "back_to_categories")
async def handle_back_to_categories(callback_query: CallbackQuery, state: FSMContext, db: AsyncSession):
    user = await db.scalar(select(User).where(User.telegram_id == callback_query.from_user.id))

    data = await state.get_data()
    session_id = data.get("session_id")

    if not session_id:
        await callback_query.answer("❗ Не найдена активная сессия.", show_alert=True)
        return

    session = await db.scalar(select(InventorySession).where(InventorySession.id == session_id))
    if not session:
        await callback_query.answer("❗ Сессия не найдена.", show_alert=True)
        return

    categories = await get_categories_by_organization(db, user.organization_id)
    if not categories:
        await callback_query.message.edit_text("❗ В вашей организации нет категорий продуктов.")
        return

    category_kb = await create_category_keyboard(categories)
    created_at_str = session.created_at.strftime("%d.%m.%Y %H:%M")
    session_number = str(session.id).zfill(5)

    message_text = (
        f"📦 Начата ревизия номер {session_number} от {created_at_str} "
        f"с кодом доступа {session.pin_code}, выберите категорию для учета:"
    )

    await callback_query.message.edit_text(
        message_text,
        reply_markup=category_kb
    )

@router.message(InventoryStates.waiting_for_quantity)
async def handle_quantity_input(message: Message, state: FSMContext, db: AsyncSession):
    data = await state.get_data()
    product_id = data.get("selected_product_id")
    session_id = data.get("session_id")
    telegram_id = message.from_user.id
    user_id = await get_user_id_by_telegram_id(db, telegram_id)
    update_mode = data.get("update_mode", "new")

    try:
        quantity = Decimal(message.text)
    except ValueError:
        await message.answer("❗ Введите корректное число.")
        return

    stmt = select(InventoryProduct).where(
        InventoryProduct.session_id == session_id,
        InventoryProduct.product_id == product_id,
        InventoryProduct.user_id == user_id
    )
    inventory_product = await db.scalar(stmt)

    if inventory_product:
        if update_mode == "add":
            inventory_product.quantity += quantity
        elif update_mode == "overwrite":
            inventory_product.quantity = quantity
        else:
            inventory_product.quantity = quantity
        inventory_product.added_at = datetime.utcnow()
        await db.commit()
    else:
        inventory_product = InventoryProduct(
            session_id=session_id,
            user_id=user_id,
            product_id=product_id,
            added_at=datetime.utcnow(),
            quantity=quantity
        )
        db.add(inventory_product)
        await db.commit()

    product = await db.scalar(select(Product).where(Product.id == product_id))
    await message.answer(
        f"✅ Продукт {product.name} учтен в количестве {inventory_product.quantity}."
    )

    user = await db.scalar(select(User).where(User.id == user_id))
    categories = await get_categories_by_organization(db, user.organization_id)
    keyboard = await create_category_keyboard(categories, session_id)
    session = await db.scalar(select(InventorySession).where(InventorySession.id == session_id))
    created_at_str = session.created_at.strftime("%d.%m.%Y %H:%M")
    session_number = str(session.id).zfill(5)
    message_text = (
        f"📦 Начата ревизия номер {session_number} от {created_at_str} "
        f"с кодом доступа {session.pin_code}, выберите категорию для учета:"
    )
    await message.answer(message_text, reply_markup=keyboard)
