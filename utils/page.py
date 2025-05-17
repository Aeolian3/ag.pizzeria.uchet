from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from database.reposotory import get_products_by_category

PRODUCTS_PER_PAGE = 7


async def send_product_page(callback_query: CallbackQuery, state: FSMContext, db: AsyncSession):
    data = await state.get_data()
    category_id = data["category_id"]
    page = data.get("page", 1)

    products = await get_products_by_category(db, category_id)

    if not products:
        await callback_query.message.edit_text(
            "В этой категории нет продуктов.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад к категориям", callback_data="back_to_categories")]
            ])
        )
        return

    total_pages = max(1, (len(products) - 1) // PRODUCTS_PER_PAGE + 1)
    page = min(max(1, page), total_pages)
    start = (page - 1) * PRODUCTS_PER_PAGE
    end = start + PRODUCTS_PER_PAGE
    products_page = products[start:end]

    buttons = []
    for product, unit_name in products_page:
        buttons.append([
            InlineKeyboardButton(
                text=f"{product.name} ({unit_name})",
                callback_data=f"select_product_{product.id}"
            )
        ])

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="page_prev"))
    nav_buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="current_page"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Вперед", callback_data="page_next"))

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([InlineKeyboardButton(text="🔙 Назад к категориям", callback_data="back_to_categories")])

    await callback_query.message.edit_text(
        "Выберите продукт для инвентаризации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

    await state.update_data(page=page)