# PubPartner Portable — Handoff

Rear View Foresight LLC — Feic Mo Chroí

## What this is

PubPartner's core (cartridge, memory store, prompt assembler, schema,
tokenizer) was already timing-agnostic — it answers "what should this
character say," never "when." When PubPartner runs bundled inside
PubCast, PubCast's switchblade_governor answers the "when" question by
reading emotional state (VDI) and scene composition and emitting a
priority vector to the engines.

Standalone, there is no PubCast, no VDI, no scene state. This build adds
the missing piece: a self-contained turn sequencer and an embeddable
runtime, so PubPartner can decide its own timing without any external
scheduler — while leaving an explicit, optional seam for PubCast (or
anything else) to influence that timing later if the two are ever
bundled together again.

## What was added

**pubpartner/sequence_controller.py**
`SequenceController` — buffers rapid-fire user input into one coherent
turn (debounce), enforces a minimum spacing between fired turns (so
nothing can spam the LLM layer faster than it can process), and tracks
session idle state. Takes an optional `PriorityHint` on every `evaluate()`
call — if none is given, or any field on it is `None`, it falls back to
its own defaults. Nothing in this module blocks waiting for an external
signal.

Also exports `score_captured_memory()` — a small, documented importance
scorer for memories captured live during a turn (corrections and
repeated topics score higher; message length is explicitly not a signal).

**pubpartner/portable_runtime.py**
`PortableRuntime` — the embeddable glue object. Wraps a `Cartridge`, a
`SequenceController`, and an optional Anthropic client into one thing a
host (CLI, web handler, bot framework) can drive: `submit_input()`,
`ready_for_turn()`, `run_turn()`. Never blocks on stdin, never assumes a
REPL. `run_turn()` calls the LLM, captures an episodic memory of the
exchange, and returns a `TurnResult` with the reply text and metadata.
`build_prompt_only()` exists for hosts that want to hand the assembled
prompt to their own model client instead of the built-in call.

## Architecture — what stays separated

The dependency graph runs one direction only:

```
cli.py / portable_runtime.py
        │
        ├──> cartridge.py ──> memory_store.py, schema.py
        │         │
        │         └──> prompt_assembler.py ──> tokenizer.py
        │
        └──> sequence_controller.py  (stdlib only — time, dataclasses, enum)
```

`cartridge.py`, `memory_store.py`, `prompt_assembler.py`, `schema.py`, and
`tokenizer.py` never import `sequence_controller.py`, and
`sequence_controller.py` never imports any of them. Verified by AST
import audit on every module in this build, not just grep — see the
`Verification` section below. `portable_runtime.py` is the only file that
imports both, and it holds no character logic or timing policy itself —
it's glue, nothing else.

This means the cartridge layer can be embedded in PubCast, in Portable,
or in something else entirely, without ever knowing which pacer (if any)
is driving it. If a future PubCast bridge wants to hand PubPartner a
priority vector from switchblade_governor, it constructs a `PriorityHint`
from that vector's `identity_moment` / urgency-equivalent fields and
passes it to `ready_for_turn(hint=...)` — no changes required to
`sequence_controller.py` or anything below it.

## Verification (executed, not documented)

- 76 tests passing (24 original cartridge/memory/prompt tests, unchanged,
  plus 52 new: 34 for `SequenceController`, 18 for `PortableRuntime`).
  Run: `python -m pytest tests/ -v`
- One real bug was caught and fixed during this build: a test assumed
  `take_turn()` immediately allowed a next turn to fire, but the default
  `min_turn_interval_seconds` (0.35s) correctly holds it — that's the
  rate-limit floor working as designed. Fixed the test, not the code,
  after confirming the behavior was correct.
- A standalone end-to-end smoke test was run outside pytest: simulated a
  burst of three rapid user messages, confirmed they debounced into one
  turn, confirmed the fake LLM call received the right assembled prompt
  and history, confirmed a second turn accumulated conversation history
  correctly, confirmed two episodic memories persisted in the cartridge's
  SQLite store. All assertions passed on live execution.
- Import coupling was audited two ways: `grep` for switchblade/VDI/PubCast
  references (only docstring mentions, zero import statements), and a
  Python `ast` walk of every module's actual `Import`/`ImportFrom` nodes
  (confirms `sequence_controller.py` imports stdlib only: `time`,
  `dataclasses`, `enum`, `typing`).

## What was not touched

`cartridge.py`, `memory_store.py`, `prompt_assembler.py`, `schema.py`,
`tokenizer.py`, and `cli.py` are byte-for-byte identical to what shipped
before this session. Nothing about the cartridge format, memory scoring
algorithm, or CLI commands changed. This build only adds two new files
and re-exports them from `__init__.py`.

## What's still open

- `cli.py` still uses its own blocking REPL loop (`_cmd_chat`) rather than
  `PortableRuntime` — it works standalone today but doesn't yet exercise
  the new sequencer/embeddable path. Wiring `cli.py chat` through
  `PortableRuntime` is a natural next step if you want the reference CLI
  to double as a working example of the embeddable API, but it wasn't
  required for Portable to function and wasn't done here to keep this
  handoff scoped to what was asked.
- No PubCast-side bridge code was written (nothing in the PubCast repo
  was touched). This handoff only proves the seam exists on PubPartner's
  side — an actual bridge that constructs `PriorityHint` from a live
  `PriorityVector` is separate work, in PubCast's codebase, not this one.
- `PriorityHint`'s `urgency` field is a 0.0–1.0 float chosen to be roughly
  compatible with switchblade's `vdi_score`/`render_intensity` scale, but
  no real mapping between the two has been defined or tested against
  actual switchblade output — this is a documented assumption, not a
  verified integration.
