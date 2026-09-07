# Build Instructions — Read This First, Then Execute In Order

**Audience:** an AI session that has never seen this project before and can
only read text. Every step below is written to be followed literally —
exact paths, exact commands, exact verification. Do not skip verification
steps. Do not improvise file locations.

**Do not re-derive strategy.** The decisions below were already made and
verified in a prior session. Your job is to execute, not to re-evaluate
whether this is the right plan. If a step's verification fails, stop and
report the failure — do not silently work around it or substitute your own
approach.

If you want project history/context (why these decisions were made, what
else exists across the repo landscape, what's still unresolved), read
`SESSION_HANDOFF_2026-09-07.md` in this same repo. That file is background.
This file is the task list.

---

## 0. What you're building, in one paragraph

There are three separate PubPartner (AI companion) implementations spread
across three repos. One of them (a reference snapshot the user hand-provided,
now unpacked at a path given in step 1) already proves, with 60 passing
integration tests, that a Node.js chat UI ("2i") can talk to a Python
federation backend ("PubPartner") over real HTTP, with working offline
sync and conflict handling. Your job is to merge that proven federation
code into this repo's `pubpartner/` package (which already has a different,
also-real, cartridge/personality/memory system with 76 passing tests), so
that ONE package has both capabilities. Then wire the 2i chat UI to it using
the pattern the reference already proves works. Do this before building any
new feature (collaborative writing pacing, group chat) — build those against
the merged core, not against any of the three original implementations.

---

## 1. Locate the reference snapshot

The user uploaded a zip named `PubCast_2i_PubPartner_WORKING_20260816.zip`.
In the session that wrote this document, it was unpacked to:

```
/tmp/claude-0/-home-user/bb826872-03f5-5a4f-95c5-02bf291dac0d/scratchpad/PubCast_2i_PubPartner_WORKING_2026-08-16/
```

**That exact path will not exist in your session** (scratchpad paths are
session-specific). If the user re-attaches the same zip, unzip it into your
own scratchpad and use that path instead. If you cannot find or obtain this
zip, STOP and ask the user for it before proceeding past step 2 — steps 2
onward depend on this code existing on disk. Do not attempt to reconstruct
it from memory or from this document's prose; the actual source files are
required.

Verify you have it before continuing:
```bash
find <your-scratchpad>/PubCast_2i_PubPartner_WORKING_2026-08-16/pubpartner/pubpartner_federation -name "*.py"
```
Expected: 6 files — `__init__.py`, `engine.py`, `identity.py`, `memory.py`,
`protocol.py`, `service.py`, `store.py`.

---

## 2. Merge the federation code into this repo — mechanical, verified clean

**This repo is `Pub-Partner-Base-Horizon`** (you should already be in it,
or clone `https://github.com/whatsupjosie/Pub-Partner-Base-Horizon`,
branch `main`).

Confirmed in the prior session (do not re-check unless something looks
different): **zero filename collisions** between this repo's
`pubpartner/*.py` and the reference's `pubpartner/pubpartner_federation/*.py`.
This repo has: `cartridge.py`, `cli.py`, `memory_store.py`,
`portable_runtime.py`, `prompt_assembler.py`, `schema.py`,
`sequence_controller.py`, `tokenizer.py`. The reference federation module
has: `engine.py`, `identity.py`, `memory.py`, `protocol.py`, `service.py`,
`store.py`. No overlap. This is a copy-in, not a line-by-line merge.

**Important — `memory_store.py` vs. federation's `memory.py` are DIFFERENT
THINGS, do not conflate them:**
- This repo's `memory_store.py` = cartridge personality memory (episodic /
  semantic / procedural / emotional / project / personal), TF-IDF relevance
  ranking, for the AI companion remembering things about its relationship
  with the user.
- Reference's `pubpartner_federation/memory.py` = a "candidate capture and
  promote" gate for manuscript-editing memory candidates — an unrelated
  concept scoped to the writing/sync workflow.

Both are staying, under their own names, in the same package. Do not delete
either. Do not try to unify them into one memory system in this pass.

### Steps

