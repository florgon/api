"""
    Database model for ticket.
"""

from sqlalchemy.sql import func
from sqlalchemy import String, Integer, ForeignKey, DateTime, Column
from app.database.core import Base


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    text = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String(18), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=False)
    subject = Column(String, nullable=False)

    # Time
    time_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
