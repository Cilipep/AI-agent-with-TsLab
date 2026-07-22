# External Script Blocks Agent Guide

Use this file when the graph contains `ExternalScriptItem` or `ExternalOptionScriptItem`.
These are template blocks that bind to external code.

## Hard rules

- Do not invent server file paths.
- If the user did not provide deployment details, prefer a predefined type binding over file-path binding.
- Always validate and build after edits.
- Input indices are zero-based.
- The number of connected inputs controls which external interface variant is expected.
- Persisted predefined-type binding must be proved through `GET /api/scripts/{name}/json`, not only through `/explain`.

## Two binding modes

### Predefined handler type
Preferred when the handler type is already available on the server.
Use `SetPredefinedHandlerTypeFullName` with a fully qualified type name.

### External scripts list
Use `SetExternalScripts` only when you already know the server-side `.cs`, `.vb`, or `.dll` paths.
These are server filesystem paths, not client paths.
The API does not upload files through this route.

## Verification order

1. Prove the persisted binding through `GET /api/scripts/{name}/json`.
2. Run `validate -> build -> load -> run` on the same artifact.
3. If the task expects runtime-created panes or other runtime artifacts, inspect those endpoints only after run.

Do not keep retrying the binding op just because `/explain` still shows a template-level unresolved handler name.

## Input count semantics

Connected source count selects the expected external interface family:
- 1 input: `IExternal*Script`
- 2 inputs: `IExternal*Script2`
- 3 inputs: `IExternal*Script3`
- 4 inputs: `IExternal*Script4`
- otherwise: `IExternal*ScriptMultiSec`

Connect only the sources you actually need.

## Runtime troubleshooting

### Missing external binding
If codegen reports that no external script is configured, then neither:
- predefined handler type binding
- nor usable script or DLL paths
was persisted.

### Compile or load failures
Possible causes:
- the server cannot compile the source file
- missing dependency DLLs
- wrong assembly or type name

### No visible output
Some external handlers create control panes or canvas panes only at runtime.
After run, inspect:
- `GET /api/scripts/{name}/control-panes`
- `GET /api/scripts/{name}/canvas-panes`

If those panes are still empty together with no-data or source errors, report the runtime blocker instead of faking the UI with manual panes.