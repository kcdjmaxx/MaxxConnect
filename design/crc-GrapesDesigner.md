# GrapesDesigner

**Requirements:** R63, R64, R65, R66, R67, R75, R76, R77, R78, R71, R72, R73, R82, R83, R84
**Refs:** ref-grapesjs-core, ref-grapesjs-newsletter, ref-grapesjs-plugin-loading, ref-grapesjs-preset-umd, ref-grapesjs-demo-working

The Jinja2 template page that embeds the GrapesJS editor. Initializes GrapesJS with newsletter preset, configures panels/blocks/storage/assets, and provides the visual designer UI.

## Knows
- template filename being edited
- GrapesJS editor instance
- whether template has existing project JSON (sidecar file)
- current validation state

## Does
- Initialize GrapesJS with newsletter preset and custom config
- Register custom MaxxConnect blocks (compliance footer, QR section, greeting)
- Configure remote storage to save/load via Flask API
- Configure asset manager with image upload endpoint
- Export inlined HTML via `gjs-get-inlined-html` command
- Show validation panel with errors/warnings/info
- Handle mode switching (to code editor)

## Collaborators
- DesignerAPI: save/load project data, validate on save
- TemplateProcessor: validation of exported HTML (server-side)
- ImageUploadAPI: existing endpoint for asset manager uploads

## Sequences
- seq-designer-save.md
- seq-designer-load.md
