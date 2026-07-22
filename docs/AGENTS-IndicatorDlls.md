# Agent Instructions: Indicator DLL Libraries (DB Upload)

TSLab can load handler libraries (DLLs that contain `IHandler` types) not only from `HandlersFolder`, but also from the DB.

This doc describes the **Web API endpoints** to upload/replace/delete such DLLs and how they behave at runtime.

Important: this is **not** the same thing as "custom indicators" (Function scripts). For Function scripts see `AGENTS-Indicators.md`.

## What This Feature Is

- A "DB indicator DLL" is a managed `.dll` that contains one or more types implementing `TSLab.Script.Handlers.IHandler`.
- The DLL bytes are stored in the existing `Script` + `Payload` tables (no DB schema changes).
- After upload/delete the running server hot-reloads these libraries (no restart).

## API Endpoints

All endpoints require auth (`Authorization: Bearer <token>`) unless your environment uses TrustedClients bypass.

### List

- `GET /api/indicator-dlls`

Returns a list with (at least) `scriptId`, `name`, `version`, `sha256`, `uploadedAtUtc`, `description`.

### Upload / Replace

- `POST /api/indicator-dlls/{name}`
  - `Content-Type: multipart/form-data`
  - form field: `file` = DLL file
  - optional form field: `description` = library description (string, max 2000 chars)

Notes:
- If `{name}` already exists, the payload is **replaced** (update-in-place).
- `{name}` may be provided with or without `.dll` extension.
- The server validates that the DLL is a managed assembly and contains at least one `IHandler` type.

Cross-platform example (`curl`):
```bash
base="http://localhost:5000"
token="<Bearer token>"
dll_path="<full-path-to-local-dll>"

curl -X POST "$base/api/indicator-dlls/MyHandlers" \
  -H "Authorization: Bearer $token" \
  -F "file=@${dll_path}" \
  -F "description=My custom indicators pack"
```

Shell note:
- the `curl -F` example above is the portable default across Windows, macOS, and Linux
- if the current shell is Windows PowerShell, use `curl.exe`, not the `curl` alias
- on Windows PowerShell 5.1, do not rely on `Invoke-RestMethod -Form`

Example (PowerShell 7+ only):
```powershell
$token = "<Bearer token>"
$dllPath = "<full-path-to-local-dll>"
Invoke-RestMethod -Method Post `
  -Uri "http://localhost:5000/api/indicator-dlls/MyHandlers" `
  -Headers @{ Authorization = "Bearer $token" } `
  -Form @{ file = Get-Item $dllPath; description = "My custom indicators pack" }
```

### Delete

- `DELETE /api/indicator-dlls/{name}`

Cross-platform example (`curl`):
```bash
base="http://localhost:5000"
token="<Bearer token>"

curl -X DELETE "$base/api/indicator-dlls/MyHandlers" \
  -H "Authorization: Bearer $token"
```

## Runtime Notes / Gotchas

- Hot-reload applies to these DB libraries immediately after upload/delete.
- The DLLs are stored under a hidden special folder in the script tree: `.dll-indicators`.
  - Leaf nodes are stored as `ScriptType.Folder` on purpose, so WPF ScriptManager will not try to open them in editors.
- Debugging (PDB) is supported for handler DLLs from `HandlersFolder` (shadow copy keeps `.pdb` next to the loaded module).
  - DB-uploaded DLLs currently support **DLL only** (no PDB upload).

## Handler Descriptions From DLL Resources

If your DLL embeds resources (e.g. `Properties/Resources.resx`), Web API will use them to provide handler docs via:
- `GET /api/handlers`
- `GET /api/handlers/{typeName}`

Expected keys (short type name):
- Display name: `<TypeName>.Name`
- Description: `<TypeName>.Description`
- Parameter display name: `<TypeName>.<ParamName>.Name`
- Parameter description: `<TypeName>.<ParamName>.Description`
- Formula summary: `<TypeName>.Formula`
- Meaning summary: `<TypeName>.Meaning`
- Plot summary: `<TypeName>.Plot`
- Parameter effect summary: `<TypeName>.<ParamName>.Effect`

For bilingual Russian/English docs in the current single-DLL upload flow, put both locales into the same neutral `Properties/Resources.resx`:
- English: `<key>.en`
- Russian: `<key>.ru`
- Fallback: unsuffixed `<key>` should remain English.
- Keep the scaffolded resource structure. Every display/doc key you keep or add must have base + `.en` + `.ru`; do not replace `Resources.resx` with a minimal file that deletes `.en`/`.ru` variants.
- Replace scaffold placeholder values with concise task-specific English and Russian text before building. Do not leave `Replace this...`, `Describe...`, `Замените...`, or `Опишите...` placeholder docs in the final DLL.

If upload returns `code=IncompleteBilingualResourceDocs` or `missingResourceKeys=[...]`, add every listed key in one `Resources.resx` edit, then rebuild and upload once. Do not fix resource keys one upload at a time.

Do not rely on satellite `Resources.ru.resx` assemblies unless that deployment uploads the satellite DLLs together with the handler DLL.

## Runtime Performance

For the first live proof, keep custom stream handlers bounded. Avoid per-bar nested `rows * lookback` scans across the full history; prefer `O(n * lookback)` or better algorithms, modest safe defaults, and cached rolling calculations. For histogram/profile/binning handlers with `Rows`-like parameters, bound the bins and use rolling or incremental state for the first proof. If build/load/run later says the script is still initializing, repair every plotted/exported handler that still uses the slow algorithm, rebuild/upload the whole DLL, and rerun lifecycle on the same artifact.
