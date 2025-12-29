# SegmentList
**Source:** phase-2-campaign-management.md
**Route:** /segments (see manifest-ui.md)

## Data (see crc-SegmentManager.md)
- `segments: list` - All unique segment tags
- `segment_counts: dict` - Customer count per segment

## Layout
```
+------------------------------------------------------------------+
|  [Nav: Dashboard | Contacts | Import | Campaigns | Segments]     |
+------------------------------------------------------------------+
|                                                                  |
|  Customer Segments                                               |
|                                                                  |
|  +------------------------------------------------------------+  |
|  | Segment Name       | Customers | Actions                    |  |
|  +------------------------------------------------------------+  |
|  | vip                |       150 | View Customers             |  |
|  | pizza-lover        |     2,300 | View Customers             |  |
|  | salad-enthusiast   |       890 | View Customers             |  |
|  | inactive-6months   |       450 | View Customers             |  |
|  | new-customer       |       340 | View Customers             |  |
|  | frequent-visitor   |       620 | View Customers             |  |
|  +------------------------------------------------------------+  |
|                                                                  |
|  Total: 6 segments across 5,000 customers                        |
|  (Customers may belong to multiple segments)                     |
|                                                                  |
|  +------------------------------------------------------------+  |
|  | Assign Segment to Customers                                 |  |
|  +------------------------------------------------------------+  |
|  | Segment: [________________]                                 |  |
|  | Select customers: [Search or filter...]                     |  |
|  |                                                             |  |
|  | [ ] Select all filtered customers                           |  |
|  |                                                             |  |
|  | [Add Segment]                                                |  |
|  +------------------------------------------------------------+  |
|                                                                  |
+------------------------------------------------------------------+
```

## Events (see crc-SegmentManager.md)
- `viewCustomers(segment)` - Navigate to /contacts?segment={segment}
- `addSegment()` - Add segment tag to selected customers
- `searchCustomers(query)` - Filter customer list for selection

## CSS Classes
- `segment-table` - Main data table
- `segment-row` - Individual segment row
- `customer-count` - Count badge
- `btn-link` - View Customers link
- `segment-form` - Bulk assignment form
- `form-input` - Segment name input
- `customer-search` - Customer search input
- `btn-primary` - Add Segment button

## Notes
- Segments derived from customer.segments field
- No separate segments table (stored in customers)
- View Customers filters contacts page
- Bulk assignment for imported contacts
- Segment names normalized to lowercase
