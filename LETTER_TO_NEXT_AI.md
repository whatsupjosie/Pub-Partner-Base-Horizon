# A Letter to the Next AI Working on This Project

You weren't here for any of this. You're reading cold. That's fine — this
letter exists so you don't have to guess. Read it, then read
`BUILD_INSTRUCTIONS_NEXT_SESSION.md` in this same repo (that's your actual
task list). `SESSION_HANDOFF_2026-09-07.md` is background if you want the
longer story of how we got here.

## What the user is trying to do

The user is building **PubPartner Horizon** — a portable AI companion.
The idea, in their own words: carry a small file (a "cartridge" — holds
personality, long-term memory, voice, avatar skins) to any computer, open
a chat window, and it's the same companion, same memory, same personality,
everywhere. Lightweight, not a full production studio. It needs to work
with camera/mic like a video call, use emotional-intelligence reasoning
(PEQ), normalize output from whatever LLM is behind it (Claude, GPT,
Gemini, Ollama) into one consistent personality voice, support multiple
avatar skins, remember relationships across sessions, support group chats
with multiple of the user's own companions, and eventually stand in small
self-contained scene vignettes (coffee shop, park, etc.) with interactive
props.

This is a real, ambitious, buildable project. Treat it as one.

## What's actually true right now (verified, not assumed)

There are **three separate, real implementations** of "PubPartner" spread
across different repos, built in different sessions without knowing about
each other. That's the core problem this phase of work is solving — not
adding a fourth, but merging the best of what already exists into one
foundation.

- **This repo** (`Pub-Partner-Base-Horizon`) has the cartridge, memory,
  prompt-assembly, and turn-sequencing system. 76 tests passing.
- **Breaking-Dawn** repo has a second implementation with real offline
  sync and conflict-resolution logic that this repo's version lacks.
- **NowCurtsey-Build** has a third, simpler, single-character version with
  one useful pattern worth keeping (a "same-as-studio" sentinel).

The user also handed us a **verified reference snapshot** —
`PubCast_2i_PubPartner_WORKING_20260816.zip` — proving that a chat UI
("2i") and a Python backend ("PubPartner") can actually talk to each other
over real HTTP, with 60 passing integration tests. That reference is the
proof that the merge we're doing is not theoretical — it already worked
once, in that snapshot. Our job is to bring that same combination into
this repo permanently, as tracked source, not a one-off zip.

## The one rule that matters most to the user

**Never report a claim as fact without independently verifying it** — run
the tests, read the actual file, check the actual repo state. This
project's history is full of docs that said something was done when it
wasn't, and files that existed as real, tested code when everyone assumed
they didn't. The user has said directly: don't lie to them, even by
repeating someone else's unverified claim as if it were checked. If you
didn't run it or read it yourself, say so.

The user dictates by voice and sometimes the transcription garbles things.
If an instruction looks broken or doesn't parse, ask rather than guess —
but don't let every small thing become a question. Most of the path
forward is already decided; you're executing, not re-litigating.

## What to actually do

Open `BUILD_INSTRUCTIONS_NEXT_SESSION.md`, right here in this repo. It has
exact commands, exact file paths, exact test gates, in order. Follow it.
If something in it doesn't match what you find in the repo, trust the repo
over the document and say so plainly — don't silently paper over the gap.

You don't need to figure out the plan. The plan exists. Your job is to
execute it carefully, verify each step actually worked before moving to
the next, and tell the user clearly what's done and what's still open.

That's it. Good luck.
