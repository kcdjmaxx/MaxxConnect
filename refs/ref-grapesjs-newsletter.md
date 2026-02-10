# ref-grapesjs-newsletter

- **Source:** https://github.com/GrapesJS/preset-newsletter
- **Type:** web
- **Fetched:** 2026-02-07
- **Requirements:** TBD
- **Status:** active
- **Summary:** GrapesJS newsletter preset - email-specific blocks, CSS inlining, email client compatibility.

## Key Details

### Installation
```bash
npm i grapesjs-preset-newsletter
```
CDN: `https://unpkg.com/grapesjs-preset-newsletter`

### Initialization
```javascript
const editor = grapesjs.init({
  container: '#gjs',
  plugins: ['grapesjs-preset-newsletter'],
  pluginsOpts: {
    'grapesjs-preset-newsletter': { /* options */ }
  }
});
```

### Email-Specific Blocks
**Layouts:** sect100 (full-width), sect50 (two columns), sect30 (three columns), sect37 (30/70 split)
**Content:** button, divider, text, image, quote, text-sect (heading + paragraph combo)
**Collections:** grid-items, list-items

### Key Configuration Options
| Option | Default | Purpose |
|--------|---------|---------|
| `inlineCss` | `true` | Auto-inline CSS for email compatibility |
| `updateStyleManager` | `true` | Use email-safe style properties |
| `cmdInlineHtml` | `'gjs-get-inlined-html'` | Command to export inlined HTML |
| `juiceOpts` | `{}` | Custom CSS inliner settings |
| `showBlocksOnLoad` | `true` | Show block manager on startup |

### Built-in Commands
- `gjs-get-inlined-html` - Export with CSS inlined (critical for email)
- `gjs-open-import-template` - Import HTML modal
- `gjs-toggle-images` - Toggle image visibility

### CSS Inlining
Handled automatically via `juice` library. Critical for email client compatibility since most clients strip `<style>` tags.
