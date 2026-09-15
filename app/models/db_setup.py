import contextlib
from typing import Optional, Dict, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine

from app.logger.logger_wrapper import LoggerWrapper
from app.models.models import Base
from app.utils import Utils

logger = LoggerWrapper()

class DataBaseService:

    def __init__(self):
        self.config: Optional[Dict] = Utils.get_config_file()

        self.engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None

    def set_config(self, config: Dict) -> None:
        self.config = config

    async def init_session(self) -> None:
        try:
            DATABASE_URL = self.config.get("database", {}).get("url")
            logger(f"Database URL: {DATABASE_URL}")

            self.engine = create_async_engine(DATABASE_URL, echo=True)
            self._session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            async with self.engine.connect() as conn:
                async with conn.begin():
                    await conn.run_sync(Base.metadata.create_all)

            logger("Database initialized successfully")

        except Exception as e:
            logger(f"Database connection error: {e}")

    async def close_session(self) -> None:
        try:
            if self.engine:
                await self.engine.dispose()
        except Exception as e:
            logger(f"Database disconnection error: {e}")

    @contextlib.asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if not self._session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
                logger("Session committed successfully")
            except Exception as e:
                await session.rollback()
                logger(f"Session rolled back due to error: {e}")
                raise
            finally:
                await session.close()
