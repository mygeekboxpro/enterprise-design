# Event Store Learning Project

Learn Event Sourcing by building a hands-on order processing 
system.

## What You Will Learn

```
┌─────────────────┬──────────────────────────────────┐
│ Concept         │ Description                      │
├─────────────────┼──────────────────────────────────┤
│ Event Sourcing  │ Store state as sequence of events│
│ Event Store     │ Append-only event database       │
│ Aggregate       │ Entity rebuilt from events       │
│ Versioning      │ Optimistic locking pattern       │
│ Event Replay    │ Reconstruct state from history   │
└─────────────────┴──────────────────────────────────┘
```

## Project Structure

```
event-store-project/
├── docs/
│   ├── 01-concepts.md       # Core concepts & terminology
│   ├── 02-setup.md          # Environment setup guide
│   ├── 03-implementation.md # Code walkthrough
│   └── 04-exercises.md      # Hands-on exercises
├── src/
│   ├── event_store.py       # Event Store implementation
│   ├── events.py            # Event definitions
│   ├── order.py             # Order aggregate
│   └── main.py              # Usage examples
├── tests/
│   └── test_order.py        # Unit tests
├── docker-compose.yml       # PostgreSQL setup
├── requirements.txt         # Python dependencies
├── schema.sql               # Database schema
└── README.md                # This file
```

## Quick Start

### 1. Prerequisites

```bash
# Verify installations
python --version    # Need 3.8+
docker --version    # Need 20.10+
docker-compose --version
```

### 2. Setup Environment

```bash
# Create project directory
mkdir event-store-project
cd event-store-project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Start Database

```bash
# Start PostgreSQL
docker-compose up -d

# Create schema
docker exec -i event-store-db psql -U eventstore \
  -d eventstore < schema.sql

# Verify connection
python test_connection.py
```

### 4. Run Examples

```bash
# Run usage examples
python src/main.py

# Run exercises
python src/exercise_1.py
python src/exercise_2.py
# ... etc
```

## Learning Path

Follow documentation in this order:

```
Step 1: Read docs/01-concepts.md
        ↓ (Understand Event Sourcing fundamentals)
        
Step 2: Read docs/02-setup.md
        ↓ (Setup environment & database)
        
Step 3: Read docs/03-implementation.md
        ↓ (Understand code structure)
        
Step 4: Complete docs/04-exercises.md
        ↓ (Hands-on practice)
        
Step 5: Build your own features
        (Extend with new event types)
```

## Time Estimate

```
┌────────────────────────┬──────────┐
│ Activity               │ Duration │
├────────────────────────┼──────────┤
│ Read documentation     │ 2-3 hrs  │
│ Setup environment      │ 30 mins  │
│ Complete exercises     │ 4-6 hrs  │
├────────────────────────┼──────────┤
│ TOTAL                  │ ~8 hrs   │
└────────────────────────┴──────────┘
```

## Key Concepts

### Event Sourcing
Store ALL state changes as immutable events.

Traditional:
```
UPDATE orders SET status='paid' WHERE id=123
```

Event Sourcing:
```
INSERT INTO events VALUES ('OrderPaid', ...)
```

### Event Store
Append-only database of events.

```
Events Table:
┌────┬──────────┬──────────────┬─────────┐
│ ID │ Order ID │ Event Type   │ Version │
├────┼──────────┼──────────────┼─────────┤
│ 1  │ 123      │ OrderCreated │ 1       │
│ 2  │ 123      │ ItemAdded    │ 2       │
│ 3  │ 123      │ OrderPaid    │ 3       │
└────┴──────────┴──────────────┴─────────┘
```

### Aggregate
Entity whose state is rebuilt from events.

```
Load order 123:
  1. Get all events for order 123
  2. Apply each event in sequence
  3. Result = current order state
```

## Database Schema

```sql
CREATE TABLE events (
    event_id UUID PRIMARY KEY,
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL,
    data JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE(aggregate_type, aggregate_id, version)
);
```

## Code Examples

### Create Event
```python
from events import order_created

event = order_created(
    order_id="order-123",
    customer_id="customer-456",
    version=1
)
```

### Store Event
```python
from event_store import EventStore

store = EventStore(DB_CONFIG)
store.append(event)
```

### Load Aggregate
```python
from order import Order

order = Order.load_from_events("order-123", store)
print(order.total())  # Calculate from events
```

## Common Commands

```bash
# Start database
docker-compose up -d

# Stop database
docker-compose down

# View database logs
docker-compose logs postgres

# Connect to database
docker exec -it event-store-db psql -U eventstore \
  -d eventstore

# Clear all events (reset)
docker exec -it event-store-db psql -U eventstore \
  -d eventstore -c "TRUNCATE events"

# Run tests
pytest tests/

# Format code
black src/
```

## Exercises

```
Exercise 1: Create multiple orders
Exercise 2: Build shopping cart with items
Exercise 3: Modify order (add/remove items)
Exercise 4: Complete order workflow (create→pay)
Exercise 5: Query event history
Exercise 6: Handle version conflicts
Exercise 7: Cancel order
Challenge:  Time travel queries
```

## Troubleshooting

### Port 5432 in use
```bash
# Change port in docker-compose.yml
ports:
  - "5433:5432"
```

### Connection refused
```bash
# Check database status
docker-compose ps

# Restart database
docker-compose restart
```

### Module not found
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Benefits of Event Sourcing

```
✓ Complete audit trail
✓ Time travel (view past state)
✓ Debugging with history
✓ Event replay for testing
✓ Multiple projections from same events
```

## Trade-offs

```
Pros:
+ Full history
+ Audit trail
+ Reproducibility

Cons:
- More storage
- Complex queries
- Schema evolution
```

## Database Credentials

```
Host:     localhost
Port:     5432
Database: eventstore
User:     eventstore
Password: eventstore123
```

**WARNING**: For local development only. Never use in 
production.

## Next Steps

After completing this project:

1. **Extend functionality**
   - Add shipping events
   - Implement refunds
   - Track inventory

2. **Add projections**
   - Order summary table
   - Sales reports
   - Customer history

3. **Learn Temporal** (Week 2)
   - Workflow orchestration
   - Automatic retries
   - State persistence

## Resources

- Event Sourcing Pattern: 
  https://martinfowler.com/eaaDev/EventSourcing.html
  
- PostgreSQL Documentation: 
  https://www.postgresql.org/docs/
  
- Python psycopg2: 
  https://www.psycopg.org/docs/

## Support

If you encounter issues:
1. Check Troubleshooting section
2. Verify setup with test_connection.py
3. Review error messages carefully
4. Ensure database is running

## License

This is educational material for learning purposes.

## Acknowledgments

Project designed for hands-on learning of Event Sourcing 
fundamentals.