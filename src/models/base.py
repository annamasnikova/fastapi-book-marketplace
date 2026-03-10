from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    # created_at: Mapped[datetime] = mapped_column(default_factory=datetime.now)
    pass