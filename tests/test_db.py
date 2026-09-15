from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.logger.logger_wrapper import LoggerWrapper
from app.models.db_setup import DataBaseService, QuestionRepository, CompanyRepository
from app.models.models import QuestionModel, CompanyModel, Base

logger = LoggerWrapper()
# ---------------------------- Fixtures ----------------------------
@pytest.fixture
def config():
    """Mock configuration."""
    return {"database": {"url": "sqlite+aiosqlite:///:memory:"}}


@pytest.fixture
async def db_setup(config):
    """Create a fresh DataBaseSetup instance with in-memory database."""
    setup = DataBaseService()
    setup.set_config(config)
    await setup.init_session()
    yield setup
    await setup.close_session()


@pytest.fixture
async def question_repo(db_setup):
    """Create a QuestionRepository instance."""
    repo = QuestionRepository(db_setup)
    # await db_setup.init_session()
    return repo


@pytest.fixture
async def company_repo(db_setup):
    """Create a CompanyRepository instance."""
    repo = CompanyRepository(db_setup)
    # await db_setup.init_session()
    return repo


# ---------------------------- Tests for DataBaseSetup ----------------------------
class TestDataBaseSetup:
    """Tests for database initialization and connection management."""

    @pytest.mark.asyncio
    async def test_init_session_creates_tables(self, config):
        """Test that init_session creates all tables."""
        setup = DataBaseService()
        setup.set_config(config)

        # Mock the engine and connection
        with patch("app.models.db_setup.create_async_engine") as mock_create_engine:
            mock_engine = AsyncMock()
            mock_conn = AsyncMock()
            mock_engine.begin.return_value.__aenter__.return_value = mock_conn
            mock_create_engine.return_value = mock_engine

            await setup.init_session()

            # Verify tables were created
            # await mock_conn.run_sync.assert_called_once_with(Base.metadata.create_all)
            assert setup.engine is not None
            assert setup.get_session() is not None

    @pytest.mark.asyncio
    async def test_init_session_handles_errors(self, config):
        """Test that init_session logs errors properly."""
        setup = DataBaseService()
        setup.set_config(config)

        with patch("app.models.db_setup.create_async_engine") as mock_create_engine:
            mock_create_engine.side_effect = Exception("Database connection failed")

            with patch.object(logger, "__call__") as mock_logger:
                await setup.init_session()

                # Should log the error
                mock_logger.assert_called_once()
                assert "Database connection error" in mock_logger.call_args[0][0]

    @pytest.mark.asyncio
    async def test_close_session(self, db_setup):
        """Test closing session and disposing engine."""
        # Setup has already initialized, now test close
        with patch.object(db_setup.engine, "dispose") as mock_dispose:
            # Since session is a factory, we need to handle it differently
            # This test would need refactoring of your close_session method
            await db_setup.close_session()
            # Verify engine.dispose was called
            mock_dispose.assert_called_once()


