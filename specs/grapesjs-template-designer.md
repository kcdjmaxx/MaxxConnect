# GrapesJS Drag-and-Drop Email Template Designer

**Language:** Python 3.11 (Flask backend), JavaScript (GrapesJS frontend)
**Environment:** Flask/Jinja2 web app, Railway.app production deployment
**Date:** 2026-02-07

## Overview

Add a visual drag-and-drop email template designer to MaxxConnect using GrapesJS with the newsletter preset. This coexists alongside the existing code editor, giving users two modes: a visual designer for quick template building and the code editor for fine-tuning HTML.

## Problem Statement

The current template editor is a raw HTML code editor (textarea). Non-technical users (restaurant staff, marketing managers) struggle to create professional email templates without HTML knowledge. A visual drag-and-drop interface would let them build templates by dragging content blocks (text, images, buttons, layouts) onto a canvas and configuring them via point-and-click.

## Feature: Visual Template Designer

### Editor Canvas
- Full-screen GrapesJS editor embedded in a Jinja2 template page
- Uses the `grapesjs-preset-newsletter` for email-specific blocks and CSS inlining
- Canvas renders the email template visually with click-to-edit inline editing
- Side panel with block library, style manager, and layer manager

### Content Blocks (Drag and Drop)
Standard email blocks from the newsletter preset:
- **Text** - Rich text with formatting (bold, italic, underline, links)
- **Image** - Drag image from desktop or select from asset manager
- **Button** - CTA button with customizable text, color, link
- **Divider** - Horizontal rule
- **Layouts** - Full-width, 2-column, 3-column, 30/70 split sections
- **Quote** - Blockquote styling
- **Grid/List items** - Repeatable content groups

Custom MaxxConnect blocks:
- **Compliance Footer** - Pre-built block with unsubscribe link, address, privacy link (all required CAN-SPAM elements)
- **QR Code Section** - Placeholder block with `<!-- QR_CODE_SECTION -->` marker
- **Customer Greeting** - Text block pre-filled with `[[CUSTOMER_NAME]]` placeholder

### Image Handling
- Drag-and-drop images directly onto the canvas from desktop
- GrapesJS asset manager configured with the existing `/api/template/upload-image` endpoint
- Uploaded images stored in `uploads/images/` (Railway volume in production)
- Image gallery showing previously uploaded images for reuse
- File type validation (PNG, JPG, GIF) and size limit (2MB)

### Save and Load
- Save stores both:
  - **GrapesJS project JSON** - for re-editing in the visual designer (preserves component structure)
  - **Inlined HTML** - the final email-ready output with CSS inlined (via `gjs-get-inlined-html` command)
- Project JSON stored as a sidecar file: `<template-name>.grapes.json` alongside `<template-name>.html`
- Load detects if a `.grapes.json` file exists and loads the visual designer; otherwise falls back to code editor
- Templates without a JSON sidecar can be imported into the visual designer via the existing GrapesJS import command

### Compliance Validation
- On save, run the existing `TemplateProcessor.validate()` on the exported HTML
- Show validation results (errors/warnings/info) in a panel
- Block saving if required elements are missing (unsubscribe link, address, privacy policy)
- Offer to auto-inject missing elements via `TemplateProcessor.process_all()`

### Mode Switching
- Template list page shows an "Edit" button that routes to the appropriate editor:
  - If `.grapes.json` exists: opens visual designer
  - Otherwise: opens code editor
- Visual designer has a "Switch to Code Editor" button (warns that switching loses visual editor metadata)
- Code editor has a "Switch to Visual Designer" button (imports current HTML into GrapesJS)
- New template creation offers choice: "Visual Designer" or "Code Editor"

## Feature: Starter Templates for Visual Designer

- 2-3 pre-built GrapesJS project JSON files as starter templates:
  - **Basic Announcement** - Logo, headline, paragraph, button, compliance footer
  - **Special Offer** - Hero image, headline, offer details, QR section, compliance footer
  - **Newsletter** - Logo, 2-column content section, divider, compliance footer
- Users select a starter when creating a new template in visual mode
- Starters include all compliance elements pre-configured

## Integration Points

### Existing Routes to Modify
- `/templates` (GET) - Add visual/code editor indicators, route "Edit" to correct editor
- `/template/new` (GET/POST) - Add visual designer option to creation flow

### New Routes
- `/template/designer/<path:filename>` (GET) - Visual designer page
- `/api/template/save-design` (POST) - Save both JSON + HTML from designer
- `/api/template/load-design/<path:filename>` (GET) - Load project JSON for designer

### Existing Routes Reused (No Changes)
- `/api/template/upload-image` (POST) - Image upload (already compatible with GrapesJS asset manager response format with minor adaptation)
- `/template/images/<filename>` (GET) - Serve uploaded images
- `/template/preview/<filename>` (GET) - Preview template
- `/template/delete/<filename>` (POST) - Delete template (also deletes sidecar JSON)

## Non-Goals (Explicitly Out of Scope)
- Mobile-specific editing (single responsive layout is sufficient)
- Real-time collaboration
- Template version history
- AI-assisted content generation
- SMS template designer (email only)
