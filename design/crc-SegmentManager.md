# SegmentManager
**Source Spec:** phase-2-campaign-management.md

## Responsibilities
### Knows
- db_session: Database session for queries

### Does
- get_all_segments(): Return list of unique segments across all customers
- get_segment_counts(): Return customer count per segment
- get_customers_by_segments(segments): Query customers matching any segment
- normalize_segment(tag): Lowercase and trim whitespace
- validate_segment(tag): Check for injection attacks, valid characters
- add_segment_to_customer(customer_id, tag): Add tag to customer
- remove_segment_from_customer(customer_id, tag): Remove tag from customer
- bulk_add_segment(customer_ids, tag): Add tag to multiple customers
- parse_segment_list(comma_separated): Convert string to list

## Collaborators
- Customer: Manages customer segment data
- Campaign: Provides target segments for filtering

## Sequences
- seq-segment-filter.md: Filter customers by segments
- seq-segment-manage.md: Add/remove customer segments
