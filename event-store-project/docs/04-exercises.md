# Event Store Exercises - Hands-On Practice

## How to Use This Guide

Each exercise:
1. States the goal
2. Provides hints
3. Shows expected output
4. Includes solution

Try solving each exercise before looking at the solution.

## Setup

Before starting exercises:

```bash
# 1. Ensure database is running
docker-compose ps

# 2. Clear previous data (fresh start)
docker exec -it event-store-db psql -U eventstore \
  -d eventstore -c "TRUNCATE events"

# 3. Activate virtual environment
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

# 4. Navigate to src directory
cd src
```

## Exercise 1: Create Multiple Orders

**Goal**: Create 3 different orders with different customers.

**Requirements**:
- Order IDs: "order-100", "order-101", "order-102"
- Customer IDs: "alice", "bob", "charlie"
- Each order should be version 1

**Hints**:
```python
# Use events.order_created()
# Use store.append() for each event
# Use Order.load_from_events() to verify
```

**Expected Output**:
```
Created order-100 for alice
Created order-101 for bob
Created order-102 for charlie
```

**Solution**:
```python
from event_store import EventStore
from order import Order
import events

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'eventstore',
    'user': 'eventstore',
    'password': 'eventstore123'
}

def exercise_1():
    store = EventStore(DB_CONFIG)
    
    # Create three orders
    orders_data = [
        ("order-100", "alice"),
        ("order-101", "bob"),
        ("order-102", "charlie")
    ]
    
    for order_id, customer_id in orders_data:
        event = events.order_created(
            order_id=order_id,
            customer_id=customer_id,
            version=1
        )
        store.append(event)
        print(f"Created {order_id} for {customer_id}")
    
    # Verify
    for order_id, _ in orders_data:
        order = Order.load_from_events(order_id, store)
        print(f"✓ Verified: {order}")
    
    store.close()

if __name__ == "__main__":
    exercise_1()
```

**Run**:
```bash
python exercise_1.py
```

## Exercise 2: Build Shopping Cart

**Goal**: Create order with multiple items and calculate total.

**Requirements**:
- Order ID: "order-200"
- Customer: "david"
- Add 3 items:
  - milk: 2 units @ $3.50 each
  - bread: 1 unit @ $2.00
  - eggs: 3 units @ $4.00 each
- Display final total

**Hints**:
```python
# Step 1: Create order (version 1)
# Step 2: Add milk (version 2)
# Step 3: Add bread (version 3)
# Step 4: Add eggs (version 4)
# Step 5: Load order and print total
```

**Expected Output**:
```
Order total: $21.00
Items: 3
```

**Solution**:
```python
from event_store import EventStore
from order import Order
import events

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'eventstore',
    'user': 'eventstore',
    'password': 'eventstore123'
}

def exercise_2():
    store = EventStore(DB_CONFIG)
    
    order_id = "order-200"
    
    # Step 1: Create order
    event = events.order_created(
        order_id=order_id,
        customer_id="david",
        version=1
    )
    store.append(event)
    
    # Step 2: Add items
    items_to_add = [
        ("milk", 2, 3.50),
        ("bread", 1, 2.00),
        ("eggs", 3, 4.00)
    ]
    
    version = 2  # Start after order creation
    for item_id, quantity, price in items_to_add:
        event = events.item_added(
            order_id=order_id,
            item_id=item_id,
            quantity=quantity,
            price=price,
            version=version
        )
        store.append(event)
        version += 1
    
    # Step 3: Load and display
    order = Order.load_from_events(order_id, store)
    print(f"Order total: ${order.total():.2f}")
    print(f"Items: {len(order.items)}")
    print(f"Details: {order}")
    
    store.close()

if __name__ == "__main__":
    exercise_2()
```

## Exercise 3: Modify Order (Add/Remove Items)

**Goal**: Practice adding and removing items from order.

**Requirements**:
- Use order-200 from Exercise 2
- Remove "bread"
- Add "butter": 1 unit @ $3.00
- Display new total

**Hints**:
```python
# Load current version first
# Get latest version: store.get_latest_version()
# Remove bread: version = current + 1
# Add butter: version = current + 2
```

**Expected Output**:
```
Previous total: $21.00
New total: $22.00
```

