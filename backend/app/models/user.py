from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base


class User(Base):
    """
    User entity for WeatherGPT authentication and role-based access.
    Stores name, unique email, salted hashed password, role, and preferred regional language.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(512), nullable=False)
    role = Column(String(50), default="citizen", nullable=False)  # citizen, disaster_officer, researcher
    preferred_language = Column(String(10), default="en", nullable=False)  # en, bn, hi
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User id={self.id} email='{self.email}' role='{self.role}'>"