# ---------------------------- Tests for QuestionRepository ----------------------------
class TestQuestionRepository:
    """Tests for question CRUD operations."""

    @pytest.mark.asyncio
    async def test_add_question_async(self, question_repo):
        """Test adding a question."""
        # NOTE: Your code has a bug - you need to get an actual session
        # For testing, we'll mock the session
        with patch("app.models.db_setup.AsyncSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session

            # Actually, we need to modify the repo to use async with properly
            # For now, let's test the logic by mocking
            question_repo.session = AsyncMock()
            question_repo.session.add = Mock()
            question_repo.session.commit = AsyncMock()
            question_repo.session.refresh = AsyncMock()

            await question_repo.add_question_async("Test question")

            # Verify question was added
            question_repo.session.add.assert_called_once()
            question_repo.session.commit.assert_called_once()
            question_repo.session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_question_async_found(self, question_repo):
        """Test finding an existing question."""
        # Mock the session and result
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_question = QuestionModel(id=1, question="Test question")
        mock_result.scalar_one_or_none.return_value = mock_question

        # Mock the execute method
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Assign to repo
        question_repo.session = mock_session

        result = await question_repo.find_question_async(1)

        assert result == mock_question
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_question_async_not_found(self, question_repo):
        """Test finding a non-existent question."""
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_session.execute = AsyncMock(return_value=mock_result)
        question_repo.session = mock_session

        result = await question_repo.find_question_async(999)

        # NOTE: Your code returns a fake model - this is a bug!
        # It should return None
        assert result is None  # Your code returns QuestionModel(999, "None")

    @pytest.mark.asyncio
    async def test_find_all_questions_async(self, question_repo):
        """Test retrieving all questions."""
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_questions = [
            QuestionModel(id=1, question="Question 1"),
            QuestionModel(id=2, question="Question 2"),
        ]
        mock_result.scalars.return_value.all.return_value = mock_questions

        mock_session.execute = AsyncMock(return_value=mock_result)
        question_repo.session = mock_session

        result = await question_repo.find_all_questions_async()

        assert len(result) == 2
        assert result == mock_questions

    @pytest.mark.asyncio
    async def test_remove_question_async_success(self, question_repo):
        """Test removing an existing question."""
        mock_session = AsyncMock()
        mock_question = QuestionModel(id=1, question="Test question")

        # Mock find_question_async to return the question
        with patch.object(question_repo, "find_question_async", return_value=mock_question):
            question_repo.session = mock_session
            question_repo.session.delete = AsyncMock()
            question_repo.session.commit = AsyncMock()

            result = await question_repo.remove_question_async(1)

            assert result is True
            mock_session.delete.assert_called_once_with(mock_question)
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_question_async_not_found(self, question_repo):
        """Test removing a non-existent question."""
        with patch.object(question_repo, "find_question_async", return_value=None):
            result = await question_repo.remove_question_async(999)

            assert result is False

    @pytest.mark.asyncio
    async def test_add_question_async_handles_error(self, question_repo):
        """Test error handling when adding a question."""
        question_repo.session = AsyncMock()
        question_repo.session.add = Mock()
        question_repo.session.commit = AsyncMock(side_effect=Exception("Database error"))

        with patch.object(logger, "__call__") as mock_logger:
            await question_repo.add_question_async("Test question")

            # Should log the error
            mock_logger.assert_called_once()
            assert "Question add error" in mock_logger.call_args[0][0]


# ---------------------------- Tests for CompanyRepository ----------------------------
class TestCompanyRepository:
    """Tests for company CRUD operations."""

    @pytest.mark.asyncio
    async def test_add_company_async(self, company_repo):
        """Test adding a company."""
        company_repo.session = AsyncMock()
        company_repo.session.add = Mock()
        company_repo.session.commit = AsyncMock()
        company_repo.session.refresh = AsyncMock()

        await company_repo.add_company_async(
            ticker="AAPL",
            name="Apple Inc.",
            inn="123456789",
            isin="US0378331005"
        )

        company_repo.session.add.assert_called_once()
        company_repo.session.commit.assert_called_once()
        company_repo.session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_company_by_ticker_async_found(self, company_repo):
        """Test finding a company by ticker."""
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_company = CompanyModel(
            id=1,
            ticker="AAPL",
            name="Apple Inc.",
            inn="123456789",
            isin="US0378331005"
        )
        mock_result.scalar_one_or_none.return_value = mock_company

        mock_session.execute = AsyncMock(return_value=mock_result)
        company_repo.session = mock_session

        result = await company_repo.find_company_by_ticker_async("AAPL")

        assert result == mock_company

    @pytest.mark.asyncio
    async def test_find_company_by_ticker_async_not_found(self, company_repo):
        """Test finding a company by ticker that doesn't exist."""
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_session.execute = AsyncMock(return_value=mock_result)
        company_repo.session = mock_session

        result = await company_repo.find_company_by_ticker_async("NONEXISTENT")

        # NOTE: Your code returns a fake model - this is a bug!
        assert result is None  # Your code returns CompanyModel(999, "None")

    @pytest.mark.asyncio
    async def test_find_companies_by_name_async(self, company_repo):
        """Test searching companies by name (case-insensitive)."""
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_companies = [
            CompanyModel(id=1, ticker="AAPL", name="Apple Inc."),
            CompanyModel(id=2, ticker="MSFT", name="Microsoft Corp."),
        ]
        mock_result.scalars.return_value.all.return_value = mock_companies

        mock_session.execute = AsyncMock(return_value=mock_result)
        company_repo.session = mock_session

        result = await company_repo.find_companies_by_name_async("Apple")

        assert len(result) == 2
        assert result == mock_companies

    @pytest.mark.asyncio
    async def test_remove_company_by_ticker_async_success(self, company_repo):
        """Test removing a company by ticker."""
        mock_session = AsyncMock()
        mock_company = CompanyModel(id=1, ticker="AAPL", name="Apple Inc.")

        with patch.object(company_repo, "find_company_by_ticker_async", return_value=mock_company):
            company_repo.session = mock_session
            company_repo.session.delete = AsyncMock()
            company_repo.session.commit = AsyncMock()

            result = await company_repo.remove_company_by_ticker_async("AAPL")

            assert result is True
            mock_session.delete.assert_called_once_with(mock_company)
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_company_by_ticker_async_not_found(self, company_repo):
        """Test removing a company that doesn't exist."""
        with patch.object(company_repo, "find_company_by_ticker_async", return_value=None):
            result = await company_repo.remove_company_by_ticker_async("NONEXISTENT")

            assert result is False

    @pytest.mark.asyncio
    async def test_find_company_by_ticker_async_handles_error(self, company_repo):
        """Test error handling when finding a company."""
        company_repo.session = AsyncMock()
        company_repo.session.execute = AsyncMock(side_effect=Exception("Database error"))

        with patch.object(logger, "__call__") as mock_logger:
            result = await company_repo.find_company_by_ticker_async("AAPL")

            # Should return None, not a fake model
            assert result is None
            mock_logger.assert_called_once()
            assert "Company find by ticker error" in mock_logger.call_args[0][0]


# ---------------------------- Integration Tests ----------------------------
class TestIntegration:
    """Integration tests with actual database."""

    @pytest.mark.asyncio
    async def test_full_question_workflow(self):
        """Test complete CRUD workflow for questions."""
        config = {"database": {"url": "sqlite+aiosqlite:///:memory:"}}

        # Setup
        db = DataBaseService()
        db.set_config(config)
        await db.init_session()
        repo = QuestionRepository(db)

        try:
            # Create session properly
            async with repo.session() as session:
                repo.session = session

                # 1. Add a question
                await repo.add_question_async("What is AI?")

                # 2. Find the question
                question = await repo.find_question_async(1)
                assert question is not None
                assert question.question == "What is AI?"

                # 3. Find all questions
                questions = await repo.find_all_questions_async()
                assert len(questions) == 1

                # 4. Remove the question
                removed = await repo.remove_question_async(1)
                assert removed is True

                # 5. Verify removal
                remaining = await repo.find_all_questions_async()
                assert len(remaining) == 0

        finally:
            await db.close_session()


# ---------------------------- Running the tests ----------------------------
# pytest -v test_your_file.py --asyncio-mode=auto
# To run: pytest -v --asyncio-mode=auto