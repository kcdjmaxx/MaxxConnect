# Sequence: Designer Save Template

**Requirements:** R75, R76, R79, R80, R81
**Refs:** ref-grapesjs-core, ref-existing-template-system

## Trigger
User clicks "Save" button in the visual designer.

## Flow

```
GrapesDesigner               DesignerAPI              TemplateProcessor
     |                            |                         |
     |-- get inlined HTML ------->|                         |
     |   (gjs-get-inlined-html)   |                         |
     |                            |                         |
     |-- get project JSON ------->|                         |
     |   (editor.getProjectData)  |                         |
     |                            |                         |
     |-- POST /api/template/ ---->|                         |
     |   save-design              |                         |
     |   {html, json, filename}   |                         |
     |                            |-- validate(html) ------>|
     |                            |                         |
     |                            |<-- ValidationReport ----|
     |                            |                         |
     |                            |-- [if valid] ---------->|
     |                            |   write <name>.html     |
     |                            |   write <name>.grapes   |
     |                            |   .json                 |
     |                            |                         |
     |<-- {success, report} ------|                         |
     |                            |                         |
     |-- show validation panel -->|                         |
     |   (errors/warnings/info)   |                         |
```

## Error Case: Validation Fails

```
GrapesDesigner               DesignerAPI              TemplateProcessor
     |                            |                         |
     |-- POST save-design ------->|                         |
     |                            |-- validate(html) ------>|
     |                            |<-- report.is_valid=F ---|
     |                            |                         |
     |<-- {success: false, -------|                         |
     |     report: {errors}} ---->|                         |
     |                            |                         |
     |-- show errors in panel --->|                         |
     |   (highlight missing       |                         |
     |    compliance elements)    |                         |
```

## Notes
- HTML is exported with CSS inlined via the newsletter preset's juice integration
- JSON sidecar preserves component structure for future re-editing
- Validation uses existing TemplateProcessor with no modifications needed
