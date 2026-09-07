import pytest

from pubpartner.avatar_preference import (
    AvatarAsset,
    AvatarPreferences,
    resolve_avatar,
)
from pubpartner.companion_mode import AvatarTier


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
