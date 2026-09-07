# Avatar Foundry — reference (Base-side, not built here)

These files are the user-provided PubCast "Avatar Foundry" UI: a dressing
room where a user uploads face/torso/arm/leg photos and the server bakes a
voxel avatar (`POST /api/avatars/me/bake`), plus identity/rig customization
saved via `POST /api/avatars/me`. Kept here as tracked reference, not copied
from an upload that could get lost — **not wired into `pubpartner/` yet.**

## Why this matters to the Base/Horizon split

The bake already happens server-side (`uploadToServer()` in
`avatar_foundry.html`, and again in `dressing.js`) — the browser only
uploads photos and polls progress, it never sculpts voxels itself. That
confirms the PHOTOREAL avatar tier in `pubpartner/avatar_preference.py` was
correctly modeled: it's not a "can this device compute it" question, it's a
"is a finished bake reachable" question. A voxel sculpt at up to 96³ per
body part, with normal/AO baking, has no business running on a phone, and
per this reference UI, it never was going to — even Base doesn't compute it
client-side.

Concretely, for Horizon: PHOTOREAL should only ever be runnable when linked
to a Base (or other bake service) that already has a finished bake to hand
over — never as an on-device compute path. See
`avatar_preference.link_aware_can_run()` for where that's now encoded.

## Not done here

- The dressing room UI itself is not integrated into this repo's runtime —
  it's PubCast/NowCurtsey-Build frontend code, a separate app.
- No code here actually calls `/api/avatars/me/bake` or receives its
  result — `link_aware_can_run()` only encodes *when* a PHOTOREAL asset is
  allowed to be considered runnable, not how the bake or its transfer to
  Horizon actually happens.
