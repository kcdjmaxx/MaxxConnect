# CampaignAnalytics
**Source Spec:** phase-2-campaign-management.md

## Responsibilities
### Knows
- db_session: Database session for queries

### Does
- get_campaign_summary(campaign_id): Return overview metrics
- get_send_metrics(campaign_id): Return sent/failed counts
- get_segment_breakdown(campaign_id): Return metrics by segment
- calculate_send_rate(campaign_id): Compute emails/SMS per minute
- calculate_completion_time(campaign_id): Compute total send duration
- export_report_csv(campaign_id): Generate CSV export
- get_failure_reasons(campaign_id): Aggregate error messages
- update_metrics(campaign_id, metric, value): Increment metric counters

## Collaborators
- Campaign: Source metrics data
- QRCode: Count generated codes (redemption metrics in Phase 3)
- Customer: Segment breakdown data

## Sequences
- seq-campaign-analytics.md: View campaign analytics
- seq-campaign-send.md: Update metrics during send
