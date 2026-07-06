# PowerShell and Body Files

- Use the current shell directly. On Windows PowerShell, use `curl.exe`, `Invoke-RestMethod`, `./api-json.ps1`, `./script-api.ps1`, or `./run-lifecycle.ps1`; do not use bare `curl`, `&&`, `cmd /c`, `pwsh`, nested `powershell -Command`, or POSIX redirection.
- Create localhost request-body JSON under `./tmp/...` with UTF-8 bytes. Never place localhost request-body files under absolute temp aliases such as `/tmp/*.json`, `/workspace/tmp/*.json`, `C:\tmp\*.json`, or `/tmp/lab-options.json`.
- For JSON mutations, prefer a UTF-8 body file plus `curl.exe --data-binary "@file.json"` or `./api-json.ps1`. Do not combine `-d @ops.json` with `--data-binary`, and avoid inline `curl -d`.
- `POST /api/scripts/{name}/ops` must send `{ "ops": [ ... ] }`; the top-level `ops` property must remain an actual JSON array. Do not pre-serialize it into a string.
- Use the canonical `/api/...` form with packaged helpers. If a generic read/write tool rewrites `./tmp/...` outside the workspace, retry with the current shell and the relative `./...` path.
- If the prompt points to a workspace-local spec, prompt file, or other local input artifact, read that exact file and keep the artifact anchored to the file contents.
- `exampleCreatePowerShell` examples from API responses are authoritative for shell quoting when present.
- `./create-script.ps1` writes `./tmp/last-script-artifact.json`; follow with `./script-api.ps1 @last-created ...` or `./run-lifecycle.ps1 @last-created`.
- The packaged helper now also tolerates one foldered full name by splitting the last path segment. Do not guess leaf-only or id-only variants unless that endpoint explicitly advertises them.
