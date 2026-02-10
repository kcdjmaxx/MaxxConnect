# ref-grapesjs-preset-umd

- **Source:** https://unpkg.com/grapesjs-preset-newsletter@1.0.2/package.json, https://unpkg.com/grapesjs-preset-newsletter@1.0.2/dist/index.js
- **Type:** web
- **Fetched:** 2026-02-10
- **Requirements:** R63, R65, R66, R67
- **Status:** active
- **Summary:** GrapesJS preset-newsletter v1.0.2 UMD build analysis — how it registers globally, version compatibility, entry points.

## Content Summary

### Package.json Key Fields
```json
{
  "name": "grapesjs-preset-newsletter",
  "version": "1.0.2",
  "main": "dist/index.js",
  "devDependencies": {
    "grapesjs": "^0.21.2"
  }
}
```
- **No peerDependencies declared** — no version enforcement at install time
- devDependency `grapesjs: "^0.21.2"` means compatible with 0.21.2 through 0.21.x
- Semver `^0.21.2` does NOT include 0.22.x (major version 0 treats minor as breaking)

### UMD Registration Pattern
```javascript
!function(e,t){
  'object'==typeof exports&&'object'==typeof module
    ? module.exports=t()
    : 'function'==typeof define&&define.amd
      ? define([],t)
      : 'object'==typeof exports
        ? exports["grapesjs-preset-newsletter"]=t()
        : e["grapesjs-preset-newsletter"]=t()
}
```

Registers as: `window["grapesjs-preset-newsletter"]`

### Entry Point
- `dist/index.js` — minified bundle containing Cheerio DOM utilities, CSS selectors, entity encoding
- Self-contained — does not require GrapesJS to be passed as a dependency during build
- Factory function returns the plugin implementation

### Version Compatibility Reality
- Built against `^0.21.2` — tested with 0.21.x
- The official GrapesJS demo site uses `grapesjs@0.22.2` with this preset
- Likely works with 0.22.x despite semver range, but NOT guaranteed

## Critical: CDN Load Verification
When loaded via `<script src="...">`, verify in browser console:
```javascript
typeof window['grapesjs-preset-newsletter']  // should be "function"
typeof grapesjs  // should be "object"
```
If either is "undefined", the CDN scripts failed to load.
