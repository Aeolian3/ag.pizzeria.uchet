from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from utils.page import send_product_page

router = Router()

@router.callback_query(F.data.startswith("select_category_"))
async def handle_category_selection(callback_query: CallbackQuery, state: FSMContext, db: AsyncSession):
    category_id = int(callback_query.data.split("_")[-1])
    await state.update_data(category_id=category_id, page=1)

    await send_product_page(callback_query, state, db)


