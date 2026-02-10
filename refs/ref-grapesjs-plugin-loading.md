# ref-grapesjs-plugin-loading

- **Source:** https://grapesjs.com/docs/modules/Plugins.html
- **Type:** web
- **Fetched:** 2026-02-10
- **Requirements:** R63, R64, R65
- **Status:** active
- **Summary:** GrapesJS plugin loading mechanism — how plugins are resolved, function refs vs string names, initialization order.

## Content Summary

### Plugin Definition
Plugins are "simple functions that are run when the editor is initialized." They receive `(editor, options)` parameters.

### String Names vs Function References
- **Modern docs show ONLY function references**, not string names
- String name resolution: GrapesJS looks up `window[pluginName]` for UMD builds
- Function reference (recommended): pass the actual function directly in the `plugins` array

### Plugin Options
Two-part system:
- `plugins: [pluginFn]` — array of plugin functions
- `pluginsOpts: { [pluginFn]: { ...options } }` — options keyed by plugin

### TypeScript Helper
`usePlugin(plugin, opts)` combines plugin + options into a single reference.

### Critical Note
The docs state they apply to "GrapesJS v0.21.2 or higher" but provide NO string-based plugin examples. All examples use direct function references.

## Debugging Implications

For CDN/UMD usage where you can't import modules:
```javascript
// String name (legacy pattern, depends on UMD global registration):
plugins: ['grapesjs-preset-newsletter']

// Function reference (more reliable):
plugins: [window['grapesjs-preset-newsletter']]
```

The string approach requires:
1. The plugin UMD bundle must be loaded BEFORE grapesjs.init()
2. The UMD must register on `window` with the exact string name
3. GrapesJS must look up `window[name]` — if it uses a different lookup, it fails silently
