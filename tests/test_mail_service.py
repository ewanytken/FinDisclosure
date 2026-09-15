import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, Mock

import sys
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.service.mail_service import MailService


@pytest.fixture
def mock_config():
    return {
        "mail": {
            "host": "smtp.test.com",
            "port": 587,
            "username": "user@test.com",
            "password": "secret",
            "sender": "user@test.com",
            "use_tls": False,
        }
    }


@pytest.fixture
def service(mock_config):
    with patch("app.service.mail_service.Utils.get_config_file", return_value=mock_config):
        yield MailService()


@pytest.mark.asyncio
class TestMailService:

    async def test_send_message_success(self, service):
        """Test sending a plain message."""
        with patch("app.service.mail_service.aiosmtplib.send", new=AsyncMock()) as mock_send:
            result = await service.send_message(
                to="recipient@example.com",
                subject="Hello",
                body="Hi there",
            )

        assert result is True
        mock_send.assert_awaited_once()
        message = mock_send.call_args[0][0]
        assert message["To"] == "recipient@example.com"
        assert message["Subject"] == "Hello"
        assert message["From"] == "user@test.com"

    async def test_send_message_failure(self, service):
        """Test that failures return False."""
        with patch(
            "app.service.mail_service.aiosmtplib.send",
            new=AsyncMock(side_effect=Exception("SMTP down")),
        ):
            result = await service.send_message(
                to="recipient@example.com",
                subject="Hello",
                body="Hi",
            )

        assert result is False

    async def test_send_html_message(self, service):
        """Test HTML body handling."""
        with patch("app.service.mail_service.aiosmtplib.send", new=AsyncMock()) as mock_send:
            await service.send_message(
                to="x@y.com",
                subject="HTML",
                body="<h1>Hi</h1>",
                html=True,
            )

        message = mock_send.call_args[0][0]
        # Should be multipart with text fallback + HTML alternative
        assert message.is_multipart()

    async def test_send_file_attachment(self, service, tmp_path):
        """Test file attachment."""
        file = tmp_path / "hello.txt"
        file.write_text("hello world")

        with patch("app.service.mail_service.aiosmtplib.send", new=AsyncMock()) as mock_send:
            result = await service.send_file(
                to="x@y.com",
                subject="File",
                file_path=file,
                body="See attached.",
            )

        assert result is True
        message = mock_send.call_args[0][0]
        attachments = [
            part for part in message.walk() if part.get_content_disposition() == "attachment"
        ]
        assert len(attachments) == 1
        assert attachments[0].get_filename() == "hello.txt"

    async def test_missing_attachment_returns_false(self, service):
        """Test that a missing attachment does not raise."""
        with patch("app.service.mail_service.aiosmtplib.send", new=AsyncMock()):
            result = await service.send_file(
                to="x@y.com",
                subject="Missing",
                file_path="/does/not/exist.pdf",
            )
        assert result is False

    async def test_multiple_recipients(self, service):
        """Test that a list of recipients is joined correctly."""
        with patch("app.service.mail_service.aiosmtplib.send", new=AsyncMock()) as mock_send:
            await service.send_message(
                to=["a@x.com", "b@x.com"],
                subject="Multi",
                body="Hi",
                cc="c@x.com",
            )

        message = mock_send.call_args[0][0]
        assert message["To"] == "a@x.com, b@x.com"
        assert message["Cc"] == "c@x.com"

    async def test_send_bulk_concurrently(self, service):
        """Test bulk sending."""
        with patch("app.service.mail_service.aiosmtplib.send", new=AsyncMock()):
            messages = [
                {"to": f"u{i}@x.com", "subject": "Hi", "body": "Hello"}
                for i in range(5)
            ]
            results = await service.send_bulk(messages, max_concurrent=2)

        assert all(results)
        assert len(results) == 5