---
name: tslab-api-options
description: "Build/edit options scripts (IOption/IOptionSeries pipeline) via Web API ops: option source mapping (isOption), series/strike selection, and ControlPane/CanvasPane patterns."
---

# TSLab Web API: Options Scripts (IOption / IOptionSeries)

Use this skill when working with TSLab option graphs via `/api/scripts/{name}/ops`.

## Hard rules

- Options graphs are server-side; edit only via `/api/scripts/{name}/ops`.
- Always set option source mapping with `isOption: true` (`SetSourceMapping`).
- Use `GET /api/handlers/{typeName}` for exact IO/params; do not guess.
- Validate after ops edits (`POST /validate?strictCodegen=true`) and build (`POST /build`).
- Treat structural proof and runtime proof separately for handlers that create UI during Execute(...): structural gate = graph shape + persisted handler binding + required mappings; runtime gate = named panes/artifacts from the corresponding read endpoints after run.
- A successful SetSourceMapping with isOption: true does not prove compatible/live option data. records=[], CompletedNoData, instrument/source performanceIssue, or empty runtime panes after run are runtime/data blockers on the same artifact.
- If runtime-created UI stays empty under a no-data/source blocker, keep the same artifact and report the blocker. Do not substitute a manual AddPane / AddControlPane graph for a handler-created UI.

## Minimal pipeline (concept)

`TradableOptionSourceItem (OPTION)`
-> `OptionSeriesByNumber (OPTION_SERIES)`
-> strike series (optional: `CentralStrike`)
-> `SingleOption*` (SECURITY option contract)
-> regular SECURITY handlers / trading blocks

## Docs pointer

- Options mental model and patterns: `AGENTS-Options.md` (quick: `AGENTS-Options-Quick.md`)
- Option handler taxonomy (exact IO/params): `AGENTS-HandlersReference-Options*.md`
- UI panes and how to fetch them after run: `AGENTS-RunAndAnalyze.md`

