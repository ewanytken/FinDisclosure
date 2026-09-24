import mimetypes
from email.message import EmailMessage
from pathlib import Path
from typing import List, Optional, Union

import aiosmtplib

from app.logger.logger_wrapper import LoggerWrapper
from app.utils import Utils

logger = LoggerWrapper()

class MailService:

    def __init__(self) -> None:
        config = Utils.get_config_file()
        mail_cfg = config.get("mail", {})

        self.host: str = mail_cfg.get("host", "no_host_config")
        self.port: int = int(mail_cfg.get("port", 465))
        self.username: Optional[str] = mail_cfg.get("username")
        self.password: Optional[str] = mail_cfg.get("password")
        self.sender: str = mail_cfg.get("sender", self.username)
        self.use_tls: bool = bool(mail_cfg.get("use_tls", False))
        self.to: Union[str, List[str]] = mail_cfg.get("to")

        self.attachments: Optional[List[Union[str, Path]]] = None

        logger(
            f"[MailService_c:initialized]:\n"
            f"host={self.host},\n"
            f"port={self.port},\n"
            f"sender={self.sender},\n"
            f"tls={self.use_tls}"
        )

    def set_attachments(self, attachments: Optional[List[Union[str, Path]]]) -> None:
        self.attachments = attachments

    async def send_message(self,
        subject: str,
        body: str,
        html: bool = False,
        timeout: float = 30.0) -> bool:

        try:
            message = self._build_message(
                subject=subject,
                body=body,
                html=html,
            )
            await self._send(message, timeout=timeout)
            logger(f"[MailService_c:send_message_f:to_v]: {self.to} with subject '{subject}'")
            return True

        except Exception as e:
            logger(f"[MailService_c:send_message_f:_send_err]: {e}")
            return False

    async def send_file(self, subject: str, body: str = "", html: bool = False, timeout: float = 30.0) -> bool:

        return await self.send_message(
            subject=subject,
            body=body,
            html=html,
            timeout=timeout,
        )

    def _build_message(self, subject: str, body: str, html: bool) -> EmailMessage:

        message = EmailMessage()
        message["From"] = self.sender
        message["To"] = self._join_addresses(self.to)
        message["Subject"] = subject

        if html:
            message.set_content("Your email client does not support HTML.")
            message.add_alternative(body, subtype="html")
        else:
            message.set_content(body)

        if self.attachments:
            for path in self.attachments:
                self._attach_file(message, Path(path))

        return message

    def _attach_file(self, message: EmailMessage, path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f"[MailService_c:_attach_file_f:path_err]: {path}")

        mime_type, _ = mimetypes.guess_type(path.name)
        maintype, subtype = (mime_type or "application/octet-stream").split("/", 1)

        with path.open("rb") as f:
            message.add_attachment(
                f.read(),
                maintype=maintype,
                subtype=subtype,
                filename=path.name,
            )

    async def _send(self, message: EmailMessage, timeout: float) -> None:
        await aiosmtplib.send(
            message,
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls,          # True for port 465, False for 587
            start_tls=not self.use_tls,    # STARTTLS on port 587
            timeout=timeout,
        )

    @staticmethod
    def _join_addresses(addresses: Union[str, List[str]]) -> str:
        if isinstance(addresses, str):
            return addresses
        return ", ".join(addresses)