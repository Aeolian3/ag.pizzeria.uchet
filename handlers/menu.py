from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Начать ревизию", callback_data="start_inventory")],
        [InlineKeyboardButton(text="Присоединиться к ревизии", callback_data="join_inventory")],
        [InlineKeyboardButton(text="Завершенные ревизии", callback_data="finished_inventory")],
        [InlineKeyboardButton(text="Отмененные ревизии", callback_data="cancelled_inventory")],
    ]
)

async def create_category_keyboard(categories, session_id: int | None = None):
    keyboard = [
        [InlineKeyboardButton(text=category.name, callback_data=f"select_category_{category.id}")]
        for category in categories
    ]

    action_buttons = [
        InlineKeyboardButton(text="Отменить ревизии", callback_data="cancel_inventory"),
        InlineKeyboardButton(text="Завершить ревизии", callback_data="finish_inventory"),
    ]

    if session_id:
        action_buttons.insert(0, InlineKeyboardButton(
            text="Сформировать ведомость",
            callback_data=f"export_inventory_{session_id}"
        ))

    keyboard.append(action_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

frequency_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Дневная", callback_data="frequency:daily")],
    [InlineKeyboardButton(text="Недельная", callback_data="frequency:weekly")],
    [InlineKeyboardButton(text="Месячная", callback_data="frequency:monthly")],
    [InlineKeyboardButton(text="Назад", callback_data="to_main_menu")],
])
