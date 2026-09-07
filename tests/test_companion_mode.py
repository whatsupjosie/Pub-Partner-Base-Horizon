import pytest

from pubpartner.companion_mode import (
    AnimationLevel,
    AvatarTier,
    CompanionMode,
    DORMANT_WHEN_LINKED,
    resolve_capabilities,
)


def test_base_is_always_full_capability_and_never_dormant():
    caps = resolve_capabilities(CompanionMode.BASE)
    assert caps.studio_equipment is True
    assert caps.avatar_tier is AvatarTier.PHOTOREAL
    assert caps.animation_level is AnimationLevel.FULL
    assert caps.dormant_features == frozenset()
    assert caps.linked is False


def test_base_ignores_linked_argument_it_is_never_a_slave():
    # Base's behavior does not change based on whether a Horizon is attached.
    assert resolve_capabilities(CompanionMode.BASE, linked=True) == resolve_capabilities(
        CompanionMode.BASE, linked=False
    )


def test_horizon_standalone_is_lighter_but_fully_active():
    caps = resolve_capabilities(CompanionMode.HORIZON, linked=False)
    assert caps.studio_equipment is False
    assert caps.avatar_tier is AvatarTier.STYLIZED
    assert caps.animation_level is AnimationLevel.LIGHT
    assert caps.dormant_features == frozenset()
    for feature in DORMANT_WHEN_LINKED:
        assert caps.is_active(feature)


def test_horizon_linked_defers_reasoning_and_state_features():
    caps = resolve_capabilities(CompanionMode.HORIZON, linked=True)
    assert caps.linked is True
    for feature in DORMANT_WHEN_LINKED:
        assert caps.is_dormant(feature)
        assert not caps.is_active(feature)


def test_horizon_linked_still_runs_device_local_capture():
    # Camera/mic capture and local display aren't in the dormant set —
    # there's no "Base's camera" to defer to.
    caps = resolve_capabilities(CompanionMode.HORIZON, linked=True)
    assert caps.video_call is True
    assert caps.voice_io is True


def test_horizon_never_gets_studio_equipment_linked_or_not():
    assert resolve_capabilities(CompanionMode.HORIZON, linked=False).studio_equipment is False
    assert resolve_capabilities(CompanionMode.HORIZON, linked=True).studio_equipment is False


def test_horizon_avatar_tier_and_animation_unaffected_by_link_state():
    # Rendering tier is a local-hardware capability, not a reasoning
    # concern, so it does not change when a Base link appears.
    unlinked = resolve_capabilities(CompanionMode.HORIZON, linked=False)
    linked = resolve_capabilities(CompanionMode.HORIZON, linked=True)
    assert unlinked.avatar_tier == linked.avatar_tier == AvatarTier.STYLIZED
    assert unlinked.animation_level == linked.animation_level == AnimationLevel.LIGHT
