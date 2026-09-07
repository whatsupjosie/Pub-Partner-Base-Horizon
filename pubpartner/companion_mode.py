"""Shared capability policy for PubPartner Base and PubPartner Horizon.

Base and Horizon are the same program, running the same `pubpartner` core
(cartridge, memory, prompt assembly, sequencer, federation sync). They are
not two codebases that happen to talk to each other — this module is what
lets them stay one codebase while still behaving differently:

- **Base** is the resident install, wired directly into PubCast. It always
  runs at full capability: studio equipment, photoreal avatar rendering,
  full animation, everything.
- **Horizon** is the portable install (phone-class hardware). Standalone,
  it runs its own lighter version of the same features — no studio
  equipment (that never existed on Horizon, linked or not), a stylized
  avatar instead of photoreal, light animation instead of full.
- **Horizon, linked to a reachable Base** — the case this module exists
  for — goes further: features that are about *which mind is deciding*
  (personality reasoning, memory writes, collaborative-writing pacing,
  group-chat routing) go dormant locally and mirror Base's state instead,
  so the two never reason independently and drift apart. Features that are
  inherently local to the device (camera/mic capture, local display of
  whatever avatar frame it was handed) stay active regardless of link
  state, because there is no "Base's camera" to defer to.

Nothing in this module talks to the network. It is pure policy: given a
mode and a link state, what should be active, and what should be dormant.
`link.py` is what decides whether the link state is true; this module is
what that decision means.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import FrozenSet


class CompanionMode(str, Enum):
    """Which install this process is. Maps 1:1 onto the federation
    module's NodeIdentity.role ('resident' == BASE, 'portable' == HORIZON)
    — see link.py."""

    BASE = "base"
    HORIZON = "horizon"


class AvatarTier(str, Enum):
    PHOTOREAL = "photoreal"
    STYLIZED = "stylized"


class AnimationLevel(str, Enum):
    FULL = "full"
    LIGHT = "light"


# Features that go dormant on a linked Horizon. Each one is a decision-making
# or state-owning concern, not a device-local capture/render concern — see
# module docstring for why that distinction is the one that matters.
DORMANT_WHEN_LINKED: FrozenSet[str] = frozenset(
    {
        "personality_reasoning",
        "memory_writes",
        "collaborative_writing_pacing",
        "group_chat_routing",
    }
)

# Features Horizon never has, linked or not — these are studio-only, tied to
# hardware/rendering load a phone can't and shouldn't carry.
NEVER_ON_HORIZON: FrozenSet[str] = frozenset({"studio_equipment"})


@dataclass(frozen=True)
class CapabilitySet:
    mode: CompanionMode
    linked: bool
    studio_equipment: bool
    avatar_tier: AvatarTier
    animation_level: AnimationLevel
    video_call: bool
    voice_io: bool
    group_chat: bool
    collaborative_writing: bool
    vignette_scenes: bool
    # Feature names currently deferring to a linked peer instead of running
    # their own logic locally. Always empty for BASE — Base is never a
    # dormant slave to anything; it's the thing Horizon defers to.
    dormant_features: FrozenSet[str] = field(default_factory=frozenset)

    def is_dormant(self, feature: str) -> bool:
        return feature in self.dormant_features

    def is_active(self, feature: str) -> bool:
        """A feature is active if this install can run it at all, and it
        isn't currently deferring to a linked peer."""
        if feature == "studio_equipment":
            return self.studio_equipment
        return feature not in self.dormant_features


def resolve_capabilities(mode: CompanionMode, linked: bool = False) -> CapabilitySet:
    """The one place this policy is decided. Both the Base adapter and the
    Horizon adapter call this — neither hardcodes its own capability list.

    `linked` means: a live PubPartner Base peer is currently reachable and
    heartbeating (see link.LinkSession.is_linked_to_base()). It is always
    False for mode=BASE — Base doesn't change behavior based on whether a
    Horizon is attached to it; Horizon changes behavior based on whether a
    Base is attached to it.
    """
    if mode is CompanionMode.BASE:
        return CapabilitySet(
            mode=mode,
            linked=False,
            studio_equipment=True,
            avatar_tier=AvatarTier.PHOTOREAL,
            animation_level=AnimationLevel.FULL,
            video_call=True,
            voice_io=True,
            group_chat=True,
            collaborative_writing=True,
            vignette_scenes=True,
            dormant_features=frozenset(),
        )

    # HORIZON
    dormant = DORMANT_WHEN_LINKED if linked else frozenset()
    return CapabilitySet(
        mode=mode,
        linked=linked,
        studio_equipment=False,
        avatar_tier=AvatarTier.STYLIZED,
        animation_level=AnimationLevel.LIGHT,
        video_call=True,
        voice_io=True,
        group_chat=True,
        collaborative_writing=True,
        vignette_scenes=True,
        dormant_features=dormant,
    )
