import pytest

from pubpartner.avatar_preference import (
    AvatarAsset,
    AvatarPreferences,
    link_aware_can_run,
    resolve_avatar,
)
from pubpartner.companion_mode import AvatarTier, resolve_capabilities, CompanionMode


def make_thumbnail():
    return AvatarAsset(tier=AvatarTier.STILL, asset_ref="thumb.png")


def test_no_preference_defaults_to_still_thumbnail():
    prefs = AvatarPreferences(base_thumbnail=make_thumbnail())
    result = resolve_avatar(prefs, video_call=True)
    assert result.tier_used is AvatarTier.STILL
    assert result.asset.asset_ref == "thumb.png"
    assert result.degraded is False
    assert result.notify_user is False


def test_no_preference_defaults_to_still_outside_video_call_too():
    prefs = AvatarPreferences(base_thumbnail=make_thumbnail())
    result = resolve_avatar(prefs, video_call=False)
    assert result.tier_used is AvatarTier.STILL


def test_preferred_tier_used_when_runnable():
    prefs = AvatarPreferences(
        base_thumbnail=make_thumbnail(),
        default_tier=AvatarTier.STYLIZED,
        assets=(AvatarAsset(tier=AvatarTier.STYLIZED, asset_ref="stylized.glb"),),
    )
    result = resolve_avatar(prefs)
    assert result.tier_used is AvatarTier.STYLIZED
    assert result.degraded is False
    assert result.notify_user is False


def test_degrades_and_notifies_when_preferred_tier_cannot_run():
    prefs = AvatarPreferences(
        base_thumbnail=make_thumbnail(),
        default_tier=AvatarTier.PHOTOREAL,
        assets=(
            AvatarAsset(tier=AvatarTier.PHOTOREAL, asset_ref="photoreal.glb"),
            AvatarAsset(tier=AvatarTier.STYLIZED, asset_ref="stylized.glb"),
        ),
    )
    result = resolve_avatar(prefs, can_run=lambda tier: tier is not AvatarTier.PHOTOREAL)
    assert result.tier_used is AvatarTier.STYLIZED
    assert result.requested_tier is AvatarTier.PHOTOREAL
    assert result.degraded is True
    assert result.notify_user is True
    assert "photoreal" in result.reason and "stylized" in result.reason


def test_degrades_all_the_way_to_still_when_nothing_else_configured():
    prefs = AvatarPreferences(
        base_thumbnail=make_thumbnail(),
        default_tier=AvatarTier.PHOTOREAL,
        assets=(AvatarAsset(tier=AvatarTier.PHOTOREAL, asset_ref="photoreal.glb"),),
    )
    result = resolve_avatar(prefs, can_run=lambda tier: tier is AvatarTier.STILL)
    assert result.tier_used is AvatarTier.STILL
    assert result.notify_user is True


def test_degrades_when_tier_can_run_but_no_asset_configured_for_it():
    # default_tier=STYLIZED but the user never actually designed a stylized
    # asset -> should fall to STILL, not crash.
    prefs = AvatarPreferences(base_thumbnail=make_thumbnail(), default_tier=AvatarTier.STYLIZED)
    result = resolve_avatar(prefs)
    assert result.tier_used is AvatarTier.STILL
    assert result.degraded is True
    assert result.notify_user is True


def test_vignette_specific_skin_overrides_generic_look():
    prefs = AvatarPreferences(
        base_thumbnail=make_thumbnail(),
        default_tier=AvatarTier.STYLIZED,
        assets=(
            AvatarAsset(tier=AvatarTier.STYLIZED, asset_ref="generic.glb"),
            AvatarAsset(tier=AvatarTier.STYLIZED, asset_ref="puppy.glb", vignette_id="dog_world"),
        ),
    )
    result = resolve_avatar(prefs, vignette_id="dog_world")
    assert result.asset.asset_ref == "puppy.glb"


def test_vignette_without_specific_skin_falls_back_to_generic_look():
    prefs = AvatarPreferences(
        base_thumbnail=make_thumbnail(),
        default_tier=AvatarTier.STYLIZED,
        assets=(AvatarAsset(tier=AvatarTier.STYLIZED, asset_ref="generic.glb"),),
    )
    result = resolve_avatar(prefs, vignette_id="8bit_world")
    assert result.asset.asset_ref == "generic.glb"
    assert result.degraded is False


def test_base_thumbnail_must_be_still_tier():
    with pytest.raises(ValueError):
        AvatarPreferences(
            base_thumbnail=AvatarAsset(tier=AvatarTier.STYLIZED, asset_ref="oops.glb")
        )


def photoreal_prefs():
    return AvatarPreferences(
        base_thumbnail=make_thumbnail(),
        default_tier=AvatarTier.PHOTOREAL,
        assets=(
            AvatarAsset(tier=AvatarTier.PHOTOREAL, asset_ref="photoreal.glb"),
            AvatarAsset(tier=AvatarTier.STYLIZED, asset_ref="stylized.glb"),
        ),
    )


def test_base_can_always_run_photoreal():
    caps = resolve_capabilities(CompanionMode.BASE)
    result = resolve_avatar(photoreal_prefs(), can_run=link_aware_can_run(caps))
    assert result.tier_used is AvatarTier.PHOTOREAL
    assert result.degraded is False


def test_horizon_unlinked_cannot_run_photoreal_degrades_to_stylized():
    caps = resolve_capabilities(CompanionMode.HORIZON, linked=False)
    result = resolve_avatar(photoreal_prefs(), can_run=link_aware_can_run(caps))
    assert result.tier_used is AvatarTier.STYLIZED
    assert result.degraded is True
    assert result.notify_user is True


def test_horizon_linked_with_reachable_bake_can_run_photoreal():
    caps = resolve_capabilities(CompanionMode.HORIZON, linked=True)
    can_run = link_aware_can_run(caps, bake_reachable=lambda: True)
    result = resolve_avatar(photoreal_prefs(), can_run=can_run)
    assert result.tier_used is AvatarTier.PHOTOREAL
    assert result.degraded is False


def test_horizon_linked_but_bake_not_yet_reachable_degrades():
    caps = resolve_capabilities(CompanionMode.HORIZON, linked=True)
    can_run = link_aware_can_run(caps, bake_reachable=lambda: False)
    result = resolve_avatar(photoreal_prefs(), can_run=can_run)
    assert result.tier_used is AvatarTier.STYLIZED
    assert result.degraded is True


def test_stylized_and_still_always_runnable_regardless_of_link():
    for linked in (True, False):
        caps = resolve_capabilities(CompanionMode.HORIZON, linked=linked)
        can_run = link_aware_can_run(caps, bake_reachable=lambda: False)
        assert can_run(AvatarTier.STYLIZED) is True
        assert can_run(AvatarTier.STILL) is True
