from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)

    # 🆕 标签字段（新增）
    tags: Mapped[str] = mapped_column(default="", nullable=False)