```bash
cd /home/user/pub-partner-base-horizon   # or wherever you cloned it

# 1. Copy the federation module in as a subpackage
cp -r <scratchpad>/PubCast_2i_PubPartner_WORKING_2026-08-16/pubpartner/pubpartner_federation \
      pubpartner/pubpartner_federation

# 2. Copy its tests in, under their own subfolder so they don't collide
#    with this repo's existing tests/test_*.py files
mkdir -p tests/federation
cp <scratchpad>/PubCast_2i_PubPartner_WORKING_2026-08-16/pubpartner/tests/test_concurrency.py tests/federation/
cp <scratchpad>/PubCast_2i_PubPartner_WORKING_2026-08-16/pubpartner/tests/test_sync.py tests/federation/
cp <scratchpad>/PubCast_2i_PubPartner_WORKING_2026-08-16/pubpartner/tests/test_service.py tests/federation/
touch tests/federation/__init__.py
```

### Add the federation module's dependencies to `pyproject.toml`

This repo's current `dependencies` list (`pyyaml`, `tiktoken`,
`scikit-learn`) does NOT include what the federation module needs
(`fastapi`, `uvicorn`, `httpx` — confirmed from the reference's own
`pyproject.toml`). Edit this repo's `pyproject.toml`:

```toml
dependencies = [
    "pyyaml>=6.0",
    "tiktoken>=0.5",
    "scikit-learn>=1.3",
    "fastapi>=0.110",
    "uvicorn>=0.29",
    "httpx>=0.27",
]
```

### Install and verify — this is the gate, do not skip

```bash
pip install -e .
python -m pytest tests/ -v
```

**Expected: all pre-existing 76 tests still pass, PLUS the federation
tests (14 in the reference's own count) now also pass, for a new total
around 90.** If ANY pre-existing test now fails, you introduced a real
collision — stop and diagnose before continuing; do not delete or skip the
failing test to make the number look right.

Commit this as its own commit before doing anything else:
```bash
git add pubpartner/pubpartner_federation tests/federation pyproject.toml
git commit -m "Merge proven pubpartner_federation (sync/concurrency/manuscript) into shared core

Copied from user-provided reference snapshot PubCast_2i_PubPartner_WORKING_20260816.zip,
which demonstrated 60 passing integration tests proving real 2i<->PubPartner HTTP sync.
No filename collisions with existing cartridge/memory/prompt-assembly/sequencer code.
memory_store.py (personality memory) and pubpartner_federation/memory.py (manuscript
candidate gate) are distinct concerns kept under separate names, not merged.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KAPb7yKsTUbYJHVUWe7D8J"
git push -u origin main
```

**Definition of done for this step:** `python -m pytest tests/ -v` shows
zero failures, and both the old test files and `tests/federation/*.py` ran.

---

## 3. Wire the 2i UI to the merged backend, using the reference's proven pattern

**Do not write this wiring from scratch or guess at an API shape.** The
reference snapshot's `integration/test_2i_pubpartner.py` (in the same
unpacked directory as step 1) is a real, passing, end-to-end test that
shows the exact request/response contract 2i uses to talk to PubPartner —
read it before writing any code. Key facts already confirmed from it in
the prior session:

- 2i's `POST /api/manuscript/commit` accepts a manuscript payload and
  forwards it to PubPartner's federation service.
- A successful commit returns `{"status": "committed", "manuscript_id": ...,
  "message_id": "msg-..."}` and does NOT include a `pubpartner_status` key
  (that key only appears when the commit was queued locally instead of
  routed — see `OPEN-002` below, this matters for error-state UI).
- PubPartner's own read endpoint is `GET /api/manuscript/<id>` and returns
  `{"fields": {...}}` including the same `content`, `character_names`, and
  `message_id` that were committed.

Read the rest of `integration/test_2i_pubpartner.py` in full (it also
covers timeout/malformed-response/server-error fault injection) before
wiring the UI, so error states in the UI aren't invented from nothing.

### The UI file to wire

`The-Counter-and-2i` repo, file `2i_writers_room_v2.html` — as of the prior
session, no exact file literally named `2i_writers_room_v3.html` could be
found anywhere in that repo despite a handoff doc claiming it exists
(check again yourself in case it's been added since; don't trust the old
claim uncritically). The stub to replace is `sendChat()`, roughly at
line 597:

