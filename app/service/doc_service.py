import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from app.logger.logger_wrapper import LoggerWrapper
from app.utils import Utils

logger = LoggerWrapper()

class DocWriterService:

    def __init__(self) -> None:
        config = Utils.get_config_file()
        doc_cfg = config.get("doc_writer", {})

        self.output_dir = Path(doc_cfg.get("output_dir"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger(f"DocWriterService initialized: output_dir={self.output_dir}")

    async def save_answers(self,
        pairs: List[tuple[Optional[str], str]],
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None) -> Optional[Path]:

        try:
            file_path = self._resolve_path(filename)
            document = self._build_document(pairs, metadata)

            await asyncio.to_thread(document.save, file_path)

            logger(f"Saved document: {file_path}")
            return file_path
        except Exception as e:
            logger(f"Failed to save document: {e}")
            return None


    def _resolve_path(self, filename: Optional[str]) -> Path:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"company_digest_{timestamp}"

        if not filename.lower().endswith(".docx"):
            filename += ".docx"

        return self.output_dir / filename

    def _build_document(self,
        pairs: List[tuple[Optional[str], str]],
        metadata: Optional[Dict[str, str]]) -> Document:

        document = Document()

        self._add_title(document)
        if metadata:
            self._add_metadata(document, metadata)

        for index, (question, answer) in enumerate(pairs, start=1):
            if question:
                self._add_question(document, index, question)
            self._add_answer(document, answer)

        return document

    @staticmethod
    def _add_title(document: Document) -> None:
        title = document.add_heading("Company Digest", level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    @staticmethod
    def _add_metadata(document: Document, metadata: Dict[str, str]) -> None:
        for key, value in metadata.items():
            paragraph = document.add_paragraph()
            run = paragraph.add_run(f"{key}: {value}")
            run.italic = True
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(0x60, 0x60, 0x60)

    @staticmethod
    def _add_question(document: Document, index: int, question: str) -> None:
        heading = document.add_heading(f"Q{index}. {question}", level=2)
        heading.alignment = WD_ALIGN_PARAGRAPH.LEFT

    @staticmethod
    def _add_answer(document: Document, answer: str) -> None:
        for line in answer.split("\n"):
            if line.strip():
                document.add_paragraph(line)