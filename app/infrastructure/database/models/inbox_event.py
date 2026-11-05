from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.db import Base


class InboxEventModel(Base):
    __tablename__ = "inbox_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    topic: Mapped[str] = mapped_column(nullable=False)
    partition: Mapped[int] = mapped_column(nullable=False)
    offset: Mapped[int] = mapped_column(nullable=False)

    UniqueConstraint("topic", "partition", "offset", name="uq_inbox_event_source")
