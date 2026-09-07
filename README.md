# PubPartner

Persistent character cartridges for consistent AI personas. Define a
character once — appearance, voice, cadence, tendencies — and carry a
growing, ranked memory of them across every session, engine, and surface.

`Rear View Foresight LLC — Feic Mo Chroí™`

## What a cartridge is

A cartridge is a directory (or a `.zip` of one) with this layout:

```
alex/
    character.yaml       # required — name, summary, values, boundaries, tendencies
    voice_profile.yaml   # required — cadence, vocabulary, verbal tics
    appearance.yaml       # optional — physical/visual description
    memories.jsonl        # optional — seed memories shipped with the cartridge
    memories.db            # auto-created — the live, growing memory store
```

Nothing about this format is engine-specific. It doesn't assume Claude,
GPT, or any particular model — `pubpartner prompt` produces a plain-text
system prompt you can hand to anything that accepts one. `pubpartner chat`
is a convenience wrapper around the Anthropic API for testing a cartridge
directly, not a requirement.

## Install

```bash
pip install -e .
```

Requires Python 3.10+. Core dependencies (`pyyaml`, `tiktoken`,
`scikit-learn`) are all free, local, and require no API keys — a cartridge
works completely offline except for the optional `chat` command.

## Quickstart

```bash
# Scaffold a new cartridge
pubpartner init alex \
    --name "Alex" \
    --summary "Steady and observant. Waits before responding." \
    --cadence "short sentences, deliberate pauses" \
    --vocabulary "plain and warm, avoids jargon"

# Fill in appearance.yaml by hand, then start adding memories
pubpartner add-memory alex --type personal --text "Prefers direct feedback." --importance 0.6
pubpartner add-memory alex --type project --text "Currently building PubPartner." --importance 0.8

# See what a fully-assembled system prompt looks like for a given message
pubpartner prompt alex --query "how should we handle hard feedback" --budget 2000

# Talk to it directly (requires ANTHROPIC_API_KEY)
pubpartner chat alex
```

## How memory retrieval works

Every memory is typed as one of: `episodic`, `semantic`, `procedural`,
`emotional`, `project`, `personal`. On each turn, `assemble_prompt()` scores
every stored memory against the current message using a weighted blend of:

- **relevance** — TF-IDF cosine similarity between the query and the memory text
- **recency** — exponential decay, half-life configurable (default 14 days)
- **importance** — the 0.0–1.0 weight given at write time

The character block (identity, voice, appearance) is never dropped. When
the token budget is tight, memories are cut lowest-score-first until the
prompt fits. This is real, tested retrieval — no embedding API required,
no network dependency, no cost per call.

## Library usage

```python
from pubpartner import load_cartridge, assemble_prompt

with load_cartridge("alex") as cartridge:
    cartridge.memory.add(
        "Mentioned she's been reworking the housing situation.",
        memory_type="episodic",
        importance=0.5,
    )
    result = assemble_prompt(cartridge, query="how's everything going", token_budget=2000)
    print(result.text)          # the system prompt to send to any LLM
    print(result.token_count)   # exact token count for budgeting
```

## Packaging a cartridge for distribution

```bash
cd alex && zip -r ../alex.zip . && cd ..
```

`load_cartridge()` accepts either the directory or the `.zip` directly —
a cartridge is meant to be handed to someone else and just work.

## Testing

```bash
pip install pytest
python -m pytest tests/ -v
```

24 tests covering cartridge loading/validation, memory CRUD and ranking,
and prompt assembly under token pressure — including the failure paths
(malformed YAML, missing required fields, bad memory types, zero-budget
edge cases), not just the happy path.

## Design decisions worth knowing

- **No embedding API.** TF-IDF + recency + importance is free, offline, and
  fast. It won't catch every semantic paraphrase an embedding model would,
  but it costs nothing per call and never depends on a third-party service
  being up. If you outgrow it, `memory_store.query()` is the one place to
  swap in a different scorer — the rest of the system doesn't care how
  scoring works internally.
- **Character block is never dropped**, even at a token budget of zero.
  A character with no memories is still itself; a character with no
  identity block isn't a character at all.
- **Cartridges fail loudly, not silently.** A missing field or malformed
  YAML raises `CartridgeValidationError` with the specific file and field
  at load time — not a mysteriously wrong prompt three turns later.
