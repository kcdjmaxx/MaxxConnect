# Sequence: Segment Filter
**Source Spec:** phase-2-campaign-management.md

## Participants
- CampaignManager: Service orchestrating campaign lifecycle
- SegmentManager: Service for segment operations
- Customer: Domain model entity
- Database: Persistence layer

## Sequence
```
  CampaignManager      SegmentManager          Customer            Database
       |                   |                    |                    |
       |  get_customers_by_segments(segments)   |                    |
       |------------------>|                    |                    |
       |                   |                    |                    |
       |                   | parse_segment_list()|                   |
       |                   |----+               |                    |
       |                   |    |               |                    |
       |                   |<---+               |                    |
       |                   |  segment_list[]    |                    |
       |                   |                    |                    |
       |                   | normalize each     |                    |
       |                   |----+               |                    |
       |                   |    | lowercase     |                    |
       |                   |<---+               |                    |
       |                   |                    |                    |
       |                   | validate each      |                    |
       |                   |----+               |                    |
       |                   |    | check chars   |                    |
       |                   |<---+               |                    |
       |                   |                    |                    |
       |                   |                    |                    |
       | ====== IF segments == "ALL" ======     |                    |
       |                   |                    |                    |
       |                   | SELECT * WHERE subscribed=True          |
       |                   |---------------------------------------------------------->   |
       |                   |                    |                    |                    |
       |                   |<----------------------------------------------------------|
       |                   |  all_customers[]   |                    |                    |
       |                   |                    |                    |
       | ====== ELSE specific segments ======   |                    |
       |                   |                    |                    |
       |                   | SELECT * WHERE segments LIKE any tag    |
       |                   |---------------------------------------------------------->   |
       |                   |                    |                    |                    |
       |                   |<----------------------------------------------------------|
       |                   |  matching_customers[]                   |                    |
       |                   |                    |                    |
       | ====== END IF ======                   |                    |
       |                   |                    |                    |
       |                   | filter subscribed  |                    |
       |                   |----+               |                    |
       |                   |    | email OR sms  |                    |
       |                   |<---+               |                    |
       |                   |                    |                    |
       |<------------------|                    |                    |
       |  customers[]      |                    |                    |
       |                   |                    |                    |
```

## Notes
- "ALL" returns all subscribed customers
- Segment matching is case-insensitive
- Customers must be subscribed (email or SMS) to be included
- SQL LIKE used for comma-separated segment matching
- Consider: future optimization with separate segments table
