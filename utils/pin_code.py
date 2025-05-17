import random
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import InventorySession

async def generate_unique_pin(db: AsyncSession) -> int:
    while True:
        pin = random.randint(100000, 999999)
        result = await db.execute(
            select(InventorySession).where(InventorySession.pin_code == pin)
        )
        if not result.scalar():
            return pin
