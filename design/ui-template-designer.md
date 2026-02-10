# UI: Template Designer

**Requirements:** R63, R64, R65, R66, R67, R68, R69, R70, R71, R72, R73, R80, R82, R83
**Refs:** ref-grapesjs-core, ref-grapesjs-newsletter

## Layout

```
+------------------------------------------------------------------+
| MaxxConnect  Dashboard  Contacts  Campaigns  [Templates]  ...    |
+------------------------------------------------------------------+
| <- Back to Templates    Edit: welcome.html    [Code Editor] [Save]|
+------------------------------------------------------------------+
|          |                                          |             |
| BLOCKS   |              CANVAS                      |  STYLE MGR  |
|          |                                          |             |
| +------+ |  +--------------------------------------+ | Dimension  |
| | Text | |  |  [Logo Image]                        | | - Width    |
| +------+ |  |                                      | | - Padding  |
| +------+ |  |  [Hero Image - drag to replace]      | |            |
| | Image| |  |                                      | | Typography |
| +------+ |  |  Hello, [[CUSTOMER_NAME]]!           | | - Font     |
| +------+ |  |                                      | | - Size     |
| |Button| |  |  Your content here. Click to edit    | | - Color    |
| +------+ |  |  inline. Drag blocks from left.      | |            |
| +------+ |  |                                      | | Decorations|
| |Divider |  |  [CTA Button - Click Here]           | | - BG Color |
| +------+ |  |                                      | | - Border   |
| +------+ |  |  <!-- QR Code Section -->            | |            |
| |Columns||  |                                      | |            |
| +------+ |  |  --------------------------------    | |            |
|          |  |  Fric & Frac                         | |            |
| MAXXCON  |  |  1700 W 39th St, KC MO 64111        | |            |
| +------+ |  |  Unsubscribe | Privacy Policy        | |            |
| |Footer| |  +--------------------------------------+ |            |
| +------+ |                                          |             |
| | QR   | |                                          |             |
| +------+ |                                          |             |
| |Greet | |                                          |             |
| +------+ |                                          |             |
|          |                                          |             |
+----------+------------------------------------------+-------------+
|                    VALIDATION PANEL                               |
| [Valid] or [2 Errors] [1 Warning]                                |
| - Missing {{ unsubscribe_link }}                                 |
| - Missing physical address                                       |
+------------------------------------------------------------------+
```

## Panel Breakdown

### Left: Block Manager (240px)
- **Standard Blocks** (from newsletter preset): Text, Image, Button, Divider, Quote, Columns (sect100/50/30/37), Grid Items, List Items
- **MaxxConnect Blocks** (custom, separated by header): Compliance Footer, QR Code Section, Customer Greeting

### Center: Canvas (fluid)
- GrapesJS visual canvas
- Click-to-edit inline text editing
- Drag blocks from left panel to canvas
- Drag images from desktop onto image blocks
- Selected component highlighted with blue border

### Right: Style Manager (280px)
- Shows when a component is selected
- Email-safe CSS properties only (from newsletter preset)
- Sections: Dimension, Typography, Decorations

### Bottom: Validation Panel (collapsible, 60px collapsed)
- Shows after save attempt or on demand
- Color-coded: green (valid), red (errors), yellow (warnings)
- Lists specific issues with descriptions

### Top: Toolbar
- "Back to Templates" link
- Template filename display
- "Code Editor" button (with warning modal)
- "Save" button (triggers validation + save)

## Responsive Behavior
- Below 1200px: style manager collapses to icon-toggle
- Below 768px: blocks panel collapses to icon-toggle
- Canvas always takes remaining space
