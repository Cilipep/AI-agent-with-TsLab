# Using a Handler in a Script Graph (API Ops)

## Minimal workflow (always validate/build/run)

1. Inspect current graph:
   - `GET /api/scripts/{name}/explain`
2. Inspect handler contract:
   - `GET /api/handlers/{typeName}`
3. Add the correct container block:
   - `InputsCount == 0` -> `ZeroInputItem`
   - `InputsCount == 1` -> `ConverterItem`
   - `InputsCount >= 2` -> `TwoOrMoreInputsItem`
4. Set the handler type/name and parameters exactly as shown by `/api/handlers/{typeName}` and `/explain`.
5. Connect inputs by index (`toPort`) or by name (when the op supports it).
6. Validate/build/run:
   - `POST /load` -> `POST /validate` -> `POST /build` -> `POST /run`

## Notes

- For Function indicators: you do not use `typeName`. Use `DynamicItem` + `HandlerName = <FunctionName>`.
- If you see "missing Input0" or similar, it is almost always a wiring mismatch; re-check `/explain` and `/api/handlers/{typeName}`.
