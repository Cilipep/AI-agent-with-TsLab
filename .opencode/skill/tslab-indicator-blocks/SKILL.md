---
name: tslab-indicator-blocks
description: "Use indicators inside TSLab block scripts via Web API: discover handler schema (/api/handlers/{typeName}), add/connect blocks, set params, validate/build/run. Covers using Function indicators (DynamicItem+HandlerName) and DLL-based indicators (HandlersFolder or /api/indicator-dlls). Focus on wiring rules and stream/value/precalc pitfalls."
---

# TSLab: Using Indicators in Block Scripts (API + Cubes)

Use this skill when the user asks to **use an indicator in a script graph** (cubes/blocks) and wants it wired and run via Web API.

If the user asks to **implement** a new indicator in C#, use `$tslab-indicator-authoring`.

## Hard Rules

- Always use `/api/handlers/{typeName}` as the ground truth for inputs/outputs/parameters.
- If you are unsure which `Execute(...)` signature family the server supports (stream vs values vs precalc), use `GET /api/sdk/contracts` and copy a shipped template.
- Always read `GET /api/scripts/{name}/explain` before editing a graph; never guess block IDs or parameter names.
- After ops edits: `POST /load` -> `POST /validate` -> `POST /build` -> `POST /run` and treat warnings as actionable.
- Keep block names readable: meaningful ASCII `CodeName`; for new scripts prefer `blockId = CodeName = VisualName`.
- In formulas, `i` is built-in; do not connect it. `UnknownExpressionReference` for `i` is expected on some builds and is non-blocking.
- For period/window indicators in formulas, use startup guards (`i >= period ? Expr : Fallback`).

## Choose the indicator source

1. **Function indicator (custom indicator script)**:
   - Use `$tslab-api-indicators`.
   - In scripts: add `DynamicItem` and set `HandlerName = <FunctionName>` (not `HandlerTypeName`).
2. **DLL indicator library**:
   - Disk: HandlersFolder hot reload (drop `.dll` + optional `.pdb`).
   - DB: upload/replace/delete via `$tslab-api-indicator-dlls` (`/api/indicator-dlls`).

## Read only when needed

- Add/connect blocks via ops: use `$tslab-api-script-edit` (primary).
- Indicator-specific wiring pitfalls: `references/troubleshooting-stream-value-precalc.md`
- Minimal "how to wire a handler block": `references/using-handler-in-graph.md`
