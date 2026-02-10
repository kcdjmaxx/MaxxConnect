# CustomBlocks

**Requirements:** R68, R69, R70, R86, R87, R88, R85
**Refs:** ref-grapesjs-newsletter, ref-existing-template-system

JavaScript module that registers MaxxConnect-specific custom blocks in the GrapesJS block manager. These blocks pre-populate compliance elements and personalization placeholders.

## Knows
- business address string
- privacy policy URL
- unsubscribe link template syntax
- customer name placeholder syntax
- QR code section comment syntax
- starter template JSON structures

## Does
- Register "Compliance Footer" block (unsubscribe + address + privacy in table layout)
- Register "QR Code Section" block (placeholder comment with surrounding table structure)
- Register "Customer Greeting" block (heading with `[[CUSTOMER_NAME]]`)
- Provide starter template project JSON data (Basic Announcement, Special Offer, Newsletter)

## Collaborators
- GrapesDesigner: registers these blocks during editor initialization

## Sequences
- seq-designer-load.md (starter templates loaded here)
