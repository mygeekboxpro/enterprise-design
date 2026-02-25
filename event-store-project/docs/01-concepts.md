# Event Sourcing & Event Store - Core Concepts

## What is Event Sourcing?

**Definition**: Event Sourcing is a pattern where you store all
changes to application state as a sequence of events.

### Traditional Approach (CRUD)

```
Database stores CURRENT state only.

Orders Table:
┌────┬────────┬───────┬─────────┐
│ ID │ Status │ Total │ Items   │
├────┼────────┼───────┼─────────┤
│ 1  │ paid   │ $50   │ 2       │
└────┴────────┴───────┴─────────┘

Problem: You lost the history.
- When was it created?
- What items were added/removed?
- When was it paid?
```

### Event Sourcing Approach

```
Database stores ALL events (changes).

Events Table:
┌────┬──────────┬─────────────────┬───────────────┐
│ ID │ Order ID │ Event Type      │ Timestamp     │
├────┼──────────┼─────────────────┼───────────────┤
│ 1  │ 1        │ OrderCreated    │ 10:00:00      │
│ 2  │ 1        │ ItemAdded       │ 10:01:00      │
│ 3  │ 1        │ ItemAdded       │ 10:02:00      │
│ 4  │ 1        │ OrderPaid       │ 10:05:00      │
└────┴──────────┴─────────────────┴───────────────┘

Benefit: You have complete history.
- Replay events to get current state
- Audit trail is automatic
- Time travel: see state at any point
```

## What is an Event Store?

**Definition**: A database optimized for storing events in an
append-only log.

### Properties

```
1. APPEND-ONLY
   - New events are added
   - Events are NEVER updated or deleted
   - Immutable history

2. ORDERED
   - Events have sequence numbers
   - Events have timestamps
   - Order matters for replay

3. QUERY BY AGGREGATE
   - Get all events for Order #123
   - Get all events for User #456
   - Fast lookup by entity ID
```

### Event Store vs Regular Database

```
┌─────────────────────┬──────────────┬──────────────┐
│ Feature             │ Event Store  │ Regular DB   │
├─────────────────────┼──────────────┼──────────────┤
│ Operations          │ Append only  │ CRUD         │
│ Updates             │ Not allowed  │ Allowed      │
│ Deletes             │ Not allowed  │ Allowed      │
│ History             │ Full         │ None         │
│ Query current state │ Rebuild      │ Direct       │
│ Audit trail         │ Automatic    │ Manual       │
└─────────────────────┴──────────────┴──────────────┘
```

## Key Terminology

### 1. EVENT

**Definition**: A fact that happened in the past.

```
Event Structure:
{
  "event_id": "uuid-1234",
  "aggregate_id": "order-123",
  "aggregate_type": "Order",
  "event_type": "OrderCreated",
  "data": {
    "customer_id": "cust-456",
    "created_at": "2024-02-17T10:00:00Z"
  },
  "version": 1,
  "timestamp": "2024-02-17T10:00:00Z"
}

Key Points:
- Event names are PAST TENSE (OrderCreated, not CreateOrder)
- Events are IMMUTABLE
- Events contain ALL data needed to apply the change
```

### 2. AGGREGATE

**Definition**: An entity whose state is built from events.

```
Example: Order (the aggregate)

Order #123 has these events:
1. OrderCreated
2. ItemAdded (item: apple)
3. ItemAdded (item: banana)
4. OrderPaid

Current State = Apply events 1→2→3→4

Order {
  id: 123,
  items: [apple, banana],
  status: paid,
  version: 4
}
```

### 3. VERSION

**Definition**: Sequence number for events of an aggregate.

```
Order #123:
┌─────────┬──────────────────┬─────────┐
│ Version │ Event Type       │ Purpose │
├─────────┼──────────────────┼─────────┤
│ 1       │ OrderCreated     │ First   │
│ 2       │ ItemAdded        │ Second  │
│ 3       │ ItemAdded        │ Third   │
│ 4       │ OrderPaid        │ Fourth  │
└─────────┴──────────────────┴─────────┘

Purpose:
- Detect concurrent modifications
- Ensure events are applied in order
- Prevent lost updates
```

### 4. PROJECTION

**Definition**: A read model built from events.

```
Events (write model):
  OrderCreated → ItemAdded → OrderPaid

Projection (read model):
  Order Summary Table
  ┌──────────┬────────┬───────┐
  │ Order ID │ Status │ Total │
  ├──────────┼────────┼───────┤
  │ 123      │ paid   │ $50   │
  └──────────┴────────┴───────┘

Why?
- Events are slow to query
- Projections are fast to query
- Rebuild projections by replaying events
```

## When to Use Event Sourcing

**Term to memorize**

- Event: an immutable record of something that happened.
- Immutable: cannot be changed after written.
- Replay: rebuild state by re-applying events.

Use it when these benefits matter.

### 1) Full audit trail (strong reason)

- You can answer: who did what, when, and why.
- Useful for finance, compliance, security.

### 2) Time travel and debugging

- Rebuild state “as of yesterday”.
- Reproduce bugs by replaying the same events.

### 3) Rich history and analytics

- You can compute trends from event history.
- You can build new projections later.

### 4) Better fit for complex workflows

- Many state transitions.
- Many business rules.
- You want clear “business facts” recorded.

### 5) Event-driven integration

- Other services can subscribe to events.
- Good for microservices and async processing.

---

## When NOT to use Event Sourcing

Avoid it when cost > value.

