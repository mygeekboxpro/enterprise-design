# Event Store Implementation - Code Walkthrough

## Overview

You will create 4 Python files:
```
src/
├── events.py       # Event classes
├── event_store.py  # Event Store logic
├── order.py        # Order aggregate
└── main.py         # Usage examples
```

Each file is explained step-by-step below.

## File 1: events.py - Event Definitions

**Purpose**: Define event classes and base event structure.

Create `src/events.py`:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
import uuid


# Base Event Class
# ----------------
# All events inherit from this.
# Provides common fields for every event.

@dataclass
class Event:
    """
    Base class for all events.
    
    Fields:
    - event_id: unique identifier (auto-generated)
    - aggregate_type: entity type (e.g., "Order")
    - aggregate_id: specific entity ID (e.g., "order-123")
    - event_type: name of event (e.g., "OrderCreated")
    - version: sequence number for this aggregate
    - data: event-specific payload
    - timestamp: when event occurred
    """
    event_id: str
    aggregate_type: str
    aggregate_id: str
    event_type: str
    version: int
    data: Dict[str, Any]
    timestamp: datetime
    
    @staticmethod
    def create(aggregate_type: str, aggregate_id: str, 
               event_type: str, version: int, 
               data: Dict[str, Any]) -> 'Event':
        """
        Factory method to create events.
        Auto-generates event_id and timestamp.
        
        Example:
            Event.create(
                aggregate_type="Order",
                aggregate_id="123",
                event_type="OrderCreated",
                version=1,
                data={"customer_id": "456"}
            )
        """
        return Event(
            event_id=str(uuid.uuid4()),
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            version=version,
            data=data,
            timestamp=datetime.utcnow()
        )


# Specific Event Types
# --------------------
# These are helper functions to create domain events.
# They enforce event structure and naming.

def order_created(order_id: str, customer_id: str, 
                  version: int = 1) -> Event:
    """
    Create OrderCreated event.
    
    This event marks the creation of a new order.
    
    Args:
        order_id: unique order identifier
        customer_id: who created the order
        version: event version (default: 1)
    
    Returns:
        Event instance
    """
    return Event.create(
        aggregate_type="Order",
        aggregate_id=order_id,
        event_type="OrderCreated",
        version=version,
        data={
            "customer_id": customer_id,
            "status": "created"
        }
    )


def item_added(order_id: str, item_id: str, 
               quantity: int, price: float, 
               version: int) -> Event:
    """
    Create ItemAdded event.
    
    This event records adding an item to an order.
    
    Args:
        order_id: which order
        item_id: which item
        quantity: how many
        price: price per item
        version: event version (increment from last)
    
    Returns:
        Event instance
    """
    return Event.create(
        aggregate_type="Order",
        aggregate_id=order_id,
        event_type="ItemAdded",
        version=version,
        data={
            "item_id": item_id,
            "quantity": quantity,
            "price": price
        }
    )


def item_removed(order_id: str, item_id: str, 
                 version: int) -> Event:
    """
    Create ItemRemoved event.
    
    This event records removing an item from an order.
    
    Args:
        order_id: which order
        item_id: which item to remove
        version: event version
    
    Returns:
        Event instance
    """
    return Event.create(
        aggregate_type="Order",
        aggregate_id=order_id,
        event_type="ItemRemoved",
        version=version,
        data={
            "item_id": item_id
        }
    )


def order_paid(order_id: str, payment_method: str, 
               version: int) -> Event:
    """
    Create OrderPaid event.
    
    This event records payment for an order.
    
    Args:
        order_id: which order
        payment_method: how they paid
        version: event version
    
    Returns:
        Event instance
    """
    return Event.create(
        aggregate_type="Order",
        aggregate_id=order_id,
        event_type="OrderPaid",
        version=version,
        data={
            "payment_method": payment_method,
            "status": "paid"
        }
    )


def order_cancelled(order_id: str, reason: str, 
                    version: int) -> Event:
    """
    Create OrderCancelled event.
    
    This event records order cancellation.
    
    Args:
        order_id: which order
        reason: why cancelled
        version: event version
    
    Returns:
        Event instance
    """
    return Event.create(
        aggregate_type="Order",
        aggregate_id=order_id,
        event_type="OrderCancelled",
        version=version,
        data={
            "reason": reason,
            "status": "cancelled"
        }
    )
