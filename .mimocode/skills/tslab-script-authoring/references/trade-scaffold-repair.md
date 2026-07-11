# Trade Scaffold Repair

- For strategy/trading prompts, the first meaningful scaffold must include one real entry family, `RelativeCommission`, and one protective or profit-taking exit; source-only, Close/Open/High/Low-only, or indicator-only scaffolds are unfinished.
- blank-create or instrument-source alone is still not meaningful progress.
- Prefer direct price-based non-market entry and exit blocks first for breakout, limit, or stop scaffolds when the prompt does not explicitly require a condition-wrapper family.
- prefer direct price-based non-market entry and exit blocks first.
- If you use condition-driven wrappers such as `OpenPositionIf*`, `ChangePositionIf*`, or `ClosePositionIf*`, wire the `Eq`/`EqClear` gate in the same batch. Do not substitute convenience wrappers such as `OpenPositionIf*`, `OpenPositionAt*` when a simpler direct family is enough, and do not add market-entry fallback or proof blocks.
- do not substitute convenience wrappers such as `OpenPositionIf*`, `OpenPositionAt*`.
- Do not use `ChangePosition*` as the first live entry on an empty-position artifact. Do not call the artifact complete while it still has only the initial `OpenPosition*` leg and no real `ChangePosition*` add-to-position leg when the prompt requires scaling/adds.
- Do not call the artifact complete while it still has only the initial OpenPosition* leg and no real ChangePosition* add-to-position leg.
- Keep candles, primary price bands, and derived price-level lines visible when the prompt asks for chart proof. Read-only position/state readers or metrics do not satisfy live trade-path families.
- keep candles, primary price bands, and derived price-level lines.
- read-only position/state readers or metrics.
- switch immediately to a narrow template-block query such as `OpenPosition`, `ClosePosition`, `ChangePosition`, or `RelativeCommission`.
- If build/runtime messages say `ClosePositionByStopItem`, `ClosePositionByProfitItem`, or a close block needs an order price, raw `Close`/`Open`/`High`/`Low`/`Highest`/`Lowest` is not a stop/profit level by itself. Create a derived executable exit price such as `EntryPrice +/- fixed`, percent, ATR, or prompt level, then rerun.
- Raw `Close`/`Open`/`High`/`Low`/`Highest`/`Lowest` is not a stop/profit level by itself.
- If a protective/profit exit is already present but lifecycle says its order price is missing, repair that same exit price stream before optimization, cleanup, or final claims.
- Do not emulate ordinary handlers or trade blocks by setting `handlerTypeName` inside `BoolCustomHandlerItem` / `DoubleCustomHandlerItem` params.
- Older compile errors still visible in `/messages` or `/logs` are stale unless a later validate/build/load/run reproduces them. Do not report an older compiled version of the same artifact as fresh proof.
- older compile errors still visible in `/messages` or `/logs` are stale.
