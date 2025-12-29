# CampaignList
**Source:** phase-2-campaign-management.md
**Route:** /campaigns
**Template:** templates/campaigns.html

## Data (see crc-Campaign.md)
- `campaigns: Campaign[]` - All campaigns ordered by created_at DESC
- `campaign.id: int` - Campaign identifier
- `campaign.name: string` - Campaign title (clickable link to edit)
- `campaign.subject: string` - Email subject line
- `campaign.template_name: string` - Template filename
- `campaign.status: string` - draft/sent
- `campaign.created_at: datetime` - Creation timestamp

## Layout
```
+------------------------------------------------------------------+
|  [Nav: Dashboard | Contacts | Import | Campaigns | SMS Preview]  |
+------------------------------------------------------------------+
|                                                                  |
|  Email Campaigns                           [Create New Campaign] |
|                                                                  |
|  +------------------------------------------------------------+  |
|  | Campaign Name | Subject     | Template    | Status | Created | Actions |
|  +------------------------------------------------------------+  |
|  | Monday Deal   | DOUBLE UP   | Monday Spec | draft  | 2024-12 | [eye][mail][trash] |
|  | Winter Sale   | Holiday...  | monday_spe  | sent   | 2024-12 | [eye][trash] |
|  +------------------------------------------------------------+  |
|                                                                  |
|  (No campaigns yet message if empty)                             |
|                                                                  |
+------------------------------------------------------------------+
```

## Events (see crc-CampaignManager.md)
- `[Create New Campaign]` - Navigate to /campaign/new
- `campaign.name click` - Navigate to /campaign/edit/{id}
- `[eye icon]` - Open /campaign/preview/{id} in new tab
- `[mail icon]` - Navigate to /campaign/send-confirm/{id} (draft only)
- `[trash icon]` - POST /campaign/delete/{id} with JS confirm

## CSS Classes
- `.table` - Main data table with shadow and rounded corners
- `.badge` - Status indicator pill (12px padding, rounded)
- `.badge-draft` - Gray background (#f0f0f0)
- `.badge-sent` - Green background (#4caf50)
- `.btn-primary` - Gradient purple (New Campaign button)
- `.btn-sm` - Small buttons for actions
- `.btn-success` - Green (send button)
- `.btn-danger` - Red (delete button)
- `.campaign-name` - Purple link with hover underline
- `.actions` - Nowrap for action buttons

## Notes
- Sort by created_at descending (newest first)
- Campaign name is clickable link to edit page
- Send button only shown for draft status
- Delete requires JavaScript confirm dialog
- Flash messages displayed at top for success/error
