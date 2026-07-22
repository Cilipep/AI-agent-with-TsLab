# Handlers Reference (Auto-Generated)

This reference is generated using reflection and the same metadata used by the script engine (`HandlerCategory`, `InputAttribute`, `HandlerParameter`, etc.).

Assemblies included (when available):
- `TSLab.Script.Handlers` (core handlers)
- `TSLab.Script.Handlers.Options` (options domain handlers)

It is designed for agents that edit scripts through the Web API:
- `GET /api/handlers` and `GET /api/handlers/{typeName}` provide the runtime contract.
- These markdown files provide a stable offline snapshot for agent prompting and reasoning.

Total handlers: 396

## How To Use
- Find a handler by category, then search within the page by `typeName` (class name) used by `/api/handlers/{typeName}` and `AddBlock` ops.
- Use the handler's `InputCount` to choose the correct block container when adding it:
  - `0` -> `ZeroInputItem`
  - `1` -> `ConverterItem`
  - `2+` -> `TwoOrMoreInputsItem`
- Connect inputs by index (`toPort`) or (for template blocks) by named input (`ConnectByInputName`).
- Stream/value note: `OnlyValueHandlersCanUsed` is graph-derived in desktop (not just handler metadata).
  Rely on server validation and `/api/handlers/{typeName}` rather than assuming the markdown `stream-only` flag
  alone is sufficient for POSITION flows.

## Categories
- [CanvasPaneHandler (1)](AGENTS-HandlersReference-CanvasPaneHandler.md)
- [ClusterAnalysis (24)](AGENTS-HandlersReference-ClusterAnalysis.md)
- [GraphPaneHandler (2)](AGENTS-HandlersReference-GraphPaneHandler.md)
- [Indicators (46)](AGENTS-HandlersReference-Indicators.md)
- [Options (18)](AGENTS-HandlersReference-Options.md)
- [OptionsBugs (3)](AGENTS-HandlersReference-OptionsBugs.md)
- [OptionsDeribit (6)](AGENTS-HandlersReference-OptionsDeribit.md)
- [OptionsIndicators (16)](AGENTS-HandlersReference-OptionsIndicators.md)
- [OptionsPositions (50)](AGENTS-HandlersReference-OptionsPositions.md)
- [OptionsPublic (6)](AGENTS-HandlersReference-OptionsPublic.md)
- [OptionsTickByTick (24)](AGENTS-HandlersReference-OptionsTickByTick.md)
- [Portfolio (16)](AGENTS-HandlersReference-Portfolio.md)
- [Position (56)](AGENTS-HandlersReference-Position.md)
- [RusAlgo (1)](AGENTS-HandlersReference-RusAlgo.md)
- [ServiceElements (15)](AGENTS-HandlersReference-ServiceElements.md)
- [TradeMath (84)](AGENTS-HandlersReference-TradeMath.md)
- [TS Channel (7)](AGENTS-HandlersReference-TS_Channel.md)
- [Uncategorized (17)](AGENTS-HandlersReference-Uncategorized.md)
- [VolumeAnalysis (4)](AGENTS-HandlersReference-VolumeAnalysis.md)
