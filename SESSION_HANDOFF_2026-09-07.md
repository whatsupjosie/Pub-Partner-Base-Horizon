# Session Handoff — 2026-09-07

Read this whole file before doing anything else. It exists so a new chat can
pick up this project without re-deriving what this session already
established. Everything in here was independently verified (tests run,
files read, repos cloned) unless explicitly marked "unverified" or "claimed."

---

## 1. The Vision (what we're building, in the user's words)

**PubPartner Horizon** = a portable AI companion. Core promise: carry a
**cartridge** (a small file holding personality + long-term memory + voice +
avatar skins) to any computer, open a chat window, and it's the same
companion — same memory, same personality — everywhere.

Required pieces (per the user, verbatim intent):
- No full studio suite needed for Horizon — it should stay lightweight.
- Must support basic camera/mic controls (Zoom-call-like).
- Must use **PEQ** (probabilistic emotional-intelligence engine) for emotional
  reasoning.
- Must use a **provider neutralizer/humanizer**: normalize output from any
  LLM backend (Claude, GPT, Gemini, Ollama, etc.) into one consistent
  personality voice/cadence/vocabulary — translate "cold neutral reasoning"
  into the companion's specific quirks without changing content/intent.
- Multiple avatar skins per cartridge (8-bit, PubCast-native, etc.), each
  with motion tracking.
- Persistent, cross-session relationship data with other characters.
- Multi-avatar group chat — "weekly hangout" with several of the user's own
  cartridges in one conversation.
- Standalone 2.5D parallax **vignette** scenes — coffee shop, park,
  restaurant, living room, picnic, beach, office — each self-contained, NOT
  linked/navigable to each other (unlike PubCast's existing narrative room
  graph).
- Interactive props inside vignettes: TV (double-click → theater/fullscreen,
  plays YouTube), radio (Pandora or personal playlist), fireplace (ambient
  loop).
- **Collaborative writing mode**: AI writes ~1.5 pages at a time, then MUST
  stop and wait for the user to review/edit before continuing — forces
  actual review instead of walls of unreviewed AI text. The user believed
  this already existed and was surprised to learn (see §4) it was
  half-built, not done.
- Long-term architecture question (resolved, see §3): should Horizon feed a
  3D avatar to PubCast, sync to a PubCast home base, or run fully
  standalone? **Resolved: standalone lightweight app.** The point of
  Horizon is portability — "you can open up a chat window and have a chat
  with your avatar... that's the point." Full 3D/studio rendering stays in
  PubCast; Horizon gets a lighter vignette renderer later, by design, not
  as a lesser copy.

---

## 2. Repository Map — what's actually in each repo

The user's GitHub account has many repos; this session had these attached
(owner `whatsupjosie` throughout):

| Repo | Role | State |
|---|---|---|
| `NowCurtsey-Build` | Main PubCast assembly (main.py + modules/) | PR #2 open, see §5 |
| `Pub-Partner-Base-Horizon` | **New** shared-core PubPartner repo | Real code, 76/76 tests pass (see §4) |
| `Pubcaast-Breaking-Dawn` | A separate, more mature 3-service PubCast/PubPartner/2i stack | Verified working, see §4 |
| `The-Counter-and-2i` | Grab-bag of loose HTML prototypes + zips for 2i and Foresight UI | No unpacked source tree, mostly zips |
| `The-Prime` | Huge grab-bag dump repo — hundreds of loose files + ~15 zips | Contains Foresight v17/v18 + real Python backing |
| `6.0-`, `friday`, `Just-The-Pubcast`, `Pubcast-Phase-2-` | Attached, not yet substantively explored this session | Unknown state |

**Important:** several of these repos contain overlapping/duplicate attempts
at the same features, built in different sessions without cross-reference.
This handoff exists partly to stop that pattern.

---

## 3. Architecture Decisions Already Made This Session

1. **Horizon stays standalone/lightweight.** No studio modules (avatar
   mocap, choreography, voxel, recording, cameras_advanced, room_conductor,
   the Rust renderer) belong in Horizon. Those are PubCast-only.
