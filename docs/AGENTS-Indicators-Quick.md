# Custom Indicators (Quick)

Short workflow for Function scripts.

## Hard rules
- Indicators are **Function** scripts; edit via `/api/scripts/{name}/ops`.
- A Function must have a `FuncResultItem` connected.
- Compile indicators via `POST /api/scripts/{name}/compile` (not build).
- Use DynamicItem with HandlerName to reference the indicator in scripts.
- A strategy graph that merely contains DynamicItem or another reference to the indicator does not itself implement the indicator. For a C# indicator prompt, the Function artifact must exist and compile first.
- A pre-existing DLL-based or third-party handler can be a reference, but it does not satisfy a prompt to implement the indicator in C# unless the user explicitly asked to reuse that existing handler.

## Minimal workflow
1) Create Function: `POST /api/script-manager/scripts` with `type="Function"`.
2) Edit graph: `GET /api/scripts/{name}/explain` -> `POST /api/scripts/{name}/ops`.
3) Validate: `POST /api/scripts/{name}/validate`.
4) Compile: `POST /api/scripts/{name}/compile`.
5) Use in a script via `DynamicItem` (`HandlerName = <IndicatorName>`).

See `AGENTS-Indicators.md` for full details.

For DB-uploaded handler DLL indicator libraries, see `AGENTS-IndicatorDlls.md`.
