# CampaignAnalytics
**Source:** phase-2-campaign-management.md
**Route:** /campaigns/<id>/analytics (see manifest-ui.md)

## Data (see crc-CampaignAnalytics.md, crc-Campaign.md)
- `campaign: Campaign` - Campaign with metrics
- `send_metrics: dict` - Sent/failed counts
- `segment_breakdown: dict` - Metrics per segment
- `send_rate: float` - Emails per minute achieved
- `duration_minutes: int` - Total send duration
- `failure_reasons: list` - Aggregated error messages

## Layout
```
+------------------------------------------------------------------+
|  [Nav: Dashboard | Contacts | Import | Campaigns | Segments]     |
+------------------------------------------------------------------+
|                                                                  |
|  Analytics: Pizza Deal Campaign                                  |
|  Status: completed | Sent: Jan 15, 2024 2:30 PM                  |
|                                                                  |
|  +------------+  +------------+  +------------+  +------------+  |
|  |   4,990    |  |     10     |  |   1,180    |  |      5     |  |
|  |   Emails   |  |   Failed   |  |    SMS     |  |   Failed   |  |
|  |    Sent    |  |   Emails   |  |    Sent    |  |    SMS     |  |
|  +------------+  +------------+  +------------+  +------------+  |
|                                                                  |
|  +------------------------------------------------------------+  |
|  | Send Progress                                               |  |
|  +------------------------------------------------------------+  |
|  | [========================================] 100%             |  |
|  | Completed in 49 minutes (avg 102 emails/min)                |  |
|  +------------------------------------------------------------+  |
|                                                                  |
|  +------------------------------------------------------------+  |
|  | Segment Breakdown                                           |  |
|  +------------------------------------------------------------+  |
|  | Segment        | Targeted | Sent  | Failed |                |  |
|  +------------------------------------------------------------+  |
|  | vip            |      150 |   150 |      0 |                |  |
|  | pizza-lover    |    2,300 | 2,295 |      5 |                |  |
|  | inactive       |      450 |   445 |      5 |                |  |
|  +------------------------------------------------------------+  |
|                                                                  |
|  +------------------------------------------------------------+  |
|  | Failed Sends (10 total)                                     |  |
|  +------------------------------------------------------------+  |
|  | Reason                              | Count                 |  |
|  +------------------------------------------------------------+  |
|  | Invalid email address               |     6                 |  |
|  | Mailbox full                        |     3                 |  |
|  | Temporary server error              |     1                 |  |
|  +------------------------------------------------------------+  |
|                                                                  |
|  [Back to Campaign]  [Export CSV]                                |
|                                                                  |
+------------------------------------------------------------------+
```

## Events (see crc-CampaignAnalytics.md)
- `backToCampaign()` - Navigate to /campaigns/{id}
- `exportCSV()` - Download analytics report as CSV
- `refreshMetrics()` - Reload metrics (for in-progress campaigns)

## CSS Classes
- `analytics-dashboard` - Main container
- `stat-card` - Metric card (reuse from dashboard)
- `stat-card-success` - Green for sent counts
- `stat-card-error` - Red for failed counts
- `progress-bar` - Send progress indicator
- `progress-fill` - Filled portion of progress bar
- `segment-table` - Segment breakdown table
- `failure-table` - Failure reasons table
- `btn-primary` - Export CSV button
- `btn-secondary` - Back button

## Notes
- Auto-refresh every 5 seconds during sending
- Progress bar animated during send
- Failure reasons aggregated and counted
- CSV export includes all metrics
- QR redemption metrics added in Phase 3
