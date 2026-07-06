---
name: tslab-api-optimization
description: "Legacy wrapper. Route optimization tasks to the smaller optimization-run skill."
---

# Legacy Wrapper: Optimization

Do not load this skill unless the user explicitly named `$tslab-api-optimization` or an older prompt referenced it.

Use `$tslab-optimization-run` for:
- `SetOptimizationRange`
- optimization start/status
- Top-K results
- rerun of best candidate

Keep these rules:
- Use `paramInvariantName`, not `paramName`.
- Always set a baseline `value` for ranged params.
- Do not mix `SetParam` with `SetOptimizationRange` for the same parameter.
- Prefer UTF-8 files plus `curl --data-binary`. On Windows PowerShell, call `curl.exe`.
