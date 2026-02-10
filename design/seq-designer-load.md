# Sequence: Designer Load Template

**Requirements:** R76, R77, R78, R85, R86, R88
**Refs:** ref-grapesjs-core

## Trigger
User navigates to `/template/designer/<filename>` (from template list or new template creation).

## Flow: Existing Template with Sidecar JSON

```
Browser                  DesignerAPI              GrapesDesigner
  |                           |                         |
  |-- GET /template/ -------->|                         |
  |   designer/<filename>     |                         |
  |                           |-- read <name>.grapes ---|
  |                           |   .json                 |
  |                           |                         |
  |<-- render template_designer.html -------------------|
  |    (with project_json in page data)                 |
  |                           |                         |
  |-- GrapesJS init ---------------------------------->|
  |   loadProjectData(json)   |                         |
  |                           |                         |
  |-- editor ready ---------------------------------->|
```

## Flow: Existing Template WITHOUT Sidecar (Import HTML)

```
Browser                  DesignerAPI              GrapesDesigner
  |                           |                         |
  |-- GET /template/ -------->|                         |
  |   designer/<filename>     |                         |
  |                           |-- no .grapes.json ------|
  |                           |-- read <name>.html -----|
  |                           |                         |
  |<-- render template_designer.html -------------------|
  |    (with raw_html, no project_json)                 |
  |                           |                         |
  |-- GrapesJS init ---------------------------------->|
  |   editor.setComponents(html)                        |
  |                           |                         |
  |-- editor ready ---------------------------------->|
```

## Flow: New Template from Starter

```
Browser                  DesignerAPI              CustomBlocks
  |                           |                         |
  |-- GET /template/ -------->|                         |
  |   designer/new            |                         |
  |   ?starter=special-offer  |                         |
  |                           |                         |
  |<-- render template_designer.html -------------------|
  |    (with starter_json from CustomBlocks)            |
  |                           |                         |
  |-- GrapesJS init ---------------------------------->|
  |   loadProjectData(starter_json)                     |
  |                           |                         |
  |-- user edits & saves ---->|                         |
```

## Notes
- Sidecar JSON is the preferred load path (preserves all component metadata)
- HTML import works but loses some GrapesJS-specific data (component types, traits)
- Starter selection passed as query parameter when creating new templates
