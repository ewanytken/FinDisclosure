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
            logger(f"[DataBaseService_c:init_session_f:database_url_v]: {DATABASE_URL}")

            self.engine = create_async_engine(DATABASE_URL, echo=True)
            self._session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            async with self.engine.connect() as conn:
                async with conn.begin():
                    await conn.run_sync(Base.metadata.create_all)

            logger(f"[DataBaseService_c:init_session_f:engine_init]: Database initialized successfully")

        except Exception as e:
            logger(f"[DataBaseService_c:init_session_f:db_init_err]: {e}")

    async def close_session(self) -> None:
        try:
            if self.engine:
                await self.engine.dispose()
        except Exception as e:
            logger(f"[DataBaseService_c:init_session_f:db_close_err]: {e}")

    @contextlib.asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if not self._session_factory:
            raise RuntimeError("[DataBaseService_c:get_session_f]: DB not initialized. Call init_session() first.")

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
                logger(f"[DataBaseService_c:get_session_f:session_init]: Session committed successfully")
            except Exception as e:
                await session.rollback()
                logger(f"[DataBaseService_c:get_session_f:session_err]: Session rolled back due to error: {e}")
                raise
            finally:
                await session.close()
