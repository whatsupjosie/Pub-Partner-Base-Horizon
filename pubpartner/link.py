"""Base<->Horizon link detection, built on the federation sync engine.

This does not invent a new transport. It reuses `pubpartner_federation`'s
SyncEngine/SyncStore (already used for manuscript sync) to carry a small
heartbeat entity between nodes: each node periodically upserts its own
presence record, and a Horizon node is "linked" exactly when it can see a
recent, live presence record from a 'resident' (Base) node.

Nothing here decides what a link *means* for feature behavior — that policy
lives in companion_mode.resolve_capabilities(). This module only answers
one question: is a reachable Base peer heartbeating right now.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from .companion_mode import CapabilitySet, CompanionMode, resolve_capabilities
from .pubpartner_federation.engine import SyncEngine
from .pubpartner_federation.identity import NodeIdentity
from .pubpartner_federation.store import SyncStore

PRESENCE_ENTITY_TYPE = "link_presence"

_ROLE_TO_MODE = {
    "resident": CompanionMode.BASE,
    "portable": CompanionMode.HORIZON,
}


@dataclass(frozen=True)
class PeerPresence:
    node_id: str
    role: str
    last_seen: float

    def is_fresh(self, now: float, timeout_seconds: float) -> bool:
        return (now - self.last_seen) <= timeout_seconds


class LinkSession:
    """One node's view of who else is present, over a shared SyncStore.

    In production the two nodes' stores are the same logical dataset kept
    in sync by SyncEngine.apply()/export_changes() over whatever transport
    (HTTP, LAN discovery, etc.) `pubpartner_federation.service` exposes —
    that transport wiring is separate work, not built here. This class only
    needs a SyncEngine bound to *some* store that both nodes' presence
    changes eventually land in.
    """

    DEFAULT_HEARTBEAT_TIMEOUT_SECONDS = 15.0

    def __init__(
        self,
        identity: NodeIdentity,
        engine: SyncEngine,
        heartbeat_timeout_seconds: float = DEFAULT_HEARTBEAT_TIMEOUT_SECONDS,
    ):
        self.identity = identity
        self.engine = engine
        self.heartbeat_timeout_seconds = heartbeat_timeout_seconds

    @property
    def mode(self) -> CompanionMode:
        return _ROLE_TO_MODE[self.identity.role]

    def heartbeat(self, now: Optional[float] = None) -> None:
        """Announce this node is alive. Call this on a timer while running."""
        self.engine.upsert(
            PRESENCE_ENTITY_TYPE,
            self.identity.node_id,
            {"role": self.identity.role, "last_seen": now if now is not None else time.time()},
        )

    def known_peers(self, now: Optional[float] = None) -> list[PeerPresence]:
        now = now if now is not None else time.time()
        peers = []
        for entity in self.engine.store.all_entities():
            if entity.entity_type != PRESENCE_ENTITY_TYPE or entity.deleted:
                continue
            if entity.entity_id == self.identity.node_id:
                continue
            peers.append(
                PeerPresence(
                    node_id=entity.entity_id,
                    role=str(entity.fields.get("role", "")),
                    last_seen=float(entity.fields.get("last_seen", 0.0)),
                )
            )
        return peers

    def is_linked_to_base(self, now: Optional[float] = None) -> bool:
        """True only for a Horizon node with a live, fresh Base peer.
        Always False for a Base node — Base never defers to anything."""
        if self.mode is not CompanionMode.HORIZON:
            return False
        now = now if now is not None else time.time()
        return any(
            peer.role == "resident" and peer.is_fresh(now, self.heartbeat_timeout_seconds)
            for peer in self.known_peers(now)
        )

    def capabilities(self, now: Optional[float] = None) -> CapabilitySet:
        return resolve_capabilities(self.mode, linked=self.is_linked_to_base(now))
