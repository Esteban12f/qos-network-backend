from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.future_database_models import Base
import app.repositories.measurements_repository as repo_module


@pytest.fixture
def repo(monkeypatch):
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    test_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    monkeypatch.setattr(repo_module, "SessionLocal", test_session_local)

    return repo_module.MeasurementsRepository()


def _measurement(session_id: str) -> dict:
    return {
        "session_id": session_id,
        "latency_ms": 10.0,
        "jitter_ms": 1.0,
        "download_mbps": 50.0,
        "upload_mbps": 10.0,
        "failed_requests": 0,
        "total_requests": 10,
        "packet_loss_pct": 0.0,
        "measurement_duration_s": 5.0,
        "device_type": "desktop",
        "network_type": "wifi",
        "client_timestamp": datetime.now(timezone.utc),
        "server_timestamp": datetime.now(timezone.utc),
    }


def test_same_session_id_different_users_are_isolated(repo):
    repo.save(user_id="user-a", session_id="shared-session", measurement=_measurement("shared-session"))
    repo.save(user_id="user-b", session_id="shared-session", measurement=_measurement("shared-session"))

    history_a = repo.get_history("user-a", "shared-session")
    history_b = repo.get_history("user-b", "shared-session")

    assert len(history_a) == 1
    assert len(history_b) == 1
    assert history_a[0]["user_id"] == "user-a"
    assert history_b[0]["user_id"] == "user-b"


def test_get_latest_scoped_by_user(repo):
    repo.save(user_id="user-a", session_id="s1", measurement=_measurement("s1"))

    assert repo.get_latest("user-a", "s1") is not None
    assert repo.get_latest("user-b", "s1") is None


def test_count_and_exists_scoped_by_user(repo):
    repo.save(user_id="user-a", session_id="s1", measurement=_measurement("s1"))

    assert repo.count("user-a", "s1") == 1
    assert repo.count("user-b", "s1") == 0
    assert repo.exists("user-a", "s1") is True
    assert repo.exists("user-b", "s1") is False


def test_clear_session_only_deletes_requesting_users_rows(repo):
    repo.save(user_id="user-a", session_id="s1", measurement=_measurement("s1"))
    repo.save(user_id="user-b", session_id="s1", measurement=_measurement("s1"))

    deleted = repo.clear_session("user-a", "s1")

    assert deleted is True
    assert repo.exists("user-a", "s1") is False
    assert repo.exists("user-b", "s1") is True


def test_clear_all_only_clears_requesting_users_rows(repo):
    repo.save(user_id="user-a", session_id="s1", measurement=_measurement("s1"))
    repo.save(user_id="user-b", session_id="s2", measurement=_measurement("s2"))

    repo.clear_all("user-a")

    assert repo.exists("user-a", "s1") is False
    assert repo.exists("user-b", "s2") is True


def test_get_all_session_ids_scoped_by_user(repo):
    repo.save(user_id="user-a", session_id="s1", measurement=_measurement("s1"))
    repo.save(user_id="user-a", session_id="s2", measurement=_measurement("s2"))
    repo.save(user_id="user-b", session_id="s3", measurement=_measurement("s3"))

    assert sorted(repo.get_all_session_ids("user-a")) == ["s1", "s2"]
    assert repo.get_all_session_ids("user-b") == ["s3"]
