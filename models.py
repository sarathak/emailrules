from sqlalchemy import String, DateTime, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Email(Base):
    __tablename__ = 'emails'
    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[str] = mapped_column(String(50), unique=True)
    sender: Mapped[str] = mapped_column(String(200), index=True)
    subject: Mapped[str] = mapped_column(String(200), index=True)
    received_at = Column(DateTime, index=True)

    def __repr__(self) -> str:
        return f'Email({self.message_id})'
