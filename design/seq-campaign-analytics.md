# Sequence: Campaign Analytics
**Source Spec:** phase-2-campaign-management.md

## Participants
- Admin: Business user viewing analytics
- AnalyticsView: UI analytics component
- CampaignAnalytics: Service for metrics
- Campaign: Domain model entity
- QRCode: QR code entity
- Database: Persistence layer

## Sequence
```
     Admin            AnalyticsView       CampaignAnalytics        Campaign            QRCode             Database
       |                   |                    |                    |                    |                    |
       |  view analytics   |                    |                    |                    |                    |
       |------------------>|                    |                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   | get_campaign_summary(id)                |                    |                    |
       |                   |------------------->|                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   |                    | load campaign      |                    |                    |
       |                   |                    |----------------------------------->     |                    |
       |                   |                    |                    |                    |                    |
       |                   |                    |                    | SELECT campaign    |                    |
       |                   |                    |                    |----------------------------------->     |
       |                   |                    |                    |                    |                    |
       |                   |                    |                    |<-----------------------------------|
       |                   |                    |<-----------------------------------|    |                    |
       |                   |                    |  campaign data     |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   |                    | get_send_metrics() |                    |                    |
       |                   |                    |----+               |                    |                    |
       |                   |                    |    | from campaign |                    |                    |
       |                   |                    |<---+               |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   |                    | count qr_codes     |                    |                    |
       |                   |                    |------------------------------------------------------>       |
       |                   |                    |                    |                    |                    |
       |                   |                    |                    |                    | COUNT qr_codes     |
       |                   |                    |                    |                    |------------------->|
       |                   |                    |                    |                    |                    |
       |                   |                    |                    |                    |<-------------------|
       |                   |                    |<------------------------------------------------------|      |
       |                   |                    |  qr_count          |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   |                    | calculate_send_rate()                   |                    |
       |                   |                    |----+               |                    |                    |
       |                   |                    |    | sent_at to completed_at            |                    |
       |                   |                    |<---+               |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   |                    | get_failure_reasons()                   |                    |
       |                   |                    |---------------------------------------------------------------------------->
       |                   |                    |                    |                    |                    |
       |                   |                    |<----------------------------------------------------------------------------|
       |                   |                    |  failure_logs[]    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   |<-------------------|                    |                    |                    |
       |                   |  analytics_data    |                    |                    |                    |
       |<------------------|                    |                    |                    |                    |
       |  display dashboard|                    |                    |                    |                    |
       |                   |                    |                    |                    |                    |
```

## Notes
- Metrics include: sent, failed, targeted, completion time
- Send rate calculated from duration between sent_at and completed_at
- QR redemption metrics added in Phase 3
- Failure reasons aggregated from task logs
- Dashboard auto-refreshes during active campaigns
