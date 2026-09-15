from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
  pass

class CompanyModel(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(50), nullable=True)
    name = Column(String(255), nullable=False)
    inn = Column(String(50), nullable=True)
    isin = Column(String(50), nullable=True)

    def __repr__(self) -> str:
        return (f"<Company: (id={self.id}, "
                f"ticker='{self.ticker}', "
                f"name='{self.name}', "
                f"inn='{self.inn}', "
                f"isin='{self.isin}')>")

    def get_id(self) -> Optional[int]:
        return self.id

    def get_ticker(self) -> Optional[str]:
        return self.ticker

    def get_name(self) -> Optional[str]:
        return self.name

    def get_inn(self) -> Optional[str]:
        return self.inn

    def get_isin(self) -> Optional[str]:
        return self.isin


class QuestionModel(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text(10000), nullable=False)

    def __repr__(self) -> str:
        return (f"<Question: (id={self.id}, "
                f"question='{self.question}')>")

    def get_id(self) -> Optional[int]:
        return self.id

    def get_question(self) -> Optional[str]:
        return self.question

