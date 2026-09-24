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
            "to": ["user@test.com"]
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
                subject="Hello",
                body="Hi there",
            )

        assert result is True
        mock_send.assert_awaited_once()
        message = mock_send.call_args[0][0]
        assert message["To"] == "user@test.com"
        assert message["Subject"] == "Hello"
        assert message["From"] == "user@test.com"

    async def test_send_message_failure(self, service):
        """Test that failures return False."""
        with patch(
            "app.service.mail_service.aiosmtplib.send",
            new=AsyncMock(side_effect=Exception("SMTP down")),
        ):
            result = await service.send_message(
                subject="Hello",
                body="Hi",
            )

        assert result is False

    async def test_send_html_message(self, service):
        """Test HTML body handling."""
        with patch("app.service.mail_service.aiosmtplib.send", new=AsyncMock()) as mock_send:
            await service.send_message(
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
                subject="File",
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
                subject="Missing",
            )
        assert result is False