**Solution**:
```python
from event_store import EventStore
from order import Order
import events

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'eventstore',
    'user': 'eventstore',
    'password': 'eventstore123'
}

def exercise_3():
    store = EventStore(DB_CONFIG)
    order_id = "order-200"
    
    # Load current state
    order_before = Order.load_from_events(order_id, store)
    print(f"Previous total: ${order_before.total():.2f}")
    
    # Get latest version
    current_version = store.get_latest_version("Order", order_id)
    
    # Remove bread
    event_remove = events.item_removed(
        order_id=order_id,
        item_id="bread",
        version=current_version + 1
    )
    store.append(event_remove)
    
    # Add butter
    event_add = events.item_added(
        order_id=order_id,
        item_id="butter",
        quantity=1,
        price=3.00,
        version=current_version + 2
    )
    store.append(event_add)
    
    # Load new state
    order_after = Order.load_from_events(order_id, store)
    print(f"New total: ${order_after.total():.2f}")
    print(f"Items: {list(order_after.items.keys())}")
    
    store.close()

if __name__ == "__main__":
    exercise_3()
```

## Exercise 4: Complete Order Workflow

**Goal**: Implement complete order lifecycle.

**Requirements**:
- Create order (order-300, customer: "emma")
- Add 2 items of your choice
- Pay for order
- Print status at each step

**Expected Output**:
```
Step 1: Order created, status=created
Step 2: Items added, total=$X.XX
Step 3: Order paid, status=paid
```

**Solution**:
```python
from event_store import EventStore
from order import Order
import events

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'eventstore',
    'user': 'eventstore',
    'password': 'eventstore123'
}

def exercise_4():
    store = EventStore(DB_CONFIG)
    order_id = "order-300"
    
    # Step 1: Create order
    event = events.order_created(
        order_id=order_id,
        customer_id="emma",
        version=1
    )
    store.append(event)
    order = Order.load_from_events(order_id, store)
    print(f"Step 1: Order created, status={order.status}")
    
    # Step 2: Add items
    event = events.item_added(
        order_id=order_id,
        item_id="coffee",
        quantity=2,
        price=5.00,
        version=2
    )
    store.append(event)
    
    event = events.item_added(
        order_id=order_id,
        item_id="muffin",
        quantity=1,
        price=3.50,
        version=3
    )
    store.append(event)
    
    order = Order.load_from_events(order_id, store)
    print(f"Step 2: Items added, total=${order.total():.2f}")
    
    # Step 3: Pay
    event = events.order_paid(
        order_id=order_id,
        payment_method="debit_card",
        version=4
    )
    store.append(event)
    
    order = Order.load_from_events(order_id, store)
    print(f"Step 3: Order paid, status={order.status}")
    
    store.close()

if __name__ == "__main__":
    exercise_4()
```

## Exercise 5: Query Event History

**Goal**: Retrieve and analyze event history.

**Requirements**:
- Load all events for order-200
- Count events by type
- Display event timeline

**Expected Output**:
```
Total events: 6
OrderCreated: 1
ItemAdded: 3
ItemRemoved: 1

Timeline:
v1: OrderCreated at 10:00:00
v2: ItemAdded at 10:01:00
...
```

**Solution**:
```python
from event_store import EventStore
from collections import Counter

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'eventstore',
    'user': 'eventstore',
    'password': 'eventstore123'
}

def exercise_5():
    store = EventStore(DB_CONFIG)
    order_id = "order-200"
    
    # Load all events
    events = store.load_events("Order", order_id)
    
    print(f"Total events: {len(events)}")
    
    # Count by type
    event_types = [e.event_type for e in events]
    counts = Counter(event_types)
    
    for event_type, count in counts.items():
        print(f"{event_type}: {count}")
    
    # Display timeline
    print("\nTimeline:")
    for event in events:
        timestamp = event.timestamp.strftime("%H:%M:%S")
        print(
            f"v{event.version}: {event.event_type} "
            f"at {timestamp}"
        )
    
    store.close()

if __name__ == "__main__":
    exercise_5()
```

## Exercise 6: Handle Version Conflicts

**Goal**: Understand optimistic locking with versions.

**Requirements**:
- Try to append event with duplicate version
- Catch and handle the error
- Display error message

**Expected Output**:
```
✗ Error: Version conflict for order-200 version 2
✓ This is expected - versions must be unique
```

**Solution**:
```python
from event_store import EventStore
import events

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'eventstore',
    'user': 'eventstore',
    'password': 'eventstore123'
}

def exercise_6():
    store = EventStore(DB_CONFIG)
    order_id = "order-200"
    
    # Try to add event with existing version
    try:
        event = events.item_added(
            order_id=order_id,
            item_id="duplicate",
            quantity=1,
            price=1.00,
            version=2  # This version already exists
        )
        store.append(event)
        print("✗ Should not reach here")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("✓ This is expected - versions must be unique")
    
    # Correct way: get latest version first
    latest = store.get_latest_version("Order", order_id)
    print(f"\n✓ Latest version is: {latest}")
    print(f"✓ Next event should use version: {latest + 1}")
    
    store.close()

if __name__ == "__main__":
    exercise_6()
```