### 1) Simple CRUD apps

- Basic create/update/delete screens.
- No real need for history.
- A normal relational model is simpler.

### 2) You cannot handle complexity

ES adds:

- event schema design
- versioning
- replay logic
- projections
- eventual consistency issues

### 3) Strong “update in place” requirements

- ES is append-only.
- “Fixing” old data is harder.
- You need compensating events, not edits.

### 4) Query patterns are unpredictable but must be fast

- ES often needs read models (projections).
- You must design projections for queries.
- If you cannot, queries can become slow or messy.

### 5) Strict privacy deletion requirements (risk)

- Laws/policies may require deletion.
- Events are immutable.
- You can encrypt + delete keys, or store PII separately.
- But it is more engineering work.

Term to memorize

- PII: personal identifying information.
- Compensating event: a new event that corrects a previous one.
- Projection (read model): a query-optimized view built from events.
- Eventual consistency: reads may lag behind writes.

---

## Decision table (quick)

| Requirement / Constraint                           | Event Sourcing? |
|----------------------------------------------------|-----------------|
| Need full audit history and “as-of” reconstruction | Yes             |
| Complex domain with many state transitions         | Yes             |
| Need to integrate via events to other services     | Yes             |
| Simple CRUD with little business logic             | No              |
| Team is new and timeline is tight                  | Usually No      |
| Must delete/modify historical records easily       | Usually No      |

---

### GOOD Use Cases

- Payments, ledgers, accounting
- Orders with many states (placed, paid, shipped, returned)
- Insurance claims
- Inventory movements
- Workflow engines / long-running processes

```
✓ Audit requirements
  - Banking: need complete transaction history
  - Healthcare: need patient record changes
  
✓ Domain complexity
  - Business rules require history
  - Temporal queries (state at time T)
  
✓ Debugging
  - Reproduce bugs by replaying events
  - Understand how system reached state
  
✓ Analytics
  - Analyze user behavior over time
  - Track state changes for ML
```

### BAD Use Cases

- Blog/CMS
- Simple internal admin tools
- Basic user profile management (unless strict audit is needed)

```
✗ Simple CRUD apps
  - Blog posts, user profiles
  - No need for history
  
✗ High write volume + simple reads
  - Sensor data collection
  - Log aggregation
  
✗ Frequent schema changes
  - Event schemas are hard to change
  - Migration is complex
```

## Event Sourcing Trade-offs

```
┌────────────────────┬────────────────────────────────┐
│ Benefits           │ Drawbacks                      │
├────────────────────┼────────────────────────────────┤
│ Complete audit log │ Higher storage costs           │
│ Time travel        │ Complex queries                │
│ Rebuild state      │ Eventual consistency           │
│ Event replay       │ Schema evolution hard          │
│ Debug with history │ Learning curve                 │
└────────────────────┴────────────────────────────────┘
```

# Key summary (repeat)

- Use Event Sourcing when history is a product feature.
- Use Event Sourcing when audit + traceability is required.
- Avoid Event Sourcing for simple CRUD and low-complexity domains.

## Event Sourcing Workflow

```
1. User Action
   ↓
2. Load Aggregate from Events
   - Get all events for Order #123
   - Apply events to rebuild state
   ↓
3. Execute Business Logic
   - Validate action
   - Create new event (e.g., OrderPaid)
   ↓
4. Append Event to Event Store
   - Check version (optimistic locking)
   - Store event immutably
   ↓
5. Update Projections (Optional)
   - Update read models
   - Can be done asynchronously
```

## Example: Order Lifecycle

```
State Transitions via Events:

[Empty] 
  → OrderCreated 
    → [Created]
      → ItemAdded 
        → [Created with items]
          → OrderPaid 
            → [Paid]
              → OrderShipped 
                → [Shipped]

At any time:
- Replay events → get current state
- Query events → get full history
- Project events → get summary view
```

## Important Concepts to Memorize

```
┌──────────────────────────────────────────────────────┐
│ TERM              │ DEFINITION                       │
├───────────────────┼──────────────────────────────────┤
│ Event             │ Immutable fact from the past     │
│ Event Store       │ Append-only log of events        │
│ Aggregate         │ Entity built from events         │
│ Version           │ Event sequence number            │
│ Projection        │ Read model from events           │
│ Event Sourcing    │ Pattern: store changes as events │
│ Append-only       │ Add only, never update/delete    │
│ Replay            │ Apply events to rebuild state    │
└───────────────────┴──────────────────────────────────┘
```

## Visual: Event Sourcing Architecture

```
┌─────────────────────────────────────────────────────┐
│                 APPLICATION                         │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Command          Decision         Event           │
│  (User Action) →  (Business   →   (Fact)           │
│                   Logic)                            │
│                                      ↓              │
│                               ┌──────────────┐     │
│                               │ Event Store  │     │
│                               │ (Append-only)│     │
│                               └──────────────┘     │
│                                      ↓              │
│                               ┌──────────────┐     │
│                               │ Projections  │     │
│                               │ (Read Models)│     │
│                               └──────────────┘     │
└─────────────────────────────────────────────────────┘

Write Path: Command → Event → Event Store
Read Path:  Query → Projection (built from events)
```

## Next Steps

After understanding these concepts:

1. Read 02-setup.md for installation
2. Read 03-implementation.md for code walkthrough
3. Complete exercises in 04-exercises.md

**Key Takeaway**: Event Sourcing stores WHAT HAPPENED,
not CURRENT STATE.