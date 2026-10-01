import os

import pytest

from app.core.constructor_facade import ConstructorFacade


@pytest.mark.asyncio
class Test:

    async def test_document_processing(self):
        facade = ConstructorFacade()