2. **Feature-type split for the build plan** (chosen via a 3-solutions
   comparison — see that reasoning was: Option A "build in PubCast then
   port to Horizon" and Option B "build in Horizon then port to PubCast"
   both cause the exact duplication problem the user is trying to avoid;
   Option C won):
   - **Backend/logic features** (collaborative writing pacing, multi-avatar
     group chat) → build ONCE as shared core with zero app-specific
     imports, thin adapter per app (PubCast, Horizon). Never fork into two
     copies that drift.
   - **Graphics/rendering features** (vignette scenes, TV/radio/fireplace
     props) → build in PubCast first (it already has working parallax
     rendering — see `pubcast_room_layout.py`), then a deliberately
     *lighter*, not mirrored, version ports to Horizon later.
3. **Shared-core repo** for the backend/logic features is
   `Pub-Partner-Base-Horizon` (this repo) — the user pointed to it
   mid-session as the answer to "where does shared code live."

**Still unresolved — the most important open decision (see §6):** there
are three separate PubPartner implementations across the repo landscape
(this repo's `pubpartner/`, `NowCurtsey-Build`'s `pub_partner_chat.py`, and
`Pubcaast-Breaking-Dawn`'s `pubpartner_federation`). Before building the
collaborative-writing/group-chat features, these need to be compared
head-to-head and reconciled onto one foundation — otherwise we repeat the
exact "build it three times" problem this session was called out for.

---

## 4. Verification Log — what's real vs. claimed (the honesty audit)

This session's operating rule: **never report a doc's claims as fact
without independently running/reading the actual code.** Multiple things
turned out to be claimed-but-not-present, and multiple things turned out to
be real-but-undiscovered. Specifics:

### Pub-Partner-Base-Horizon (this repo) — VERIFIED REAL
- Was pushed as a lone handoff `.md` file first (no code) — a second
  fetch/pull revealed a zip (`pubpartner_portable_20260828.zip`) had landed
  on `origin/main` after the initial clone; the actual code was inside it.
- Extracted and unpacked into real tracked source (committed
  `700f0db "Unpack pubpartner_portable zip into real tracked source"`,
  pushed to `main`).
- **76/76 tests pass, run live.** Modules: `cartridge.py`, `memory_store.py`
  (persistence + relevance scoring), `prompt_assembler.py` + `tokenizer.py`
  (token-budgeted prompt assembly), `sequence_controller.py` (debounces
  rapid input into one turn, enforces min turn spacing, tracks idle state —
  stdlib-only, zero PubCast/VDI coupling, verified via AST import audit),
  `portable_runtime.py` (embeddable glue: `submit_input()` /
  `ready_for_turn()` / `run_turn()`).
- Clean one-directional dependency graph: cartridge layer never imports the
  sequencer, so either can be embedded independently.
- This is a genuinely solid foundation for the shared-core plan in §3.

### NowCurtsey-Build — PARTIALLY VERIFIED, PR #2 open
- `main.py` + `modules/` assembled from zips for the first time this repo
  ever had a runnable tree (per PR #2's own description).
- Confirmed (from earlier session work, not re-verified this pass): PEQ
  `sys.path` bug fixed, BOM bug fixed in 11 files, live ASGI boot
  confirmed, `/api/peq/observe` returns real (non-degraded) output.
- **PR #2 status as of last check:** open, `mergeable_state: clean`, no CI
  configured, all 4 review threads resolved (codex bot findings fixed and
  confirmed in commit `4e0ce67`). An hourly check-in Routine is watching
  this PR (`trig_01HwqdMPXLWgbLANjgQRDD2X`) — **a new chat should either
  keep that routine running or explicitly take over watching PR #2.**
- `pub_partner_chat.py` here handles ONE character per session — no group
  chat. Has a `same_as_studio` sentinel letting PubPartner's manager AI or
  any character share whatever AI is currently PubCast Studio's primary
  mind, or run independently — this pattern is worth reusing conceptually
  in the shared core.
- **"Collaborative AI-Infused Virtual Production" is literally just a
  FastAPI app description string** (`main.py` line ~1786) — not a feature.
  This is what led to the initial (wrong) claim that collaborative writing
  didn't exist anywhere — it doesn't exist *in this repo*, but does
  elsewhere (see below).

### The-Counter-and-2i — UI exists; integration proven in reference snapshot
- `2i_writers_room_v3.html` (in a zip) is a **working UI** for almost
  exactly the "collaborative writing, 1.5 pages then review" feature:
  locked manuscript, active buffer capped at ~450 words (~1-2 pages),
  auto-graduation when the cap is hit, manual Approve button, per-line
  pinning, chapter markers, full save/restore to `.2i` JSON files.
  - **INTEGRATION ALREADY PROVEN:** User provided reference snapshot
    `PubCast_2i_PubPartner_WORKING_20260816.zip` — a complete verified
    build from August 16 — that demonstrates real end-to-end integration:
    60 integration tests pass, 2i commits successfully to PubPartner, data
    is readable on the replica side (`test_commit_reaches_pubpartner_and_is_readable_there`).
    This is not theoretical; it's a shipped reference.
  - **Integration status:** The thin-adapter wiring between the UI and backend
    (2i-backend at Breaking-Dawn, or the federation service in the reference)
    is demonstrated and repeatable. The UI's chat stub needs to be replaced
    with the proven handshake pattern from the reference.
  - **Voice I/O status:** Speech synthesis (read-aloud) is wired via
    browser's `SpeechSynthesisUtterance` API with speed control (1–5 scale).
    Speech recognition (dictation) from the original prototype was not ported
    to v3 — it's a missing feature if needed.
- "Counter View" workspace shell = **Foresight UI** (see §4a below) — the
  handoff here (`8-10 HANDOFF_FINAL.md`) calls `foresight_ui_v19.html`
  "latest, use this" — **that exact file does not exist anywhere**, across
  every repo and ~50 zips checked this session. Treat "v19" as
  aspirational/a typo; the real successor is Breaking-Dawn's
  `static/foresight.html` (see below).

### The-Prime — huge dump repo, contains the most complete Foresight backing
- `foresight_ui_v17.html` + `v18.html`, PLUS real supporting Python not
  present anywhere else: `polygon_shape_library.py` (encodes tray-shape
  design rules as executable constraints — bans squares/rectangles/regular
  polygons, feathers perimeters, etc.), `polygonal_tray_engine.py`,
  `tray_requirements.py`, `wired_system.py`, and three real test files
  (`test_polygon_shape_library.py`, `test_polygonal_suite.py`,
  `test_comprehensive_wiring_audit.py`) — **not independently re-run this
  session**, flagged as a to-do.
- `ATTACK_REPORT_2026-04-24.md` — a genuine security-hardening pass on the
  Alex/Jeremy bridge using a "three-solutions test" methodology (same
  method the user asked to be used on the vignette/Horizon build-order
  question in this session). Found and fixed a real bug (Jeremy's
  high-urgency signal wasn't actually changing the care packet). This is
  NOT a "threat hunter" tool — the user later confirmed that phrase was a
  dictation typo with no real referent. Drop it, don't chase it further.
- `jeremy_cricket.py` — a persistent per-character memory keeper
  (SQLite-backed, importance-scored). Not a "sprite," unrelated to
  Foresight the Sprite.

### Pubcaast-Breaking-Dawn — the most mature, VERIFIED-live 3-service stack
This repo turned out to be significantly more advanced than expected —
worth a new session reading `SYSTEM_AUDIT_2026-08-19.md` in full.
- Three services, all with real code: `WORKING_PROGRAM/pubcast` (Python/
  FastAPI), `WORKING_PROGRAM/2i-backend` (Node/Express), `WORKING_PROGRAM/
  pubpartner` (a THIRD PubPartner implementation, package name
  `pubpartner_federation`).
- **`pubpartner_federation`: 14/14 tests pass, run live** (after installing
  missing `fastapi`/`httpx` deps) — manuscript commit, offline bidirectional
  sync convergence, concurrent-write handling, conflict detection (does NOT
  silently overwrite on same-field conflicts). This has real sync/
  concurrency logic that Pub-Partner-Base-Horizon's cartridge code does
  NOT have.
- **`2i-backend`: 16/16 tests pass, run live** — partner routing
  (unreachable partners correctly reported, never silently mis-routed),
  rate-limit bucket lifecycle (swept, not leaked), `base_version`
  pass-through correctness.
- `pubcast/main.py`: parses clean once you account for a **UTF-8 BOM bug
  hitting 20 files** — the exact same bug class already found and fixed in
  NowCurtsey-Build's PR #2 (which only had 11 affected files). Not fixed
  here yet.
- **LLM provider neutralizer/humanizer** — `Horizon/provider_neutralizer.py`
  (verified in earlier session; NOT re-checked this pass). Handles output
  normalization across Claude/GPT/Gemini/Ollama, translating "cold neutral
  reasoning" into the companion's specific personality voice/cadence/vocabulary
  without changing content/intent. This is the core of the "humanizer" feature
  from §1. Lives outside of all three PubPartner implementations — shared
  utility layer.
- **Foresight the Sprite — confirmed real concept, confirmed NOT built.**
  `FORESIGHT_ENGINEERING_HANDOFF_2026-08-19.md`: *"There is also Foresight
  the Sprite — same name, the system's living presence... Meeting her is
  meeting Foresight."* Mental model: Disney's Tinker Bell — small, glowing,
  iridescent presence tied to a lantern icon, embodies the assistant. THREE
  separate docs (`RUN_GUIDE.md`, `SESSION_HANDOFF_2026-08-19.md`,
  `FORESIGHT_UI_HANDOFF_2026-08-19.md`) independently confirm it is
  spec-only: *"Status: design direction, not yet built. This document is
  the plan, not a spec of finished work."*
- **Foresight UI authority unclear.** The-Prime contains `foresight_ui_v17.html`
  + `v18.html` with supporting Python (`polygon_shape_library.py`,
  `polygonal_tray_engine.py`, three test files) — comprehensive backend.
  Breaking-Dawn's `pubcast/static/foresight.html` is smaller (490 vs 1362
  lines), cleaner, integrated into the running app. Unclear which is
  canonical or whether they should be merged. Needs clarification in a future
  session before deciding the vignette/Foresight path.
- `pubcast/static/foresight.html` — the actual current, integrated
  Foresight/Counter build (titled "Foresight — The Counter"), genuinely
  reachable via the app's `/static` mount in `main.py` (not orphaned).
  Smaller than The-Prime's v17/v18 (490 lines vs 1362) — likely a cleaner
  rewrite, not a lesser version.
- `SYSTEM_AUDIT_2026-08-19.md` is a full honest state audit (✅ verified /
  🟡 loaded-untested / 🔌 wired-needs-dependency / 📦 orphan / ❌ broken /
  ⏸ degraded legend) covering 19 startup steps and ~15 orphaned-but-real
  modules (evidence_layer.py, response_execution_layer.py,
  mocap_precision.py, theory_graph.py, contradiction_engine.py,
  llm_orchestrator.py, pete_avatar.py, room_conductor.py, and more) — worth
  reading in full before deciding what else to salvage from this repo.

---

## 5. Live/Ongoing State to Not Drop

- **NowCurtsey-Build PR #2** is open and being actively driven to green
  under an hourly check-in Routine (`trig_01HwqdMPXLWgbLANjgQRDD2X`, named
  "Re-check PR #2 status"). Last check: clean, mergeable, all review
  threads resolved, no CI configured. **A new session should either
  continue honoring that Routine or explicitly cancel/reassign it** —
  don't let it silently orphan.
- **Task list** (harness TaskCreate/TaskUpdate — re-create in a new session
  since task state doesn't cross sessions). **Follow
  `BUILD_INSTRUCTIONS_NEXT_SESSION.md` for the execution order and exact
  steps — this list is now just a status summary, not the plan:**
  1. ✅ **DONE** — Fix UTF-8 BOM on 20 files in Breaking-Dawn (`pubcast/`
     tree). Committed `0fc079a` on branch `claude/nowcurtsey-repo-audit-rlsqkc`.
  2. ⏳ **Wire 2i UI to backend** — spec written, not yet applied to the
     actual HTML file. See `BUILD_INSTRUCTIONS_NEXT_SESSION.md` §3 for the
     proven contract and exact replacement code.
  3. ✅ **DECIDED, not yet executed** — Reconcile the three PubPartner
     implementations: merge `pubpartner_federation` (from the user's
     reference snapshot) into this repo's `pubpartner/` as the one shared
     core. See `BUILD_INSTRUCTIONS_NEXT_SESSION.md` §2 for the exact merge
     commands and test gate — do NOT re-open this as an open decision.
  4. Build multi-avatar group chat / weekly hangout (on the merged shared
     core, after task 3 is executed) — pending
  5. Design standalone vignette scene system — pending
  6. Build interactive vignette props (TV, fireplace, radio) — pending
  7. Port collaborative writing mode + group chat to PubPartner Horizon —
     pending, after task 3 is executed.

---

## 5.5. Critical Missing Features (Known Gaps Across All Three PubPartner Implementations)

These are NOT bugs; they are features the user specified in §1 that are not
yet implemented everywhere:

1. **Offline fallback (durable)** — User requirement (§1): "work with local LLM when
   internet fails." Breaking-Dawn's 2i-backend has a partial implementation:
   `queued-locally` fallback when PubPartner is unreachable (allows queuing
   messages locally). This queue is in-memory only — it dies with the process.
   For this to be a real offline feature, it needs durable local spool/queue.
   The other two implementations (Horizon and NowCurtsey) have no offline
   fallback at all. Durable fallback logic needs to be built into whichever
   implementation becomes the shared core.

2. **LLM-provider neutralizer wiring** — `provider_neutralizer.py` exists
   (verified), but is NOT currently wired into any of the three implementations.
   It needs to be integrated into the shared-core pipeline so all three
   PubPartner code paths normalize output through the humanizer before
   returning to the app.

3. **Voice I/O (input)** — Speech synthesis (output) is wired in 2i v3.
   Speech recognition (input/dictation) was in the original prototype but not
   ported to v3. Missing from all other implementations.

---

## 6. Immediate Next Step (where this session left off)

**Before writing any more feature code**, do the head-to-head comparison
that was queued when this handoff was requested: compare what each of the
three PubPartner implementations actually has.

### PubPartner Implementations Comparison Matrix

| Feature | pub_partner_chat.py (NowCurtsey) | pubpartner/ (Base-Horizon) | pubpartner_federation (Breaking-Dawn) |
|---------|---|---|---|
| **Lines of code** | ~800 | ~1200 | ~600 |
| **Tests** | 0 | 76/76 pass | 14/14 pass |
| **Cartridge/portable** | No | Yes (full) | No |
| **Memory persistence** | No | Yes (memory_store.py) | No |
| **Prompt assembly** | Basic | Sophisticated (tokenizer + prompt_assembler) | Basic |
| **Turn sequencing** | No | Yes (sequence_controller.py, debouncing + idle tracking) | No |
| **Multi-avatar group chat** | No | No | No |
| **Manuscript sync** | No | No | Yes (bidirectional, offline-capable) |
| **Concurrency/conflict handling** | No | No | Yes (real conflict detection) |
| **Voice I/O** | No | No | No |
| **LLM-provider normalization** | No | No | No |
| **Character personality cart** | Via `same_as_studio` sentinel | Via cartridge.py | Via personality routing |

**DECIDED (superseded — do not re-litigate):** merge #3's sync/concurrency
logic into #2 (this repo, `Pub-Partner-Base-Horizon`) as the one true shared
core. This decision was made using a reference snapshot the user provided
(`PubCast_2i_PubPartner_WORKING_20260816.zip`) that proves, with 60 passing
integration tests, that this exact combination — Horizon-style
cartridge/memory/prompt-assembly plus federation-style sync/concurrency —
already works end-to-end with a 2i chat UI.

**The actual step-by-step execution plan lives in a separate file:
`BUILD_INSTRUCTIONS_NEXT_SESSION.md`, in this same repo.** That file is the
one to follow — exact merge commands, exact dependency changes, exact test
gates, exact UI wiring code, and a prioritized gap list. Everything in this
section (§6) is background on how the decision was reached; treat
`BUILD_INSTRUCTIONS_NEXT_SESSION.md` as authoritative for what to do next,
and this file as authoritative for why.

---

## 7. User Working Style Notes (for whoever picks this up)

- Explicit stated preference: **"stop lying to me and ruining what im
  trying to do."** Never report a doc's claims, a session's self-description,
  or a "should already be done" assumption as fact without independently
  verifying (run the tests, read the actual file, check the actual repo
  state). This session found real gaps between claimed and actual state
  multiple times — that pattern will keep recurring across this many repos
  and sessions; keep checking.
- User dictates via voice-to-text; expect occasional garbled phrases (this
  session's "threat hunter" turned out to be a typo with no real referent —
  confirmed and dropped, don't resurrect it).
- User explicitly asked for a "three solutions test" methodology when
  facing an architecture fork — lay out ≥3 real options with honest
  tradeoffs, pick one with stated reasoning, rather than presenting a single
  path.
- User wants brief upfront blueprints/specs before big builds, not
  incremental step-by-step play-by-play — "the blueprint of how it comes
  together... just the summary breakdown of each major section."
