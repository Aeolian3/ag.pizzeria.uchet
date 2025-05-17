from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import *
from models.inv_session import InventoryFrequency
from utils.pin_code import generate_unique_pin


async def create_inventory_session(
    db: AsyncSession,
    telegram_id: int,
    frequency: InventoryFrequency
) -> InventorySession:

    user = await db.scalar(select(User).where(User.telegram_id == telegram_id))

    if not user:
        raise ValueError("Пользователь не найден")

    if user.role_id not in [2, 3]:
        raise PermissionError("Недостаточно прав для создания сессии")

    if isinstance(frequency, str):
        frequency = InventoryFrequency(frequency)

    organization_id = await set_user_organization(db, telegram_id)

    result = await db.execute(select(func.max(InventorySession.id)))
    max_id = result.scalar_one() or 0
    new_id = max_id + 1

    if new_id > 999999:
        raise ValueError("Достигнут предел количества сессий")

    pin_code = await generate_unique_pin(db)

    session = InventorySession(
        id=new_id,
        pin_code=pin_code,
        status="active",
        creator_id=user.id,
        organization_id=organization_id,
        frequency=frequency.value
    )

    db.add(session)

    session_user = InventoryUser(
        session_id=new_id,
        user_id=user.id,
    )
    db.add(session_user)

    await db.commit()
    await db.refresh(session)

    return session


async def get_categories_by_organization(db: AsyncSession, organization_id: int):
    result = await db.execute(select(Category).where(Category.organization_id == organization_id))
    return result.scalars().all()

async def get_products_by_category(db: AsyncSession, category_id: int):
    result = await db.execute(
        select(Product, Unit.name.label("unit_name"))
        .join(Unit, Product.unit_id == Unit.id)
        .where(Product.category_id == category_id)
        .order_by(Product.name)
    )
    return result.all()


async def set_user_organization(db: AsyncSession, telegram_id: int) -> int:
    user = await db.scalar(select(User).where(User.telegram_id == telegram_id))

    if not user:
        raise ValueError("Пользователь не найден")

    organization_id = user.organization_id
    return organization_id

async def get_user_id_by_telegram_id(session: AsyncSession, telegram_id: int) -> int | None:
    stmt = select(User.id).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user_id = result.scalar_one_or_none()
    return user_id

async def check_product_in_session(db: AsyncSession, session_id: int, product_id: int):
    result = await db.execute(
        select(InventoryProduct, User)
        .join(User, InventoryProduct.user_id == User.id)
        .where(InventoryProduct.session_id == session_id, InventoryProduct.product_id == product_id)
    )
    return result.all()

async def format_inventory_summary(session_id: int, db: AsyncSession) -> str:
    # Получаем все продукты сессии и суммы по каждому пользователю
    result = await db.execute(
        select(
            InventoryProduct.product_id,
            Product.name,
            InventoryProduct.user_id,
            User.first_name,
            InventoryProduct.quantity
        )
        .join(Product, InventoryProduct.product_id == Product.id)
        .join(User, InventoryProduct.user_id == User.id)
        .where(InventoryProduct.session_id == session_id)
    )
    records = result.all()

    # Группируем по продуктам
    products = {}
    for product_id, product_name, user_id, tg_username, quantity in records:
        if product_id not in products:
            products[product_id] = {
                "name": product_name,
                "total_qty": 0,
                "users": []
            }
        products[product_id]["total_qty"] += quantity
        products[product_id]["users"].append((tg_username or "unknown", quantity))

    # Формируем текст
    lines = []
    for product in products.values():
        lines.append(f"🔹 {product['name']} в кол. {product['total_qty']:.2f} шт.")
        for username, qty in product["users"]:
            lines.append(f"    Пользователем @{username} — {qty:.2f} шт.")
        lines.append("")  # пустая строка для разделения

    if not lines:
        return "В этой сессии пока нет добавленных продуктов."

    return "\n".join(lines)
