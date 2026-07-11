# Control Pane Wiring

- Control-pane authoring is explicit `/ops` work. Use explicit `/ops` with `AddControlPane` and `AddControlLink` only when editable runtime controls are explicitly required.
- use explicit `/ops` with `AddControlPane` and `AddControlLink`.
- `AddControlPane` alone is not enough. A clean generic authoring-quality response with `controlPaneCount=0` is not enough when the prompt requires controls.
- Every `AddControlLink` needs concrete `dataXml` on the parameter-owning block. Never send `ControlParameterType.NotDefined`, missing `Type`, or placeholder/manual controls.
- Use numeric/int/double up-down controls for numeric parameters, checkbox controls for bools, and combo/list controls for enums or fixed allowed values.
- Keep captions minimal: exact parameter name or short user-supplied caption. Do not add narrative/helper text, block explanations, or template-style labels inside the pane unless the user asked for that UI text.
- For `AddPane`, either omit `position` or pass a structured object such as `{ "x": 150, "y": 200 }`.
