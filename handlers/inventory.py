import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import BufferedInputFile, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from template.report import create_inventory_report

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("export_inventory_"))
async def handle_export_inventory(callback_query: CallbackQuery, db: AsyncSession):
    try:
        session_id = int(callback_query.data.split("_")[-1])
        excel_file = await create_inventory_report(session_id, db)

        await callback_query.message.answer_document(
            document=BufferedInputFile(
                excel_file.getvalue(),
                filename=f"Ревизия_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            ),
        )
        await callback_query.answer()

    except Exception as e:
        logger.error(f"Error exporting inventory: {e}", exc_info=True)
        await callback_query.answer("Ошибка при экспорте", show_alert=True)