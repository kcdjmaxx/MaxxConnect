# Template Designer Debug - RESOLVED

## Status: FULLY WORKING (2026-02-10) — Tested and saving successfully

All issues fixed. Designer loads, blocks are draggable, content is editable, save works with compliance validation.

## Fixes Applied

### Attempt 3: Agent team fix (2026-02-10)

**Root causes identified (via ref analysis):**

1. **Protocol-relative CDN URLs** — `//unpkg.com/...` on `http://localhost:5001` triggered http→https redirects causing timing/loading failures
2. **Plugin passed as string name** — `plugins: ['grapesjs-preset-newsletter']` relies on GrapesJS internal string→function resolution which may silently fail
3. **No error handling** — If CDN failed, `grapesjs.init()` threw uncaught error with no user feedback
4. **IIFE timing** — No DOMContentLoaded wrapper, script executed immediately
5. **Jinja2-in-JS bug in template_edit.html** — `{{ unsubscribe_link }}` in JS snippet was being evaluated by Jinja2
6. **template_edit.html designer link** — `user:` prefix was stripped before passing to designer URL

**Fixes applied to `templates/template_designer.html`:**
- CDN URLs: `//unpkg.com/...` → `https://cdn.jsdelivr.net/npm/...` (lines 9, 94, 95)
- Plugin: string name → `window['grapesjs-preset-newsletter']` function reference
- Added pre-init guards: checks `typeof grapesjs` and `typeof presetPlugin` before init
- Wrapped in `DOMContentLoaded` instead of IIFE
- Changed arrow function to regular function in customFetch for browser compat

**Fixes applied to `templates/template_edit.html`:**
- Line 410: Wrapped `{{ unsubscribe_link }}` in `{% raw %}...{% endraw %}`
- Line 9: Changed `{{ filename }}` to `{{ route_filename }}` for designer link (preserves `user:` prefix)

**Fixes applied to `app.py`:**
- Added `route_filename=filename` to all `render_template` calls for template_edit (4 locations)

**New file created:**
- `static/test_grapes.html` — Standalone test page to verify GrapesJS loads without Flask/Jinja2

## Test Plan

```
1. Start the app: python app.py
2. First test static page: http://localhost:5001/static/test_grapes.html
   - Status bar should show green "grapesjs: loaded" and "preset: loaded"
   - Editor canvas should render with blocks panel on right
   - If this fails: CDN or version issue
3. Then test the designer: http://localhost:5001/template/designer/WelcomeTemplate.html
   - GrapesJS editor should render with canvas, blocks panel, style panel
   - Drag blocks from right panel onto canvas
   - Click "Save" — should show validation panel
4. Test new template: http://localhost:5001/template/new → choose "Visual Designer"
   - Should redirect to empty designer
5. Test code editor: http://localhost:5001/template/edit/WelcomeTemplate.html
   - Click "Visual Designer" button → should switch to designer
   - Snippet buttons should insert correct text (unsubscribe link should show {{ unsubscribe_link }}, not empty)
```

## Additional Fixes (post-team, during browser testing)

**Fix 7: UMD default export unwrap**
- Preset UMD build exports `{ default: fn }` not a bare function
- Added `.default` unwrap: `if (preset && typeof preset === 'object' && typeof preset.default === 'function')`

**Fix 8: Container height 0px**
- GrapesJS inline style `height: 100%` overrode CSS `calc(100vh - 50px)`, collapsing to 0
- Fixed: `html, body { height: 100% }`, `#gjs { height: ... !important }`, GrapesJS config `height: 'calc(100vh - 50px)'`

**Fix 9: Save validation failing — missing DOCTYPE**
- GrapesJS `gjs-get-inlined-html` exports body content only (no DOCTYPE/html/head/body tags)
- Fixed: save endpoint wraps body-only HTML in proper document structure before validating

## Known Remaining Gaps

- O6: `get_starter_project_json()` returns None — starter template choices all produce empty editor (functional but no pre-built content)
- O7: No automated tests for designer routes
- O8: CDN dependency pinned to `grapesjs@0.21.13` — official demo uses `0.22.2`, could upgrade later

## References Added (2026-02-10)

- `refs/ref-grapesjs-plugin-loading.md` — Plugin loading mechanism (function refs vs strings)
- `refs/ref-grapesjs-preset-umd.md` — Preset UMD build analysis, version compatibility
- `refs/ref-grapesjs-demo-working.md` — Official demo known-working configuration

## Key Files

- `templates/template_designer.html` - The fixed standalone designer
- `static/test_grapes.html` - Standalone verification page
- `templates/template_edit.html` - Code editor with fixed Jinja2 escaping
- `app.py` - Designer routes with route_filename fix
