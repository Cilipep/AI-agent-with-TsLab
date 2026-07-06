---
name: tslab-api-script-edit
description: "Legacy wrapper. Route script mutation tasks to the smaller clone/edit skill."
---

# Legacy Wrapper: Script Edit

Do not load this skill unless the user explicitly named `$tslab-api-script-edit` or an older prompt referenced it.

Use `$tslab-script-clone-edit` for:
- script copy/clone
- `GET/PUT /json`
- `POST /ops`
- `validate/build`

Keep these rules:
- Read `GET /api/scripts/{name}/explain` before ops edits.
- For `GET /api/scripts/{name}/json`, read the graph from `response.data`.
- For `PUT /api/scripts/{name}/json`, send only raw `data`.
- Use UTF-8 bytes and `curl --data-binary @file.json`. On Windows PowerShell, call `curl.exe`.
- For `/ops`, send a top-level object shaped like `{ "ops": [ ... ] }`, not a bare array and not a pre-escaped JSON string.
- Inside `/ops`, use canonical field names such as `blockId`, `typeName`, `blockType`, `category`, `fromBlockId`, `toBlockId`, `fromPort`, `toPort`, and `toInputName`. Do not invent alias fields such as `from`, `to`, `block`, `key`, `handlerTypeName`, `fromBlock`, or `toBlock`.
- After the first failed write step, stop instead of guessing alternative endpoints.
