from typing import Optional
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class DocumentPack(Base, TimestampMixin):
    __tablename__ = "document_packs"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # 'pack-foundation', 'pack-numerical-mastery'
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    desc: Mapped[str] = mapped_column(Text, nullable=False)
    tag: Mapped[str] = mapped_column(String(50), nullable=False)  # 'Nhập môn', 'Chuyên sâu'
    level: Mapped[str] = mapped_column(String(100), nullable=False)  # 'Dành cho người mới', 'Ứng tuyển MT'
    pages: Mapped[str] = mapped_column(String(50), nullable=False)  # '45 trang PDF'
    download_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
