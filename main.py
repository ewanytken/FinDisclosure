import asyncio

from app.core.constructor_facade import ConstructorFacade
from app.logger.logger_wrapper import LoggerWrapper

logger = LoggerWrapper()

async def main():

    logger("[main_f]: Disclosure Company starting")
    try:
        await ConstructorFacade().run()
    except KeyboardInterrupt:
        logger("[main_f:interrupted_err]: Interrupted by user")
    finally:
        logger("[main_f]: Disclosure Monitor stopped")


if __name__ == "__main__":
    asyncio.run(main())