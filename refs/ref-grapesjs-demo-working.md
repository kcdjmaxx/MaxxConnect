# ref-grapesjs-demo-working

- **Source:** https://grapesjs.com/demo-newsletter-editor.html
- **Type:** web
- **Fetched:** 2026-02-10
- **Requirements:** R63, R64, R65, R66
- **Status:** active
- **Summary:** Official GrapesJS newsletter demo — known-working version combination and CDN URLs.

## Content Summary

### Official Demo Uses
- **GrapesJS:** `0.22.2`
- **CDN:** jsdelivr (NOT unpkg)
- **CSS:** `https://cdn.jsdelivr.net/npm/grapesjs@0.22.2/dist/css/grapes.min.css`
- **JS:** `https://cdn.jsdelivr.net/npm/grapesjs@0.22.2`
- **Protocol:** explicit `https://` (not protocol-relative `//`)

### Key Differences from Our Implementation
| Aspect | Official Demo | Our Code |
|--------|--------------|----------|
| GrapesJS version | 0.22.2 | 0.21.13 |
| CDN provider | jsdelivr | unpkg |
| URL protocol | `https://` | `//` (protocol-relative) |
| Rendering | React/Next.js SSR | Jinja2 template |

### GrapesJS Getting Started CDN Pattern
The official docs use protocol-relative URLs:
```html
<link rel="stylesheet" href="//unpkg.com/grapesjs/dist/css/grapes.min.css" />
<script src="//unpkg.com/grapesjs"></script>
```

### Recommended CDN URLs (from GitHub README)
**jsdelivr:**
```
https://cdn.jsdelivr.net/npm/grapesjs@0.22.2/dist/css/grapes.min.css
https://cdn.jsdelivr.net/npm/grapesjs@0.22.2
```

**CDNJS:**
```
https://cdnjs.cloudflare.com/ajax/libs/grapesjs/X.X.X/grapes.min.js
https://cdnjs.cloudflare.com/ajax/libs/grapesjs/X.X.X/css/grapes.min.css
```

## Actionable Fixes for Our Code

### Fix 1: Use https:// instead of //
Protocol-relative URLs on `http://localhost:5001` resolve to `http://unpkg.com/...`
which redirects to https but may cause timing/CORS issues.

### Fix 2: Consider upgrading to grapesjs@0.22.2
The official demo uses 0.22.2. Since the preset v1.0.2 works with it in the demo,
it should work for us too despite the `^0.21.2` devDependency.

### Fix 3: Use function reference instead of string
```javascript
// Instead of:
plugins: ['grapesjs-preset-newsletter']

// Use:
plugins: [window['grapesjs-preset-newsletter']]
```
This bypasses GrapesJS's internal string→function resolution which may have changed between versions.
