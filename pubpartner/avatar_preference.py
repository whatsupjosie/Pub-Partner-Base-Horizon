"""User-driven avatar selection with a capability-based degrade ladder.

Per-user design decision (not this module's to second-guess): the avatar
that shows up is whatever the user picked, at the tier their preferences
say, for whatever vignette/context they're in — a puppy skin in a dog-avatar
room, an 8-bit skin in an 8-bit world, otherwise their base design. If they
never configured anything, or their preferred tier can't actually run right
now, this module degrades to the next tier down the ladder
(PHOTOREAL -> STYLIZED -> STILL) rather than failing outright, and reports
whether that happened so the caller can show the "this version of your
avatar couldn't run" popup.

What this module does NOT do: probe real device capability (GPU, memory,
network) or synthesize a missing tier from another one ("cloning" a
photoreal avatar down to a stylized one automatically). `can_run` is a
caller-supplied predicate — plug in a real hardware probe when one exists.
Without one, every configured tier is assumed runnable and only a genuinely
missing/unset asset triggers degradation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Tuple

from .companion_mode import AvatarTier, CapabilitySet, CompanionMode

# PHOTOREAL degrades to STYLIZED degrades to STILL. STILL has no further
# fallback — it's a static image, there's nothing below it.
_DEGRADE_LADDER: Dict[AvatarTier, Optional[AvatarTier]] = {
    AvatarTier.PHOTOREAL: AvatarTier.STYLIZED,
    AvatarTier.STYLIZED: AvatarTier.STILL,
    AvatarTier.STILL: None,
}


@dataclass(frozen=True)
class AvatarAsset:
    tier: AvatarTier
    asset_ref: str
    # None = the user's generic/base look. A specific value (e.g. "dog_world",
    # "8bit_world") overrides the generic look only inside that vignette.
    vignette_id: Optional[str] = None


@dataclass(frozen=True)
class AvatarPreferences:
    """One user's avatar configuration.

    base_thumbnail is the only required asset — the still image the user
    designed alongside their avatar, used as the guaranteed final fallback.
    default_tier is the tier the user asked to run at by default; None means
    the user never expressed a preference, in which case video calls use
    the still thumbnail per the user's own stated default (no preference
    picked -> no reason to assume a heavier tier is wanted).
    """

    base_thumbnail: AvatarAsset
    default_tier: Optional[AvatarTier] = None
    assets: Tuple[AvatarAsset, ...] = field(default_factory=tuple)

    def __post_init__(self):
        if self.base_thumbnail.tier is not AvatarTier.STILL:
            raise ValueError("base_thumbnail must be tier=STILL — it's the guaranteed fallback")


@dataclass(frozen=True)
class AvatarResolution:
    asset: AvatarAsset
    tier_used: AvatarTier
    requested_tier: AvatarTier
    degraded: bool
    notify_user: bool
    reason: Optional[str] = None


def _find_asset(preferences: AvatarPreferences, tier: AvatarTier, vignette_id: Optional[str]) -> Optional[AvatarAsset]:
    if tier is AvatarTier.STILL and vignette_id is None:
        # Guaranteed present, see AvatarPreferences.base_thumbnail.
        candidate = preferences.base_thumbnail
        return candidate
    for asset in preferences.assets:
        if asset.tier is tier and asset.vignette_id == vignette_id:
            return asset
    # No vignette-specific asset at this tier -> fall back to the user's
    # generic look at the same tier before dropping a tier.
    if vignette_id is not None:
        for asset in preferences.assets:
            if asset.tier is tier and asset.vignette_id is None:
                return asset
    if tier is AvatarTier.STILL:
        return preferences.base_thumbnail
    return None


def resolve_avatar(
    preferences: AvatarPreferences,
    *,
    video_call: bool = False,
    vignette_id: Optional[str] = None,
    can_run: Callable[[AvatarTier], bool] = lambda tier: True,
) -> AvatarResolution:
    """Pick which avatar asset to show right now.

    No configured default_tier goes straight to the still thumbnail — most
    explicitly called out for video calls, but applied generally: there's no
    reason to guess the user wants a heavier tier they never asked for.
    `video_call` is accepted for callers that want to log/branch on context;
    it does not change the tier decision itself.
    """
    del video_call  # accepted for caller context/logging only, see docstring
    requested_tier = (
        AvatarTier.STILL if preferences.default_tier is None else preferences.default_tier
    )

    tier: Optional[AvatarTier] = requested_tier
    while tier is not None:
        asset = _find_asset(preferences, tier, vignette_id)
        if asset is not None and can_run(tier):
            degraded = tier is not requested_tier
            return AvatarResolution(
                asset=asset,
                tier_used=tier,
                requested_tier=requested_tier,
                degraded=degraded,
                notify_user=degraded and preferences.default_tier is not None,
                reason=(
                    None
                    if not degraded
                    else f"{requested_tier.value} unavailable, degraded to {tier.value}"
                ),
            )
        tier = _DEGRADE_LADDER[tier]

    # Unreachable in practice: STILL always resolves via base_thumbnail,
    # which __post_init__ guarantees exists and can_run defaults to True.
    raise RuntimeError("no runnable avatar tier found, including the guaranteed still thumbnail")


def link_aware_can_run(
    capabilities: CapabilitySet,
    *,
    bake_reachable: Callable[[], bool] = lambda: True,
) -> Callable[[AvatarTier], bool]:
    """A `can_run` predicate for resolve_avatar() that reflects how PHOTOREAL
    avatars actually get produced: server-side voxel baking (see
    reference/avatar_foundry/), never on-device compute.

    - STILL: always runnable, it's a static image.
    - STYLIZED: runnable on both Base and Horizon — this is each mode's own
      lighter rendering tier, not something that needs a bake service.
    - PHOTOREAL: runnable on Base always (it *is* the bake service host).
      On Horizon, only when linked to a reachable Base/bake service AND that
      service reports a finished bake is actually available right now —
      never "can this phone's hardware do the sculpt," because it can't and
      was never meant to.

    `bake_reachable` is a caller-supplied check for "is a finished bake
    actually downloadable right now" (e.g. a federation query against the
    linked Base) — this function does not perform that query itself, it
    only decides when the question is even worth asking.
    """

    def can_run(tier: AvatarTier) -> bool:
        if tier is AvatarTier.STILL or tier is AvatarTier.STYLIZED:
            return True
        # tier is PHOTOREAL
        if capabilities.mode is CompanionMode.BASE:
            return True
        return capabilities.linked and bake_reachable()

    return can_run
