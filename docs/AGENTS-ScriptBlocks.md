# Script Blocks And Graph Model

This is a compact mental-model document.
For real graph editing rules, use `AGENTS-ScriptEditing.md`.
Do not keep a second large graph manual here.

## Identity model

- `blockId`: graph block key, used by `/ops`
- `CodeName`: formula identifier
- `VisualName`: UI label

Formulas use `CodeName`, not `blockId`.

## Container model

There are two broad families:

- handler containers, selected by input count
- template blocks, such as sources, trade blocks, value blocks, panes, parameter linking blocks, and external script blocks

## Connection model

- graph links are data-flow links created through `Connect`, `ReplaceInput`, or `ConnectByInputName`
- UI links are created through `AddGraphLink` and `AddControlLink`
- input indices are zero-based

## High-risk mistakes

- guessing ports instead of reading `/explain`
- confusing `blockId` with `CodeName`
- connecting trade-block `Src` from anything other than the real tradable source
- leaving duplicate links on the same input
- using pane-like blocks instead of real pane creation with `AddPane`

## When to open next

- `AGENTS-ScriptEditing.md` for graph edits, formulas, panes, trade wiring, or multi-timeframe wiring
- `AGENTS-RunAndAnalyze.md` for lifecycle and runtime results