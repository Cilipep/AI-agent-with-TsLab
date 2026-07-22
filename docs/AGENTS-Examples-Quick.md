# Examples (Quick Index)

Use this short index to avoid loading the full cookbook (`AGENTS-Examples.md`).

## Hard rules (API-first)
- Scripts are server-side; edit via `/api/scripts/{name}/ops`, not local files.
- Formulas use **CodeName**, not `blockId`.
- Always run `/explain` before edits.

## How to use the cookbook
Open `AGENTS-Examples.md` (index) and then load **only** the relevant part file:
- `AGENTS-Examples-Basics.md`
- `AGENTS-Examples-Patterns.md`
- `AGENTS-Examples-Options.md`

## Common sections (by heading)
- **Working with `blockId != CodeName`** (identity hygiene)
- **Minimal "open by market" strategy skeleton**
- **Formula input hygiene (avoid missing Input0)**
- **Optimization setup and "stuck job" handling**
- **Options basics**: option source -> series -> single option
- **ControlPane / CanvasPane** wiring patterns
- **ATR SL/TP management**, **scale-in**, **pyramiding** examples

If you need a concrete recipe, ask for that single section from `AGENTS-Examples.md`.