```

**Key Concepts in events.py:**

```
┌─────────────────┬──────────────────────────────────┐
│ Concept         │ Explanation                      │
├─────────────────┼──────────────────────────────────┤
│ @dataclass      │ Python decorator for data class  │
│ Event.create()  │ Factory method, auto-fills ID    │
│ uuid.uuid4()    │ Generate unique event ID         │
│ datetime.utcnow │ Current timestamp in UTC         │
│ version         │ Must increment for each event    │
│ data            │ Dictionary with event payload    │
└─────────────────┴──────────────────────────────────┘
```

## File 2: event_store.py - Event Store Implementation

**Purpose**: Store and retrieve events from PostgreSQL.

Create `src/event_store.py`:

```python
import psycopg2
import json
from typing import List, Optional
from datetime import datetime
from events import Event


class EventStore:
    """
    Event Store: manages event persistence.
    
    Responsibilities:
    - Append events to database
    - Load events by aggregate
    - Ensure version consistency
    """
    
    def __init__(self, connection_params: dict):
        """
        Initialize Event Store with database connection.
        
        Args:
            connection_params: dict with host, port, database, 
                               user, password
        """
        self.conn_params = connection_params
        self.conn = None
    
    def connect(self):
        """Open database connection."""
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**self.conn_params)
    
    def close(self):
        """Close database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()
    
    def append(self, event: Event) -> bool:
        """
        Append event to Event Store.
        
        This is the ONLY way to add events.
        Uses UNIQUE constraint to prevent duplicate versions.
        
        Args:
            event: Event to store
        
        Returns:
            True if successful
        
        Raises:
            psycopg2.IntegrityError: if version conflict
        """
        self.connect()
        cursor = self.conn.cursor()
        
        try:
            # Insert event
            cursor.execute("""
                INSERT INTO events 
                (event_id, aggregate_type, aggregate_id, 
                 event_type, version, data, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                event.event_id,
                event.aggregate_type,
                event.aggregate_id,
                event.event_type,
                event.version,
                json.dumps(event.data),  # Convert dict to JSON
                event.timestamp
            ))
            
            # Commit transaction
            self.conn.commit()
            cursor.close()
            return True
            
        except psycopg2.IntegrityError as e:
            # Version conflict: someone else modified aggregate
            self.conn.rollback()
            cursor.close()
            raise Exception(
                f"Version conflict for {event.aggregate_id} "
                f"version {event.version}"
            ) from e
    
    def load_events(self, aggregate_type: str, 
                    aggregate_id: str) -> List[Event]:
        """
        Load all events for an aggregate.
        
        Events are returned in version order (oldest first).
        This is used to rebuild aggregate state.
        
        Args:
            aggregate_type: e.g., "Order"
            aggregate_id: e.g., "123"
        
        Returns:
            List of events, ordered by version
        """
        self.connect()
        cursor = self.conn.cursor()
        
        # Query events
        cursor.execute("""
            SELECT event_id, aggregate_type, aggregate_id,
                   event_type, version, data, timestamp
            FROM events
            WHERE aggregate_type = %s AND aggregate_id = %s
            ORDER BY version ASC
        """, (aggregate_type, aggregate_id))
        
        # Build Event objects from rows
        events = []
        for row in cursor.fetchall():
            event = Event(
                event_id=row[0],
                aggregate_type=row[1],
                aggregate_id=row[2],
                event_type=row[3],
                version=row[4],
                data=json.loads(row[5]),  # Parse JSON to dict
                timestamp=row[6]
            )
            events.append(event)
        
        cursor.close()
        return events
    
    def get_latest_version(self, aggregate_type: str, 
                           aggregate_id: str) -> int:
        """
        Get the latest version number for an aggregate.
        
        Returns:
            Latest version, or 0 if aggregate doesn't exist
        """
        self.connect()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT MAX(version)
            FROM events
            WHERE aggregate_type = %s AND aggregate_id = %s
        """, (aggregate_type, aggregate_id))
        
        result = cursor.fetchone()[0]
        cursor.close()
        
        return result if result is not None else 0
    
    def event_exists(self, aggregate_type: str, 
                     aggregate_id: str) -> bool:
        """
        Check if aggregate has any events.
        
        Returns:
            True if aggregate exists
        """
        return self.get_latest_version(
            aggregate_type, aggregate_id
        ) > 0
```

**Key Concepts in event_store.py:**

```
┌─────────────────────┬────────────────────────────────┐
│ Method              │ Purpose                        │
├─────────────────────┼────────────────────────────────┤
│ append()            │ Add event to store             │
│ load_events()       │ Get all events for aggregate   │
│ get_latest_version()│ Check current version          │
│ event_exists()      │ Check if aggregate exists      │
├─────────────────────┼────────────────────────────────┤
│ json.dumps()        │ Convert Python dict → JSON     │
│ json.loads()        │ Convert JSON → Python dict     │
│ cursor.execute()    │ Run SQL query                  │
│ conn.commit()       │ Save changes to database       │
│ conn.rollback()     │ Undo changes on error          │
└─────────────────────┴────────────────────────────────┘
```

## File 3: order.py - Order Aggregate

**Purpose**: Order entity that rebuilds state from events.

Create `src/order.py`:

```python
from typing import List, Dict, Optional
from events import Event
from event_store import EventStore


class Order:
    """
    Order aggregate: entity built from events.
    
    State is reconstructed by replaying events.
    All changes produce new events.
    """
    
    def __init__(self, order_id: str):
        """
        Initialize empty order.
        
        Args:
            order_id: unique order identifier
        """
        self.order_id = order_id
        self.customer_id: Optional[str] = None
        self.items: Dict[str, dict] = {}  # item_id -> details
        self.status = "not_created"
        self.version = 0
    
    @classmethod
    def load_from_events(cls, order_id: str, 
                        event_store: EventStore) -> 'Order':
        """
        Load order by replaying events.
        
        This is how you get current state:
        1. Load all events from Event Store
        2. Apply each event to rebuild state
        3. Return hydrated order
        
        Args:
            order_id: which order to load
            event_store: where to get events
        
        Returns:
            Order with current state
        """
        # Create empty order
        order = cls(order_id)
        
        # Load all events
        events = event_store.load_events("Order", order_id)
        
        # Apply each event
        for event in events:
            order._apply_event(event)
        
        return order
    
    def _apply_event(self, event: Event):
        """
        Apply event to change order state.
        
        This is the ONLY way to change state.
        Each event type has its own logic.
        
        Args:
            event: event to apply
        """
        if event.event_type == "OrderCreated":
            self.customer_id = event.data["customer_id"]
            self.status = event.data["status"]
            self.version = event.version
        
        elif event.event_type == "ItemAdded":
            item_id = event.data["item_id"]
            self.items[item_id] = {
                "quantity": event.data["quantity"],
                "price": event.data["price"]
            }
            self.version = event.version
        
        elif event.event_type == "ItemRemoved":
            item_id = event.data["item_id"]
            if item_id in self.items:
                del self.items[item_id]
            self.version = event.version
        
        elif event.event_type == "OrderPaid":
            self.status = event.data["status"]
            self.version = event.version
        
        elif event.event_type == "OrderCancelled":
            self.status = event.data["status"]
            self.version = event.version
    
    def total(self) -> float:
        """
        Calculate order total from items.
        
        Returns:
            Total price
        """
        return sum(
            item["quantity"] * item["price"] 
            for item in self.items.values()
        )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"Order(id={self.order_id}, "
            f"customer={self.customer_id}, "
            f"items={len(self.items)}, "
            f"total=${self.total():.2f}, "
            f"status={self.status}, "
            f"version={self.version})"
        )
```

**Key Concepts in order.py:**

```
┌──────────────────────┬──────────────────────────────┐
│ Method               │ Purpose                      │
├──────────────────────┼──────────────────────────────┤
│ __init__()           │ Create empty order           │
│ load_from_events()   │ Rebuild order from events    │
│ _apply_event()       │ Apply single event to state  │
│ total()              │ Calculate from current state │
├──────────────────────┼──────────────────────────────┤
│ @classmethod         │ Decorator for factory method │
│ cls()                │ Reference to class itself    │
│ self                 │ Reference to instance        │
└──────────────────────┴──────────────────────────────┘
```

## File 4: main.py - Usage Examples

**Purpose**: Demonstrate how to use Event Store.

Create `src/main.py`:

```python
from event_store import EventStore
from order import Order
import events


# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'eventstore',
    'user': 'eventstore',
    'password': 'eventstore123'
}


def example_1_create_order():
    """Example: Create a new order."""
    print("\n=== Example 1: Create Order ===")
    
    # Initialize Event Store
    store = EventStore(DB_CONFIG)
    
    # Create OrderCreated event
    event = events.order_created(
        order_id="order-001",
        customer_id="customer-123",
        version=1
    )
    
    # Append to Event Store
    store.append(event)
    print(f"✓ Created order: {event.aggregate_id}")
    
    # Load order from events
    order = Order.load_from_events("order-001", store)
    print(f"✓ Loaded: {order}")
    
    store.close()


def example_2_add_items():
    """Example: Add items to existing order."""
    print("\n=== Example 2: Add Items ===")
    
    store = EventStore(DB_CONFIG)
    
    # Add first item
    event1 = events.item_added(
        order_id="order-001",
        item_id="apple",
        quantity=3,
        price=1.50,
        version=2  # Increment from last version
    )
    store.append(event1)
    print(f"✓ Added item: apple")
    
    # Add second item
    event2 = events.item_added(
        order_id="order-001",
        item_id="banana",
        quantity=2,
        price=0.75,
        version=3
    )
    store.append(event2)
    print(f"✓ Added item: banana")
    
    # Load order (rebuilds from all 3 events)
    order = Order.load_from_events("order-001", store)
    print(f"✓ Loaded: {order}")
    
    store.close()


def example_3_pay_order():
    """Example: Pay for order."""
    print("\n=== Example 3: Pay Order ===")
    
    store = EventStore(DB_CONFIG)
    
    # Create payment event
    event = events.order_paid(
        order_id="order-001",
        payment_method="credit_card",
        version=4
    )
    store.append(event)
    print(f"✓ Order paid")
    
    # Load final state
    order = Order.load_from_events("order-001", store)
    print(f"✓ Final state: {order}")
    
    store.close()


def example_4_view_history():
    """Example: View complete event history."""
    print("\n=== Example 4: View History ===")
    
    store = EventStore(DB_CONFIG)
    
    # Load all events
    events_list = store.load_events("Order", "order-001")
    
    print(f"\nEvent History for order-001:")
    print(f"{'Version':<10} {'Event Type':<20} {'Data'}")
    print("-" * 70)
    
    for event in events_list:
        print(
            f"{event.version:<10} "
            f"{event.event_type:<20} "
            f"{event.data}"
        )
    
    store.close()


if __name__ == "__main__":
    """
    Run all examples in sequence.
    
    Note: Run once, then comment out examples 1-3
    to avoid duplicate version errors.
    """
    example_1_create_order()
    example_2_add_items()
    example_3_pay_order()
    example_4_view_history()
```

**Run the examples:**

```bash
# From project root
python src/main.py
```

Expected output:
```
=== Example 1: Create Order ===
✓ Created order: order-001
✓ Loaded: Order(id=order-001, customer=customer-123, 
           items=0, total=$0.00, status=created, version=1)

=== Example 2: Add Items ===
✓ Added item: apple
✓ Added item: banana
✓ Loaded: Order(id=order-001, customer=customer-123, 
           items=2, total=$6.00, status=created, version=3)

=== Example 3: Pay Order ===
✓ Order paid
✓ Final state: Order(id=order-001, customer=customer-123, 
                items=2, total=$6.00, status=paid, version=4)

=== Example 4: View History ===
Event History for order-001:
Version    Event Type           Data
----------------------------------------------------------------------
1          OrderCreated         {'customer_id': 'customer-123', ...}
2          ItemAdded            {'item_id': 'apple', ...}
3          ItemAdded            {'item_id': 'banana', ...}
4          OrderPaid            {'payment_method': 'credit_card', ...}
```

## Summary

You now have a complete Event Store implementation:

```
┌─────────────────┬──────────────────────────────────┐
│ File            │ Responsibility                   │
├─────────────────┼──────────────────────────────────┤
│ events.py       │ Define event types               │
│ event_store.py  │ Store/load events                │
│ order.py        │ Rebuild state from events        │
│ main.py         │ Usage examples                   │
└─────────────────┴──────────────────────────────────┘
```

Next: Complete exercises in 04-exercises.md