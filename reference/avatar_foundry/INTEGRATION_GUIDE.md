# Avatar Foundry Integration — CORRECT VERSION

## What This Actually Is

The dressing room now has **TWO** mirrors:

1. **Makeup Mirror** (left side) — Your original avatar customization area
2. **Full-Length Mirror** (center) — New! With a pleasant white wooden stage in front of it

The **foundry platform appears on the wooden stage** when you activate it.

---

## Room Layout

```
┌─────────────────┬─────────────────┬──────────────┐
│  MAKEUP MIRROR  │ FULL-LENGTH     │  WARDROBE    │
│                 │    MIRROR       │   PANEL      │
│  (Avatar        │                 │              │
│   Preview)      │  With wooden    │  (Controls)  │
│                 │    stage        │              │
│  [Presets]      │                 │              │
│                 │  [⬡ Activate]   │              │
└─────────────────┴─────────────────┴──────────────┘
```

---

## How It Works

### Default State
- Makeup mirror shows your avatar preview (left)
- Full-length mirror with pleasant white wooden stage (center)
- Wardrobe panel with customizer controls (right)
- Button below stage: **"⬡ Activate Forge"**

### When Foundry is Activated
1. Wooden stage fades out
2. Sci-fi foundry platform fades in on the same spot
3. Platform has: glowing grid floor, floating skeleton, plasma effects
4. Wardrobe panel switches to foundry controls (photo upload, bake, etc.)
5. Button changes to: **"← Return to Stage"**

### When Deactivated
1. Foundry platform fades out
2. Wooden stage fades back in
3. Wardrobe panel returns to avatar customizer
4. Everything back to default

---

## Key Features

### Wooden Stage (Pleasant White)
- Painted white wood matching the warm room aesthetic
- Simple platform design with support beams
- Warm cream/beige color palette
- Matches the room from your beautiful image

### Foundry Platform (Sci-Fi)
- Dark void background
- Glowing plasma grid floor
- Floating MoCap skeleton
- Sci-fi platform with corner accents
- Cyan/orange color scheme

### Photo Bake System
- Face photo required, torso optional
- Drag-and-drop or click to upload
- Quality selector: SURFACE / TRACK / ORBITAL
- Fine Voxel Face toggle (2× res for face)
- Progress bar with real-time forge log
- Calls `/api/avatars/me/bake` endpoint

### Three-Tab Panel (Foundry Mode)
- **BAKE** — Upload photos, set quality, forge avatar
- **IDENTITY** — Name, gender, mood, glow color
- **RIG** — Placeholder for CS-1 skeleton

---

## Installation

Replace these three files in your `static/` directory:

```
static/
  dressing.html  ← Full layout with both mirrors
  dressing.css   ← Styles for warm room + sci-fi foundry
  dressing.js    ← Stage ↔ foundry transition logic
```

**No backend changes needed.** Uses existing `/api/avatars/me/bake` endpoint.

---

## User Flow

1. User enters dressing room
2. Sees makeup mirror (left) and full-length mirror with white stage (center)
3. Clicks **"⬡ Activate Forge"** below the stage
4. Wooden stage fades out, foundry platform fades in
5. Wardrobe panel switches to foundry controls
6. User uploads face photo (required)
7. Selects quality and options
8. Clicks **"⬡ FORGE AVATAR"**
9. Progress bar shows bake steps
10. Real API call to server
11. Stats display with voxel count
12. Clicks **"← Return to Stage"** when done
13. Platform fades out, wooden stage returns

---

## Design Details

### Room Aesthetic (Default)
- Warm cream/beige background
- White wooden stage painted in pleasant white
- Soft shadows and natural lighting feel
- Matches the cozy dressing room from your image

### Foundry Aesthetic (Activated)
- Dark sci-fi void
- Plasma cyan (#00d4ff) glow effects
- Forge orange (#ff6b1a) accents
- Floating skeleton animation
- Grid floor with perspective

### Transitions
- 400ms fade between stage and platform
- Smooth opacity transitions
- Panel content switches instantly
- No jarring layout shifts

---

## The Fix

**What was wrong before:** I put the foundry platform where your makeup mirror was, thinking there was only one mirror.

**What's correct now:** 
- Makeup mirror stays on the left (your original setup)
- Full-length mirror added in the center (new)
- Pleasant white wooden stage in front of full-length mirror
- Foundry platform appears ON the wooden stage when activated

The wooden stage is the standing area in front of the full-length mirror — exactly like in your beautiful dressing room image. When you activate the forge, the sci-fi platform materializes on that stage.

---

**Ready to deploy.** 🎯
