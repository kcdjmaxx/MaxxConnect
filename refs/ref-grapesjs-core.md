# ref-grapesjs-core

- **Source:** https://grapesjs.com/docs/getting-started.html
- **Type:** web
- **Fetched:** 2026-02-07
- **Requirements:** TBD
- **Status:** active
- **Summary:** GrapesJS core framework docs - initialization, blocks, panels, style manager, storage.

## Key Details

### Initialization
```javascript
const editor = grapesjs.init({
  container: '#gjs',
  fromElement: true,
  height: '300px',
  width: 'auto',
  storageManager: false,
  panels: { defaults: [] },
});
```

### CDN Links (from docs — protocol-relative)
```html
<link rel="stylesheet" href="//unpkg.com/grapesjs/dist/css/grapes.min.css" />
<script src="//unpkg.com/grapesjs"></script>
```

### CDN Links (from GitHub README — explicit https)
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/grapesjs@0.22.2/dist/css/grapes.min.css" />
<script src="https://cdn.jsdelivr.net/npm/grapesjs@0.22.2"></script>
```

**Note:** Official demo at grapesjs.com uses jsdelivr with `https://` and version 0.22.2.

### Block Manager
Blocks are draggable content elements. Configure via `blockManager.blocks` array with `id`, `label`, `content` fields. Can append to a sidebar element via `appendTo`.

### Storage Manager
- `type`: 'local' or 'remote'
- `autosave`, `autoload` booleans
- Remote: `urlLoad` (GET), `urlStore` (POST)
- Project data: `editor.getProjectData()` / `editor.loadProjectData(data)`
- Custom storage via `editor.Storage.add('type', { load, store })`
- **Important:** Persist JSON project data, not just HTML. HTML export loses component metadata.

### Asset Manager
- `upload`: server endpoint URL
- `uploadName`: POST param name (default: 'files')
- Server response format: `{ data: ['url1', { src: 'url2', type: 'image', height: 100, width: 200 }] }`
- Events: `asset:upload:start`, `asset:upload:end`, `asset:upload:error`, `asset:upload:response`

### Panels & Commands
Custom panels with buttons that execute commands. Used for toolbar actions (export, save, undo/redo).

### Style Manager
Sectors with CSS properties. Can restrict to email-safe properties via newsletter preset.
