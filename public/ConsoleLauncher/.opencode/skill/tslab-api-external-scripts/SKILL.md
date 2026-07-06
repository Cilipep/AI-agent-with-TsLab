---
name: tslab-api-external-scripts
description: "Configure ExternalScriptItem/ExternalOptionScriptItem blocks via ops (SetExternalScripts, SetPredefinedHandlerTypeFullName), and understand server-side file deployment/compilation behavior."
---

# TSLab Web API: External Script Blocks (ExternalScriptItem / ExternalOptionScriptItem)

Use this skill when you need to create or configure "external script" blocks in a TSLab graph via `/api/scripts/{name}/ops`.

## What these blocks are

- `ExternalScriptItem`: runs external handlers implementing `IExternalScript*` interfaces.
- `ExternalOptionScriptItem`: runs external handlers implementing `IExternalOptionScript*` interfaces (options-domain scripts).

They are **template blocks**, not regular `/api/handlers` registry handlers.

## Ops (what to do)

1) Add the block:
- `AddBlock` with `blockType: ExternalScriptItem` or `ExternalOptionScriptItem`

2) Configure it using one of:
- `SetPredefinedHandlerTypeFullName` (recommended): bind to a known server type (no compilation)
- `SetExternalScripts`: set `scripts[]` list (server-side `.cs/.vb/.dll` files)

## Hard rules / pitfalls

- Do not invent file paths: `scripts[]` are **server filesystem paths**. Ops do not upload files.
- Do not mix `.cs` and `.vb` in one block.
- The number of connected inputs selects which interface is expected:
  - 1 input -> `IExternal*Script`
  - 2 inputs -> `IExternal*Script2`
  - 3 inputs -> `IExternal*Script3`
  - 4 inputs -> `IExternal*Script4`
  - other -> `IExternal*ScriptMultiSec`
- After ops edits: `POST /load` -> `POST /validate?strictCodegen=true` -> `POST /build` (run only when requested).
- Prove persisted predefined-type binding through GET /api/scripts/{name}/json and inspect response.data.editData.viewModel or the equivalent raw graph payload. /explain may still show a template-level UndefinedHandler for external blocks even when the binding is already persisted.
- Verification order: prove persisted binding first, then run the normal lifecycle on the same artifact, and only then inspect runtime-created UI or other runtime artifacts if the task requires them.
- If /json already proves the required PredefinedHandlerTypeFullName, do not keep retrying handler-mutation ops only because /explain still looks unresolved.

## Minimal example (predefined handler type)

```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "Ext", "blockType": "ExternalScriptItem", "category": "Usual" },
    { "op": "SetPredefinedHandlerTypeFullName", "blockId": "Ext", "handlerTypeFullName": "My.Namespace.MyHandler, My.Assembly" }
  ]
}
```

## Docs pointer

- External scripts guide: `AGENTS-ExternalScripts.md`
- Template blocks overview: `AGENTS-ScriptBlocks.md`

