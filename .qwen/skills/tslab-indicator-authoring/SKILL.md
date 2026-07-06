---
name: tslab-indicator-authoring
description: "Author C# indicator/handler DLLs for TSLab: pick correct handler interfaces (stream vs values vs precalc), apply TSLab attributes, use canonical helper APIs (Series/Indicators), and implement optimization-safe caching/memory pooling (IContext.GetData, IMemoryManagement). Package and load via HandlersFolder hot reload or upload/replace/delete via /api/indicator-dlls (DB-backed)."
---

# TSLab: C# Indicator Authoring (Handler DLLs)

Use this skill when the user asks to **implement an indicator in C#** (a handler class), compile it into a `.dll`, and load it into TSLab (disk handlers folder or DB via Web API).

If the user asks to **use an existing indicator inside a block script** (wire blocks via API ops), prefer `$tslab-indicator-blocks` and `$tslab-api-script-edit`.

## What The Agent Should Do (End-to-End)

When acting as an implementation agent, follow this exact loop and report back what happened:

0. Get the runtime contracts (do not guess):
   - `GET /api/sdk/contracts`
   - Use this response as the runtime source of truth for:
     - which marker interfaces/attributes exist
     - observed `Execute(...)` / `PreCalc(...)` signatures that actually occur in this build
     - copy/paste-ready templates (safe starting points)
   - If you need details for a specific type/method: `GET /api/sdk/types/details?name=<FullTypeName>`
1. Confirm the indicator spec:
   - Inputs and their types (price series, security, positions, option series, etc.)
   - Output type(s) and count
   - Parameters (periods, flags, thresholds)
   - Stream vs values expectation (and whether bar index / precalc is needed)
2. Implement the handler code by starting from a shipped template:
   - Use `references/examples-templates.md` and adapt minimally.
3. Package as a DLL:
   - Create/update a small class library project that references TSLab handler contracts (`TSLab.Script.Handlers`) and helper APIs (`TSLab.Script.Helpers`).
   - Build in Debug when the user wants PDB/breakpoints.
4. Load and verify:
   - Disk hot reload: copy `.dll` (and `.pdb`) to HandlersFolder.
   - DB upload: use `/api/indicator-dlls/{name}` with `description`.
   - Verify the handler is discoverable and schema is correct via:
     - `GET /api/handlers` and `GET /api/handlers/{typeName}`
5. Provide a short outcome report:
   - Handler `typeName`
   - How it was loaded (disk vs DB) + name/version
   - Description sources: API `description` + embedded resource keys
   - Any caveats (stream/value wiring, caching keys, optimization)

## Hard Rules

- Do not reference repo source files (they are not available in delivery agent environments). Use:
  - `GET /api/sdk/contracts` and `GET /api/sdk/types/details`
  - `GET /api/handlers/{typeName}`
- Do not reinvent core primitives. Use the existing TSLab APIs (available at runtime in TSLab):
  - `TSLab.Script.Helpers.Series`
  - `TSLab.Script.Helpers.Indicators`
  - `TSLab.Script.Handlers.IContext` (`GetData`, memory context, optimization flags)
- For temporary buffers, prefer pooled arrays (`Context.GetArray<T>` / `Context.ReleaseArray`) and pass `Context` into `Series.*` where supported.
- Cached data from `Context.GetData(...)` must be treated as **immutable**. Never mutate lists/arrays returned from cache.
- If several exported handlers share an expensive base calculation over the same `ISecurity`/series and parameters, compute that base once through `Context.GetData(...)` and reuse it. Do not make sibling handlers each rescan the same `Bars` window, allocate per-bar bin arrays, or recompute the same regression/profile loop independently.
- A lifecycle timeout on a freshly uploaded DLL is usually a handler-performance bug, not a reason to wait longer or change providers. Reduce unsafe defaults, replace per-bar nested scans with rolling/cached bulk series, rebuild/upload the DLL, and rerun the same artifact.

## Quick Workflow (Author -> Load -> Verify)

1. Decide the handler mode:
   - Market data series: usually **stream** (`IStreamHandler`).
   - Trading/positions/account analytics: usually **values** (`IValuesHandler*`).
   - If values mode requires pre-pass: `IValuesHandlerWithPrecalc` + `PreCalc(...)`.
   - If values mode needs bar index: `IValuesHandlerWithNumber`.
   - Read: `references/contracts-stream-vs-values.md`.
2. Implement the handler:
   - Use the shipped templates/snippets in this skill (and mirror TSLab built-in patterns).
   - Use `Series.*` / `Indicators.*` helpers and optimization-safe pooling/caching.
   - Read: `references/examples-templates.md`, `references/helpers-series-indicators.md`,
     `references/caching-and-memory.md`.
3. Add metadata:
   - `[HandlerCategory]`, `[Description]`.
   - `[InputsCount]` + `[Input(..., isValue: ...)]`, `[OutputsCount]`, `[OutputType]`.
   - Embedded resources for handler display name/description (optional but recommended).
   - Read: `references/attributes-and-metadata.md`.
4. Package and load:
   - Disk: copy `.dll` (and `.pdb` for debugging) into `HandlersFolder`. Hot reload should pick it up.
   - DB: upload via Web API:
     - Use `$tslab-api-indicator-dlls` and `POST /api/indicator-dlls/{name}` with multipart `file` and optional `description`.
5. Verify:
   - `GET /api/handlers` and `GET /api/handlers/{typeName}` should show the handler and its IO/params.
   - Add it to a test script and run once.

## What To Read Next (Only When Needed)

- Stream/value/precalc rules and `InputAttribute.IsValue`: `references/contracts-stream-vs-values.md`
- Attributes and embedded resources for descriptions: `references/attributes-and-metadata.md`
- Using `Series` / `Indicators` correctly: `references/helpers-series-indicators.md`
- Caching + memory pooling + optimization gotchas: `references/caching-and-memory.md`
- Shipped templates you can copy/paste: `references/examples-templates.md`
- Build vs source-only + upload modes: `references/build-and-upload-workflow.md`
