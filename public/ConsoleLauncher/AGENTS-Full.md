# Agent Instructions: Full Index

This file is a compatibility index, not the primary workflow brief.
Do not treat it as the first document for low-context runs.

## Primary route

- Start with `AGENTS.md`.
- For common authoring, repair, lifecycle, and delivery rules, open `AGENTS-FastPath.md`.
- For one concrete graph-editing question, open `AGENTS-ScriptEditing.md`.
- For runtime lifecycle and results analysis, open `AGENTS-RunAndAnalyze.md`.
- For optimization, open `AGENTS-Optimization.md`.

## Why this file is short

The old monolithic version duplicated rules that now live in narrower docs and skills.
Keeping the operational rules in one place reduces drift between:
- `AGENTS.md`
- `AGENTS-FastPath.md`
- `CLAUDE-FastPath.md`
- shipped skills under `.opencode/skill/`

## Specialized follow-up docs

- `AGENTS-Auth.md`
- `AGENTS-PortfolioBacktesting.md`
- `AGENTS-ScriptRuntimeParameters.md`
- `AGENTS-DataSources.md`
- `AGENTS-Options.md`
- `AGENTS-ExternalScripts.md`

## Invariants

- `one phase = one shell step`
- keep one current artifact and repair that same artifact in place
- use localhost Web API routes as the source of truth for server-side scripts
- `MissingControlPane` is non-blocking unless the prompt explicitly requires editable runtime controls
- human-facing strategies require readable chart panes
- optimization readiness does not mean optimization should be started