# DesignerAPI

**Requirements:** R75, R76, R77, R79, R80, R81, R74
**Refs:** ref-grapesjs-core, ref-existing-template-system

Flask routes that serve the designer page and handle save/load of GrapesJS project data. Acts as bridge between the GrapesJS frontend and the file-based template storage.

## Knows
- template file paths (HTML and sidecar JSON)
- uploads directory paths (dev vs production)
- whether a template has designer data (sidecar exists)

## Does
- Serve designer page for a template (`GET /template/designer/<filename>`)
- Save project data: store JSON sidecar + export inlined HTML (`POST /api/template/save-design`)
- Load project data: return JSON sidecar for GrapesJS to restore (`GET /api/template/load-design/<filename>`)
- Run TemplateProcessor.validate() on exported HTML before saving
- Return validation results to frontend
- Block save if required CAN-SPAM elements missing

## Collaborators
- TemplateProcessor: validate exported HTML
- GrapesDesigner: frontend that calls these endpoints

## Sequences
- seq-designer-save.md
- seq-designer-load.md
