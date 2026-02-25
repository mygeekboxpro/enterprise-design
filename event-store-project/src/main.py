"""
Usage examples for Event Store.

Demonstrates complete order workflow using Event Sourcing.
"""

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
    """
    Example 1: Create a new order.

    Demonstrates:
    - Creating an event
    - Appending to Event Store
    - Loading order from events
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Create Order")
    print("=" * 60)

    # Initialize Event Store
    store = EventStore(DB_CONFIG)

    # Create OrderCreated event
    event = events.order_created(
        order_id="order-001",
        customer_id="customer-123",
        version=1
    )

    # Append event to Event Store
    store.append(event)
    print(f"✓ Created order: {event.aggregate_id}")
    print(f"  Event ID: {event.event_id}")
    print(f"  Timestamp: {event.timestamp}")

    # Load order from events
    order = Order.load_from_events("order-001", store)
    print(f"\n✓ Loaded order from events:")
    print(f"  {order}")

    store.close()


def example_2_add_items():
    """
    Example 2: Add items to existing order.

    Demonstrates:
    - Getting latest version
    - Adding multiple events
    - State rebuilding from events
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Add Items to Order")
    print("=" * 60)

    store = EventStore(DB_CONFIG)

    # Get current version
    current_version = store.get_latest_version("Order", "order-001")
    print(f"Current version: {current_version}")

    # Add first item
    event1 = events.item_added(
        order_id="order-001",
        item_id="apple",
        quantity=3,
        price=1.50,
        version=current_version + 1
    )
    store.append(event1)
    print(f"\n✓ Added item: apple (3 × $1.50)")

    # Add second item
    event2 = events.item_added(
        order_id="order-001",
        item_id="banana",
        quantity=2,
        price=0.75,
        version=current_version + 2
    )
    store.append(event2)
    print(f"✓ Added item: banana (2 × $0.75)")

    # Load order (rebuilds from all events)
    order = Order.load_from_events("order-001", store)
    print(f"\n✓ Order updated:")
    print(f"  Items: {list(order.items.keys())}")
    print(f"  Total: ${order.total():.2f}")
    print(f"  Version: {order.version}")

    store.close()


def example_3_pay_order():
    """
    Example 3: Pay for order.

    Demonstrates:
    - State transitions via events
    - Final order state
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Pay for Order")
    print("=" * 60)

    store = EventStore(DB_CONFIG)

    # Get current version
    current_version = store.get_latest_version("Order", "order-001")

    # Create payment event
    event = events.order_paid(
        order_id="order-001",
        payment_method="credit_card",
        version=current_version + 1
    )
    store.append(event)
    print(f"✓ Payment processed via credit_card")

    # Load final state
    order = Order.load_from_events("order-001", store)
    print(f"\n✓ Final order state:")
    print(f"  {order}")
    print(f"\n  Status: {order.status}")
    print(f"  Is paid: {order.is_paid()}")

    store.close()


def example_4_view_history():
    """
    Example 4: View complete event history.

    Demonstrates:
    - Loading all events
    - Event timeline
    - Event details
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: View Event History")
    print("=" * 60)

    store = EventStore(DB_CONFIG)

    # Load all events for order
    events_list = store.load_events("Order", "order-001")

    print(f"\nEvent History for order-001 ({len(events_list)} events):")
    print("-" * 70)
    print(f"{'Ver':<5} {'Event Type':<20} {'Timestamp':<25} {'Data'}")
    print("-" * 70)

    for event in events_list:
        timestamp_str = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        data_str = str(event.data)[:40]  # Truncate long data
        print(
            f"{event.version:<5} "
            f"{event.event_type:<20} "
            f"{timestamp_str:<25} "
            f"{data_str}"
        )

    store.close()


def example_5_multiple_orders():
    """
    Example 5: Create and manage multiple orders.

    Demonstrates:
    - Working with multiple aggregates
    - Listing all orders
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Multiple Orders")
    print("=" * 60)

    store = EventStore(DB_CONFIG)

    # Create multiple orders
    orders_data = [
        ("order-002", "customer-456"),
        ("order-003", "customer-789"),
    ]

    for order_id, customer_id in orders_data:
        # Skip if order already exists
        if store.event_exists("Order", order_id):
            print(f"⊘ Order {order_id} already exists, skipping")
            continue

        event = events.order_created(
            order_id=order_id,
            customer_id=customer_id,
            version=1
        )
        store.append(event)
        print(f"✓ Created {order_id} for {customer_id}")

    # List all orders
    all_order_ids = store.get_all_aggregate_ids("Order")
    print(f"\n✓ Total orders in system: {len(all_order_ids)}")

    for order_id in all_order_ids:
        order = Order.load_from_events(order_id, store)
        print(f"  - {order_id}: {order.status}, "
              f"version {order.version}")

    store.close()


def example_6_version_conflict():
    """
    Example 6: Demonstrate version conflict handling.

    Demonstrates:
    - Optimistic locking
    - Version conflict detection
    - Error handling
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Version Conflict Handling")
    print("=" * 60)

    store = EventStore(DB_CONFIG)

    # Try to add event with duplicate version
    print("\nAttempting to append event with duplicate version...")

    try:
        event = events.item_added(
            order_id="order-001",
            item_id="duplicate_item",
            quantity=1,
            price=1.00,
            version=2  # This version already exists
        )
        store.append(event)
        print("✗ Should not reach here!")

    except Exception as e:
        print(f"✓ Caught expected error:")
        print(f"  {str(e)}")
        print(f"\n✓ This is correct behavior - versions must be unique")

    # Show correct approach
    print(f"\nCorrect approach:")
    current_version = store.get_latest_version("Order", "order-001")
    print(f"  1. Get latest version: {current_version}")
    print(f"  2. Use next version: {current_version + 1}")

    store.close()


def run_all_examples():
    """
    Run all examples in sequence.

    Note: Comment out examples 1-3 after first run
    to avoid duplicate version errors.
    """
    print("\n" + "=" * 60)
    print("EVENT STORE EXAMPLES")
    print("=" * 60)

    # First run: uncomment these
    example_1_create_order()
    example_2_add_items()
    example_3_pay_order()

    # Always safe to run
    example_4_view_history()
    example_5_multiple_orders()
    example_6_version_conflict()

    print("\n" + "=" * 60)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    """
    Main entry point.

    Run with: python main.py
    """
    run_all_examples()