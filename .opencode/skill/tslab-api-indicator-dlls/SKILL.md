---
name: tslab-api-indicator-dlls
description: "Manage precompiled handler DLL libraries stored in DB via Web API: list/upload/replace/delete at /api/indicator-dlls, and understand hot-reload/runtime behavior."
---

# TSLab Web API: Indicator DLL Libraries (DB Upload)

This skill is for working with **precompiled .NET handler libraries** (`.dll`) that contain one or more `TSLab.Script.Handlers.IHandler` types and are stored in the DB (not as local files).

Important: this is **not** the same thing as Function indicators. For Function scripts use `$tslab-api-indicators`.

## Endpoints

- List: `GET /api/indicator-dlls`
- Upload/Replace: `POST /api/indicator-dlls/{name}`
  - `Content-Type: multipart/form-data`
  - form field: `file` (the `.dll`)
  - optional form field: `description` (library description; returned by `GET /api/indicator-dlls`)
- List handlers in one library: `GET /api/indicator-dlls/{name}/handlers`
  - Use this (or the upload response `handlerTypeNames`) to read the exact exported handler type names; do not guess them from the file name.
- Delete: `DELETE /api/indicator-dlls/{name}`

## Behavior Notes

- Upload replaces the existing payload **in-place** if `{name}` already exists.
- `{name}` may be specified with or without `.dll` extension.
- The server validates that the DLL is managed and contains at least one `IHandler` type.
- After upload/delete, the running server reloads DB libraries (no restart).
- If the DLL contains embedded resources (`Properties/Resources.resx`), handler names/descriptions can be served via `/api/handlers` and `/api/handlers/{typeName}`.

## Upload Example

Cross-platform `curl` shape:

```bash
base="http://localhost:5000"
token="<Bearer token>"
dll_path="<full-path-to-local-dll>"

curl -X POST "$base/api/indicator-dlls/<LibraryName>" \
  -H "Authorization: Bearer $token" \
  -F "file=@${dll_path}" \
  -F "description=My custom indicators pack"
```

Shell note:
- `curl -F` is the portable default across Windows, macOS, and Linux
- on Windows PowerShell, use `curl.exe`, not the `curl` alias
- on Windows PowerShell 5.1, do not rely on `Invoke-RestMethod -Form`

## Docs Pointer

- To author/build/upload indicator DLLs: `$tslab-indicator-authoring`
- To use DLL handlers in a Script graph: `$tslab-indicator-blocks`
