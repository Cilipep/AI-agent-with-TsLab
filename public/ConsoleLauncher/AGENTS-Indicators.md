# Agent Instructions: Custom Indicators (Functions)

TSLab supports custom indicators as **Function scripts** (in desktop UI they are shown as "Indicators").

This document explains how an agent should:
- create a custom indicator
- edit it via Web API (web editor)
- compile it
- use it inside other scripts (stable linking)

For precompiled handler libraries shipped as `.dll` and stored in DB (upload/replace/delete via API), see `AGENTS-IndicatorDlls.md`.

## Hard rules (for weak/"dumb" models)
- Indicators are **Function** scripts, not files; edit them via `/api/scripts/{name}/ops`.
- A Function must have a **return block** (`FuncResultItem`) connected, or compile fails.
- Use `POST /api/scripts/{name}/compile` (not `build`) to make the indicator available.
- Use DynamicItem + HandlerName, never raw HandlerTypeName.
- A strategy graph that only references the indicator through DynamicItem does not count as implementing the indicator. For a C# indicator prompt, the Function artifact must exist, validate, and compile before the dependent strategy can count as finished.
- A pre-existing DLL-based or third-party handler can be a reference, but it does not satisfy a prompt to implement the indicator in C# unless the user explicitly asked to reuse that existing handler.

## Context note
If you only need the workflow, start with `AGENTS-Indicators-Quick.md`.

## 1) Terminology (must be correct)
- **Script** = `ScriptType.Script` (`TemplateClass.Script`) - runnable strategy (load/build/run).
- **Indicator / Function** = `ScriptType.Function` (`TemplateClass.Function`) - a reusable computation compiled into a dynamic handler.

In `/api/script-manager/tree`:
- indicators typically appear as `nodeType = "Indicator"` with `scriptType = "Function"`.

## 2) Create an indicator
Create a new Function:
- `POST /api/script-manager/scripts`
  - body: `{ "parentScriptId": <folderId>, "name": "MyIndicator", "type": "Function" }`

Tip: prefer a dedicated folder (e.g. "Indicators") and keep names unique.

## 3) Edit an indicator (web editor endpoints)
Indicators are edited with the same endpoints as scripts:
- `GET /api/scripts/{name}/json`
- `POST /api/scripts/{name}/validate`
- `POST /api/scripts/{name}/ops`
- `GET /api/scripts/{name}/explain`

Important Function rule:
- A Function must have a **return block** (`FuncResultItem`) connected to the final signal/value.
- Return type must be supported (typically `DOUBLE` or `BOOL`).
  If the return block is missing/unwired, compilation will fail.

Agent best practice:
- Do not build Function graphs from scratch unless necessary.
  Duplicate an existing working indicator and modify it incrementally (small `ops` batches + `validate` after each).

## 4) Compile an indicator
Compile by name:
- `POST /api/scripts/{name}/compile`

Notes:
- Compile is what makes the indicator available as a dynamic handler for scripts that reference it.
- After changing the indicator graph, **re-compile** it, then rebuild dependent scripts.

## 5) Use an indicator inside a script (stable linking)
Do NOT link an indicator by `HandlerTypeName` (the generated .NET type name is not stable).

Correct approach: add a **Dynamic** block that references the indicator by name.

### 5.1 Create the dynamic block
In the target Script (`TemplateClass.Script`), apply ops:
1) `AddBlock` with `blockType = "DynamicItem"` (this creates `<Block TypeName="DynamicItem">`)
2) Set dynamic binding attributes on the block's `<EditItem>`:
   - `SetEditItemAttribute` with `attributeName = "HandlerName"` and `attributeValue = "<IndicatorName>"`
   - `SetEditItemAttribute` with `attributeName = "HandlerFolder"` and `attributeValue = ""` (optional; leave empty unless you know the folder ID)

Then connect inputs as usual (`Connect` / `ConnectByInputName`), and validate/build.

Why this works:
- At runtime, TSLab resolves `DynamicItem` via `HandlerName` (and optionally `HandlerFolder`).
- If the indicator is recompiled and its generated type changes, `DynamicItem` continues to resolve correctly.

### 5.2 Dependency rule
If a script uses a custom indicator:
1) Compile the indicator: `POST /api/scripts/{indicator}/compile`
2) Build the script: `POST /api/scripts/{script}/build`

If you see handler-not-found errors during build:
- the indicator was not compiled, or
- `HandlerName` does not match the indicator name exactly.
