---
name: tslab-api-indicators
description: "Create/edit/compile TSLab custom indicators as Function scripts via Web API: edit graph with ops, ensure return block, compile (/api/scripts/{name}/compile), and reference from Scripts via DynamicItem+HandlerName. Use for Function/Indicator workflows."
---

# TSLab Web API: Custom Indicators (Functions)

## Hard Rules

- Indicators are **Function** scripts; edit them via `/api/scripts/{name}/ops`.
- A Function must have a return block (`FuncResultItem`) wired, or compile fails.
- Use `POST /api/scripts/{name}/compile` to make it available.
- Reference indicators from scripts via `DynamicItem` + `HandlerName` (never raw `HandlerTypeName`).

## Minimal Workflow

1. Create Function:
   - `POST /api/script-manager/scripts` with `type = Function`
   - Body schema is **no wrapper**: `{ "parentScriptId": 1, "name": "MyIndicator", "type": "Function" }`
2. Edit graph:
   - `GET /api/scripts/{name}/explain`
   - `POST /api/scripts/{name}/ops`
   - `POST /api/scripts/{name}/load`
   - `POST /api/scripts/{name}/validate`
3. Compile:
   - `POST /api/scripts/{name}/compile`
4. Use from a Script:
   - Add `DynamicItem` and set `HandlerName = <IndicatorName>`
   - Build the script.

## Shell JSON Notes (Avoid Quoting Bugs)

For JSON request bodies, prefer one of:
- Write JSON to a UTF-8 file and send bytes with the current shell's native HTTP client, for example `curl -X POST "$base/api/script-manager/scripts" -H "Content-Type: application/json" --data-binary "@create.json"`
- Or let the current shell produce valid JSON directly; in PowerShell that can be `@{ parentScriptId = 1; name = "MyIndicator"; type = "Function" } | ConvertTo-Json | Invoke-RestMethod -Method Post -Uri "$base/api/script-manager/scripts" -ContentType "application/json"`
- If the current shell is Windows PowerShell and you use `curl`, call `curl.exe`.

## Docs Pointer

- To use a Function indicator inside a Script graph: `$tslab-indicator-blocks`
- For graph ops editing: `$tslab-api-script-edit`
- For precompiled indicator DLL libraries stored in DB: `$tslab-api-indicator-dlls`
