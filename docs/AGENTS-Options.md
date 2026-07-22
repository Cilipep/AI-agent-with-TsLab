# Options Scripts Agent Guide

Use this file when the task is specifically about option-domain graph authoring.
For the common workflow, keep using `AGENTS-FastPath.md`.

## Core model

Option graphs revolve around three data families:

- `OPTION`: option source or option universe
- `OPTION_SERIES`: one expiration series selected from that option source
- `SECURITY`: either the underlying asset or one concrete option contract

The normal pipeline is:

`OPTION` -> `OPTION_SERIES` -> strike selection -> `SECURITY`

## Hard rules

- Option scripts are server-side graphs. Do not edit local files.
- Always set option source mapping with `isOption: true`.
- A successful mapping is only structural proof. It does not prove live or compatible option data.
- Use `GET /api/handlers/{typeName}` for exact ports and parameters.
- Validate after graph edits.
- If runtime-created option UI stays empty together with no-data or source errors, treat that as a runtime blocker on the same artifact. Do not fake the result with manual panes.

## Entry blocks

### Option source
Use a template source block such as:
- `TradableOptionSourceItem`
- `NotTradableOptionSourceItem`

Create it with `AddBlock`, then immediately apply `SetSourceMapping` with:
- exact `dataSourceName` from `GET /api/datasources`
- `securityId`
- `isOption: true`

### Series selection
Use a series-selection block such as `OptionSeriesByNumber` to choose the expiration series.
Do not assume a fixed series exists without proving it on the current datasource.

### Underlying conversion
Use `OptionBase` when you need the underlying security series for time alignment, plotting, or calculations.

### Strike selection
Use one of:
- `CentralStrike`
- a fixed strike parameter
- a formula-derived strike series

### Concrete option contract
Use `SingleOption` to turn a series plus strike rule into one tradable option `SECURITY`.

## Multi-leg structure

For spreads, straddles, condors, or other multi-leg systems:

- keep one shared option source when possible
- keep the series selection explicit
- keep each leg explicit with its own `SingleOption` branch
- share parameters through `ParameterShareItem` or `OneToManyParametersShareItem` instead of copying constants everywhere

## Control panes and canvas panes

- Control panes are optional unless the prompt explicitly requires editable runtime controls.
- Canvas panes are for richer option-specific visuals such as payoff or smile views.
- Do not build manual substitutes for runtime-created option panes while the same artifact still has a no-data or source blocker.

## Troubleshooting

### Series or strike not found
Common causes:
- wrong datasource or option root
- expired or unavailable series
- over-filtered strike step logic
- no data on the current interval or date range

### Wrong series list
Remember that dropdowns or dynamic lists are often derived from connected and mapped option sources at runtime.
If the script has not run on real data yet, those lists may still look incomplete.

## Minimal verification order

1. Prove the current graph shape through `GET /api/scripts/{name}/explain`.
2. Prove mappings through `GET /api/scripts/{name}/json` or `GET /api/scripts/{name}/mappings`.
3. Run `validate -> build -> load -> run`.
4. Read `messages`, `logs`, `ui`, and any option-specific runtime panes.
5. Only then read metrics or present the result as complete.

## Related docs

- `AGENTS-Options-Quick.md`
- `AGENTS-ScriptEditing.md`
- `AGENTS-RunAndAnalyze.md`
- `AGENTS-HandlersReference-Options*.md`