## Exercise 7: Cancel Order

**Goal**: Implement order cancellation.

**Requirements**:
- Create new order (order-400)
- Add some items
- Cancel order with reason
- Verify final status is "cancelled"

**Expected Output**:
```
Order created and items added
Order cancelled, reason: customer_request
Final status: cancelled
```

**Solution**:
```python
from event_store import EventStore
from order import Order
import events

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'eventstore',
    'user': 'eventstore',
    'password': 'eventstore123'
}

def exercise_7():
    store = EventStore(DB_CONFIG)
    order_id = "order-400"
    
    # Create order
    event = events.order_created(
        order_id=order_id,
        customer_id="frank",
        version=1
    )
    store.append(event)
    
    # Add item
    event = events.item_added(
        order_id=order_id,
        item_id="laptop",
        quantity=1,
        price=999.00,
        version=2
    )
    store.append(event)
    print("Order created and items added")
    
    # Cancel order
    event = events.order_cancelled(
        order_id=order_id,
        reason="customer_request",
        version=3
    )
    store.append(event)
    print("Order cancelled, reason: customer_request")
    
    # Verify
    order = Order.load_from_events(order_id, store)
    print(f"Final status: {order.status}")
    
    store.close()

if __name__ == "__main__":
    exercise_7()
```

## Challenge Exercise: Time Travel Query

**Goal**: Rebuild order state at specific version.

**Requirements**:
- Use order-200
- Show state at version 2 (only first item)
- Show state at version 3 (first two items)
- Show current state

**Hints**:
```python
# Load all events
# Apply events up to target version
# Create custom apply function
```

**Solution**:
```python
from event_store import EventStore
from order import Order

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'eventstore',
    'user': 'eventstore',
    'password': 'eventstore123'
}

def load_order_at_version(order_id, target_version, store):
    """Load order state at specific version."""
    order = Order(order_id)
    events = store.load_events("Order", order_id)
    
    # Apply events up to target version
    for event in events:
        if event.version <= target_version:
            order._apply_event(event)
        else:
            break
    
    return order

def challenge_exercise():
    store = EventStore(DB_CONFIG)
    order_id = "order-200"
    
    # State at version 2
    order_v2 = load_order_at_version(order_id, 2, store)
    print(f"Version 2: {order_v2}")
    
    # State at version 3
    order_v3 = load_order_at_version(order_id, 3, store)
    print(f"Version 3: {order_v3}")
    
    # Current state
    order_current = Order.load_from_events(order_id, store)
    print(f"Current: {order_current}")
    
    store.close()

if __name__ == "__main__":
    challenge_exercise()
```

## Verification Script

Run this to verify all exercises worked:

```python
from event_store import EventStore

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'eventstore',
    'user': 'eventstore',
    'password': 'eventstore123'
}

def verify_all():
    store = EventStore(DB_CONFIG)
    
    # Check orders exist
    order_ids = [
        "order-100", "order-101", "order-102",
        "order-200", "order-300", "order-400"
    ]
    
    print("Verifying orders:\n")
    for order_id in order_ids:
        exists = store.event_exists("Order", order_id)
        version = store.get_latest_version("Order", order_id)
        status = "✓" if exists else "✗"
        print(f"{status} {order_id}: version {version}")
    
    store.close()

if __name__ == "__main__":
    verify_all()
```

## Summary

You have practiced:

```
┌────────────────────────┬──────────────────────────┐
│ Exercise               │ Concept                  │
├────────────────────────┼──────────────────────────┤
│ 1. Multiple orders     │ Event creation           │
│ 2. Shopping cart       │ Multiple events          │
│ 3. Modify order        │ Add/remove items         │
│ 4. Complete workflow   │ Full lifecycle           │
│ 5. Query history       │ Event analysis           │
│ 6. Version conflicts   │ Optimistic locking       │
│ 7. Cancel order        │ State transitions        │
│ Challenge              │ Time travel queries      │
└────────────────────────┴──────────────────────────┘
```

## Next Steps

Week 1 is complete. You understand:
- Event Sourcing pattern
- Event Store implementation
- Aggregate state rebuilding
- Event versioning

Next week: Learn Temporal workflows.