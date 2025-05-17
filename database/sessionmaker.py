from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from .engine import engine

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as db:
        yield db