```javascript
// CURRENT — stub, replace this:
function sendChat(){
  const v=chatInput.value.trim(); if(!v) return;
  addChatMsg('you',v); chatInput.value='';
  setTimeout(()=>addChatMsg('pp','(placeholder reply — not yet wired to a real model call)'),350);
}
```

Replace it with a real call, matching the proven contract above (adjust
endpoint path/port to whatever `2i-backend`'s `server.js` actually exposes
for character chat — that's `POST /api/chat/character` at
`Pubcaast-Breaking-Dawn/WORKING_PROGRAM/2i-backend/server.js:1004`, a
**different** endpoint from the manuscript-commit one described above; both
exist in the same server and you likely need both wired eventually, but
chat is the one the user is waiting on first):

```javascript
async function sendChat(){
  const v = chatInput.value.trim();
  if(!v) return;
  addChatMsg('you', v);
  chatInput.value = '';
  try {
    const response = await fetch('http://localhost:8787/api/chat/character', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ character: 'pubpartner', message: v })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    addChatMsg('pp', data.response || data.content || '(no response)');
  } catch (error) {
    addChatMsg('pp', `[Connection error: ${error.message}]`);
  }
}
```

### Verify before committing

1. Start the backend: `cd Pubcaast-Breaking-Dawn/WORKING_PROGRAM/2i-backend && npm install && node server.js`
2. Open the HTML file in a browser (or serve it locally), type a message,
   confirm you get either a real model response or a clean connection-error
   message — NOT the old hardcoded placeholder string.
3. Only commit once you've actually done this manual check — a code review
   of the diff is not sufficient here, per this project's standing rule
   (stated by the user this project's whole history: verify by running,
   never report a claim as fact without having executed it).

---

## 4. Known gaps to build next, in priority order (do not reorder without asking)

These come from `OPEN-001` through `OPEN-006` in the reference snapshot's
own `ENGINEERING_RUN_2026-08-16.md` (read that file in full if you haven't —
it documents real bugs already found and fixed in the code you just merged,
and the ones still open):

1. **OPEN-002 — durable local spool.** 2i's "queued-locally" fallback (when
   PubPartner is unreachable) is in-memory only and dies with the process.
   This is also exactly the "offline fallback" feature the user explicitly
   asked for (local LLM / local queue when internet fails) — treat this as
   one requirement, not two.
2. **Collaborative writing pacing** (1.5-page buffer, forced review before
   continuing) — build this against the merged core from step 2, using
   `2i_writers_room_v2.html`'s existing buffer/approve/pin UI (already
   built, do not rebuild it) as the frontend.
3. **Multi-avatar group chat** ("weekly hangout") — also build against the
   merged core.
4. **OPEN-004 — conflict resolution endpoint.** Conflicts are currently
   listable (`GET /api/sync/conflicts`) but not resolvable. Needed before
   group chat/sync features are exposed to real users.
5. Provider neutralizer wiring — `provider_neutralizer.py` exists (this
   repo, per prior session's verification) but is not yet called from
   anywhere in the merged core's chat path. Wire it in so all LLM output
   passes through it before reaching the UI.

Vignette scenes, props (TV/radio/fireplace), and the Foresight UI
authority question (The-Prime's v17/v18 vs. Breaking-Dawn's
`static/foresight.html`) are graphics-track work, independent of this
backend-track work, and are lower priority per the user's own stated
architecture split — see `SESSION_HANDOFF_2026-09-07.md` §3 if you need
that reasoning restated.

---

## 5. Rules that apply to every step above

- **Verify by running, not by reading.** This has been the standing rule
  for this entire project across multiple sessions. A test suite passing
  is evidence; a docstring or handoff claim is not.
- **Commit each numbered step separately**, with a message stating what was
  verified (test counts, manual check performed), not just what changed.
- **Push to the branch specified in your own session's Git Development
  Branch Requirements block** — those requirements are session-specific and
  are not repeated here because they may differ by the time you run this.
- If you find this document's file paths, line numbers, or claimed test
  counts don't match what's actually in the repo, trust the repo and say
  so — this document can go stale the moment new commits land.
