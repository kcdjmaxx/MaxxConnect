# Sequence: Segment Manage
**Source Spec:** phase-2-campaign-management.md

## Participants
- Admin: Business user managing segments
- SegmentListView: UI segment management view
- SegmentManager: Service for segment operations
- Customer: Domain model entity
- Database: Persistence layer

## Sequence
```
     Admin           SegmentListView      SegmentManager          Customer            Database
       |                   |                    |                    |                    |
       |======= ADD SEGMENT TO CUSTOMER =======|                    |                    |
       |                   |                    |                    |                    |
       |  select customers |                    |                    |                    |
       |------------------>|                    |                    |                    |
       |                   |                    |                    |                    |
       |  enter segment tag|                    |                    |                    |
       |------------------>|                    |                    |                    |
       |                   |                    |                    |                    |
       |  submit           |                    |                    |                    |
       |------------------>|                    |                    |                    |
       |                   |                    |                    |                    |
       |                   | bulk_add_segment() |                    |                    |
       |                   |------------------->|                    |                    |
       |                   |                    |                    |                    |
       |                   |                    | normalize_segment()|                    |
       |                   |                    |----+               |                    |
       |                   |                    |    | lowercase     |                    |
       |                   |                    |<---+               |                    |
       |                   |                    |                    |                    |
       |                   |                    | validate_segment() |                    |
       |                   |                    |----+               |                    |
       |                   |                    |    | check chars   |                    |
       |                   |                    |<---+               |                    |
       |                   |                    |                    |                    |
       |                   |                    |======= LOOP for each customer =======   |
       |                   |                    |                    |                    |
       |                   |                    | load customer      |                    |
       |                   |                    |------------------------------------------->
       |                   |                    |                    |                    |
       |                   |                    |<-------------------------------------------|
       |                   |                    |                    |                    |
       |                   |                    |                    | add_segment()      |
       |                   |                    |------------------->|                    |
       |                   |                    |                    |                    |
       |                   |                    |                    | update segments    |
       |                   |                    |                    |----+               |
       |                   |                    |                    |    |               |
       |                   |                    |                    |<---+               |
       |                   |                    |                    |                    |
       |                   |                    |======= END LOOP ========================|
       |                   |                    |                    |                    |
       |                   |                    | commit transaction |                    |
       |                   |                    |------------------------------------------->
       |                   |                    |                    |                    |
       |                   |<-------------------|                    |                    |
       |                   |  success           |                    |                    |
       |<------------------|                    |                    |                    |
       |  show updated list|                    |                    |                    |
       |                   |                    |                    |                    |
       |                   |                    |                    |                    |
       |======= REMOVE SEGMENT FROM CUSTOMER ===|                    |                    |
       |                   |                    |                    |                    |
       |  select customer  |                    |                    |                    |
       |------------------>|                    |                    |                    |
       |                   |                    |                    |                    |
       |  click remove tag |                    |                    |                    |
       |------------------>|                    |                    |                    |
       |                   |                    |                    |                    |
       |                   | remove_segment()   |                    |                    |
       |                   |------------------->|                    |                    |
       |                   |                    |                    |                    |
       |                   |                    |                    | remove_segment()   |
       |                   |                    |------------------->|                    |
       |                   |                    |                    |                    |
       |                   |                    |                    | update segments    |
       |                   |                    |                    |----+               |
       |                   |                    |                    |    |               |
       |                   |                    |                    |<---+               |
       |                   |                    |                    |                    |
       |                   |                    | commit             |                    |
       |                   |                    |------------------------------------------->
       |                   |                    |                    |                    |
       |                   |<-------------------|                    |                    |
       |                   |  success           |                    |                    |
       |<------------------|                    |                    |                    |
       |  show updated list|                    |                    |                    |
       |                   |                    |                    |                    |
```

## Notes
- Segment tags normalized to lowercase
- Validation prevents injection attacks
- Bulk operations use single transaction
- Customer may have multiple segments (comma-separated)
- Duplicate tags not added (checked before append)
