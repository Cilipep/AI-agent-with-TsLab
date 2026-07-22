# Examples & Recipes: Editing TSLab Scripts via Web API `ops` (Index)

This cookbook was split into parts to reduce context size.

## Parts
- `AGENTS-Examples-Basics.md`: fundamentals, identity hygiene, simple strategy skeletons.
- `AGENTS-Examples-Patterns.md`: trading patterns, graph patterns, advanced recipes.
- `AGENTS-Examples-Options.md`: options-specific recipes.

## Small-context entry
- `AGENTS-Examples-Quick.md`: short index + guidance to load only the needed section.

## Rules (API-first)
- Scripts are server-side; edit via `/api/scripts/{name}/ops`, not local files.
- Always read `/api/scripts/{name}/explain` before edits.
- Formulas use **CodeName**, not `blockId`.

See `AGENTS.md` for the full index of instruction docs.
