from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class MeasurementDB(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=False, index=True)

    latency_ms = Column(Float, nullable=False)
    jitter_ms = Column(Float, nullable=False)
    download_mbps = Column(Float, nullable=False)
    upload_mbps = Column(Float, nullable=True)

    failed_requests = Column(Integer, nullable=False, default=0)
    total_requests = Column(Integer, nullable=False)
    packet_loss_pct = Column(Float, nullable=False)
    measurement_duration_s = Column(Float, nullable=False)

    device_type = Column(String, nullable=True)
    network_type = Column(String, nullable=True)

    client_timestamp = Column(DateTime, nullable=True)
    server_timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )


class NetworkProfileDB(Base):
    """
    Red identificada manualmente por un usuario.

    Ejemplos:
    - WiFi Casa
    - Oficina Piso 3
    - Datos móviles
    """

    __tablename__ = "network_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        String,
        nullable=False,
        index=True,
    )

    name = Column(
        String(60),
        nullable=False,
    )

    normalized_name = Column(
        String(60),
        nullable=False,
    )

    network_type = Column(
        String(32),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    sessions = relationship(
        "NetworkSessionDB",
        back_populates="network_profile",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "normalized_name",
            name="uq_network_profiles_user_name",
        ),
    )


class NetworkSessionDB(Base):
    """
    Relación entre un session_id generado por Angular y un perfil de red.
    """

    __tablename__ = "network_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        String,
        nullable=False,
        index=True,
    )

    session_id = Column(
        String(100),
        nullable=False,
        index=True,
    )

    network_profile_id = Column(
        Integer,
        ForeignKey(
            "network_profiles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    started_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    network_profile = relationship(
        "NetworkProfileDB",
        back_populates="sessions",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "session_id",
            name="uq_network_sessions_user_session",
        ),
    )