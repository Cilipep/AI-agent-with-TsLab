# Attributes, Parameters, and Localized Descriptions

This reference is written to be usable in a delivery build (no repo required).

Goal: make a handler DLL show up correctly in UI and via Web API (`/api/handlers`), with correct IO shape and human-friendly docs.

## 1) IO shape (inputs/outputs)

### `[InputsCount]` (required for most custom handlers)

- Fixed arity: `[InputsCount(n)]`
- Range arity: `[InputsCount(min, max)]`

This is used by the engine and by `/api/handlers/{typeName}` to describe the block.

### `[Input]` (one per input index)

`[Input(index, TemplateTypes.<...>, isValue, name)]`

Fields (conceptually):
- `index` (0-based)
- `TemplateTypes` mask (e.g. `TemplateTypes.DOUBLE`, `TemplateTypes.SECURITY`, `TemplateTypes.POSITIONS`)
- `isValue`
  - `false`: stream input (series/security/etc.)
  - `true`: value input (scalar for current bar), most relevant for values handlers and some precalc scenarios
- `name`: stable display name for the port (use short English identifiers; localization can be done via resources if needed)

### `[OutputType]` + `[OutputsCount]`

- Most indicators: `[OutputType(TemplateTypes.DOUBLE)]` and output count defaults to 1
- If output count is not 1, add: `[OutputsCount(n)]`

## 2) Category and visibility

### `[HandlerCategory]`

Categorizes the block in UI and in `/api/handlers`:

```csharp
[HandlerCategory(HandlerCategories.Indicators)]
```

Other common categories depend on your domain (positions, portfolio, etc.).

### Optional presentation attributes

- `[HandlerInvisible]`: hide the handler from UI (advanced/internal)
- `[HandlerDecimals(n)]`: suggest decimals for numeric outputs
- `[HandlerAlwaysKeep]`: keep even if has no outputs (advanced/internal)

## 3) Parameters (`[HandlerParameter]` on public properties)

Expose user-editable parameters via public properties:

```csharp
[HandlerParameter(true, "14", Min = "1", Step = "1")]
public int Period { get; set; } = 14;
```

Key fields:
- `Default` (string) is the default UI value
- `Min` / `Max` / `Step` (strings) define editor limits
- `NotOptimized=true` prevents optimization from sweeping this parameter
- `IsShown=false` hides parameter from UI
- `IsVisibleInBlock` controls block inline presentation

## 4) Caching control

### `[NotCacheable]`

Marks handler as not cacheable by the engine. Use when:
- the handler has side effects
- output depends on external state/time
- caching would be incorrect

Most pure indicators should **not** use this attribute.

## 5) Localized handler and parameter descriptions (recommended)

Prefer embedded `.resx` resources for multilingual UI and Web API docs.

### Resource keys convention (used by `/api/handlers`)

For handler class `MyHandler`:
- `MyHandler.Name`
- `MyHandler.Description`

For a parameter property `Period`:
- `MyHandler.Period.Name`
- `MyHandler.Period.Description`

These are looked up in the handler assembly resource set using the current UI culture.

### Minimal `.resx` structure

- Default: `Properties/Resources.resx`
- Russian: `Properties/Resources.ru-RU.resx`
- English: `Properties/Resources.en-US.resx`

At build time, culture-specific `.resx` files become satellite assemblies:
- `ru-RU/<AssemblyName>.resources.dll`
- `en-US/<AssemblyName>.resources.dll`

When loaded from HandlersFolder, TSLab copies satellites for shadow-loading so localization continues to work during hot reload.

## 6) Fallback: `[Description("...")]`

You can also add `System.ComponentModel.DescriptionAttribute`:

```csharp
[Description("Computes ...")]
```

This is a single string (not localized) unless you generate per-culture binaries.
Use resources when you need proper multilingual support.

