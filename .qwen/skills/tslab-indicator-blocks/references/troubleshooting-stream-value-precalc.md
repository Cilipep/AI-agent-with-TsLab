# Troubleshooting: Stream vs Value vs PreCalc

## Symptoms and fixes

- **Compile/build error about stream/value mismatch**:
  - Re-check `/api/handlers/{typeName}` input definitions.
  - For `IValuesHandlerWithPrecalc`, some inputs may be stream-only unless explicitly declared value-capable in the handler (`Input(..., isValue:true, ...)`).

- **Formula / expression references missing input name**:
  - Re-check the upstream block `CodeName` from `/explain`.
  - Ensure the block is connected and `CodeName` matches what the expression expects.

- **Indicator not found**:
  - Function indicator: ensure it was compiled (`POST /api/scripts/{name}/compile`) and referenced via `DynamicItem.HandlerName`.
  - DLL indicator: ensure the library is loaded (disk or DB upload), then list handlers via `GET /api/handlers` and search.

