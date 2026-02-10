# Test Design: GrapesJS Template Designer

**Source:** crc-GrapesDesigner.md, crc-DesignerAPI.md, crc-CustomBlocks.md

## Test: Save design with valid compliance elements
**Purpose:** Verify save stores both JSON sidecar and inlined HTML when template is valid
**Input:** GrapesJS project with text block, compliance footer block (has unsubscribe, address, privacy)
**Expected:** JSON file written as `<name>.grapes.json`, HTML file written as `<name>.html`, response includes `success: true` and validation report with no errors
**Refs:** crc-DesignerAPI.md, seq-designer-save.md

## Test: Save blocks when missing required elements
**Purpose:** Verify save is blocked and errors returned when CAN-SPAM elements missing
**Input:** GrapesJS project with text block only, no compliance footer
**Expected:** Response includes `success: false`, validation report lists missing unsubscribe link, missing address, missing privacy link. No files written.
**Refs:** crc-DesignerAPI.md, seq-designer-save.md

## Test: Load template with sidecar JSON
**Purpose:** Verify designer loads project data from sidecar file
**Input:** Navigate to `/template/designer/<filename>` where `<filename>.grapes.json` exists
**Expected:** Page renders with GrapesJS editor, `loadProjectData()` called with sidecar JSON, all components restored
**Refs:** crc-DesignerAPI.md, seq-designer-load.md

## Test: Load template without sidecar (HTML import)
**Purpose:** Verify designer imports raw HTML when no sidecar exists
**Input:** Navigate to `/template/designer/<filename>` where only `.html` exists
**Expected:** Page renders with GrapesJS editor, HTML parsed into components, editable in visual mode
**Refs:** crc-DesignerAPI.md, seq-designer-load.md

## Test: Load starter template for new design
**Purpose:** Verify new template creation with starter
**Input:** Navigate to `/template/designer/new?name=test&starter=special-offer`
**Expected:** Page renders with GrapesJS editor loaded with Special Offer starter JSON, includes hero image placeholder, QR section, compliance footer
**Refs:** crc-CustomBlocks.md, seq-designer-load.md

## Test: Custom compliance footer block
**Purpose:** Verify custom block contains all required CAN-SPAM elements
**Input:** Drag "Compliance Footer" block onto canvas, export HTML
**Expected:** Exported HTML contains `{{ unsubscribe_link }}`, physical address (1700 West 39th St), privacy policy link
**Refs:** crc-CustomBlocks.md

## Test: Image upload via asset manager
**Purpose:** Verify drag-drop image uploads work through GrapesJS asset manager
**Input:** Drag PNG image onto image component in canvas
**Expected:** Image uploaded to `/api/template/upload-image`, returned URL inserted into component, image visible in canvas
**Refs:** crc-GrapesDesigner.md

## Test: Mode switch to code editor
**Purpose:** Verify switching preserves template content with appropriate warning
**Input:** Click "Code Editor" button in designer
**Expected:** Warning modal displayed ("Visual editor metadata will be lost"), on confirm redirects to `/template/edit/<filename>`, HTML content preserved
**Refs:** crc-GrapesDesigner.md
