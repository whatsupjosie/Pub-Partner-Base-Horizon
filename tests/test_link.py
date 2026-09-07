from pathlib import Path

from pubpartner.companion_mode import CompanionMode
from pubpartner.link import LinkSession
from pubpartner.pubpartner_federation.engine import SyncEngine
from pubpartner.pubpartner_federation.identity import NodeIdentity
from pubpartner.pubpartner_federation.store import SyncStore


def make_session(tmp_path: Path, node_id: str, role: str) -> LinkSession:
    identity = NodeIdentity(node_id=node_id, role=role, created_at=0.0)
    engine = SyncEngine(node_id, SyncStore(tmp_path / f"{node_id}.db"))
    return LinkSession(identity, engine)


def sync(a: LinkSession, b: LinkSession) -> None:
    """Exchange presence changes both directions, like two real nodes would
    over whatever transport carries pubpartner_federation envelopes."""
    b.engine.receive(a.engine.envelope())
    a.engine.receive(b.engine.envelope())


def test_horizon_alone_is_not_linked(tmp_path):
    horizon = make_session(tmp_path, "phone-1", "portable")
    horizon.heartbeat()
    assert horizon.is_linked_to_base() is False


def test_horizon_sees_fresh_base_heartbeat_and_becomes_linked(tmp_path):
    base = make_session(tmp_path, "studio-1", "resident")
    horizon = make_session(tmp_path, "phone-1", "portable")

    now = 1_000.0
    base.heartbeat(now=now)
    horizon.heartbeat(now=now)
    sync(base, horizon)

    assert horizon.is_linked_to_base(now=now) is True


def test_base_never_reports_linked_to_itself(tmp_path):
    base = make_session(tmp_path, "studio-1", "resident")
    other_base = make_session(tmp_path, "studio-2", "resident")
    now = 1_000.0
    base.heartbeat(now=now)
    other_base.heartbeat(now=now)
    sync(base, other_base)

    # Base's own is_linked_to_base() is defined to always be False —
    # Base is never a dormant slave to anything.
    assert base.is_linked_to_base(now=now) is False


def test_stale_base_heartbeat_does_not_count_as_linked(tmp_path):
    base = make_session(tmp_path, "studio-1", "resident")
    horizon = make_session(tmp_path, "phone-1", "portable")

    base.heartbeat(now=0.0)
    horizon.heartbeat(now=0.0)
    sync(base, horizon)

    later = 0.0 + horizon.heartbeat_timeout_seconds + 1.0
    assert horizon.is_linked_to_base(now=later) is False


def test_horizon_ignores_other_horizons_for_link_status(tmp_path):
    horizon_a = make_session(tmp_path, "phone-1", "portable")
    horizon_b = make_session(tmp_path, "phone-2", "portable")
    now = 1_000.0
    horizon_a.heartbeat(now=now)
    horizon_b.heartbeat(now=now)
    sync(horizon_a, horizon_b)

    assert horizon_a.is_linked_to_base(now=now) is False


def test_capabilities_reflect_live_link_state(tmp_path):
    base = make_session(tmp_path, "studio-1", "resident")
    horizon = make_session(tmp_path, "phone-1", "portable")
    now = 1_000.0

    assert horizon.capabilities(now=now).linked is False

    base.heartbeat(now=now)
    horizon.heartbeat(now=now)
    sync(base, horizon)

    caps = horizon.capabilities(now=now)
    assert caps.linked is True
    assert caps.is_dormant("personality_reasoning")
    assert caps.is_active("video_call") or caps.video_call  # device-local, stays on


def test_mode_derives_from_identity_role(tmp_path):
    base = make_session(tmp_path, "studio-1", "resident")
    horizon = make_session(tmp_path, "phone-1", "portable")
    assert base.mode is CompanionMode.BASE
    assert horizon.mode is CompanionMode.HORIZON
