# UI: Template Creation Choice

**Requirements:** R85, R86, R87, R88

## Layout

Modifies the existing `/template/new` page to offer editor choice and starter selection.

```
+------------------------------------------------------------------+
| MaxxConnect  Dashboard  Contacts  Campaigns  [Templates]  ...    |
+------------------------------------------------------------------+
| <- Back to Templates        Create New Template                   |
+------------------------------------------------------------------+
|                                                                   |
|  Template Name: [________________________]                        |
|                                                                   |
|  Choose Editor:                                                   |
|  +---------------------------+  +---------------------------+     |
|  | [icon]                    |  | [icon]                    |     |
|  | VISUAL DESIGNER           |  | CODE EDITOR               |     |
|  |                           |  |                           |     |
|  | Drag-and-drop blocks to   |  | Write HTML directly with  |     |
|  | build your email.         |  | live preview.             |     |
|  | Best for quick layouts.   |  | Best for custom designs.  |     |
|  +---------------------------+  +---------------------------+     |
|                                                                   |
|  [shown when Visual Designer selected]                            |
|  Choose Starter Template:                                         |
|  +------------------+ +------------------+ +------------------+   |
|  | Basic            | | Special Offer    | | Newsletter       |   |
|  | Announcement     | |                  | |                  |   |
|  |  [preview]       | |  [preview]       | |  [preview]       |   |
|  |                  | |                  | |                  |   |
|  | Logo, headline,  | | Hero image, QR   | | Logo, 2-column,  |   |
|  | paragraph, CTA,  | | code, offer text,| | divider, footer  |   |
|  | footer           | | footer           | |                  |   |
|  +------------------+ +------------------+ +------------------+   |
|                                                                   |
|  [shown when Code Editor selected]                                |
|  Choose Starting Point:                                           |
|  ( ) Starter Template  ( ) Blank Template                         |
|                                                                   |
|                              [Create Template]                    |
+------------------------------------------------------------------+
```

## Behavior
- Editor choice cards are mutually exclusive (click to select, highlight border)
- Visual Designer selection reveals starter template gallery
- Code Editor selection reveals existing starter/blank choice
- "Create Template" routes to:
  - Visual: `/template/designer/new?name=<name>&starter=<choice>`
  - Code: `/template/edit/<name>` (existing flow)
