"""
Order aggregate implementation.

Demonstrates how to rebuild entity state from events.
"""

from typing import List, Dict, Optional
from events import Event
from event_store import EventStore


class Order:
    """
    Order aggregate: entity built from events.

    State is reconstructed by replaying events.
    All changes produce new events.

    Attributes:
        order_id: Unique order identifier
        customer_id: Customer who owns this order
        items: Dictionary of items (item_id -> details)
        status: Current order status
        version: Latest event version
    """

    def __init__(self, order_id: str):
        """
        Initialize empty order.

        Args:
            order_id: Unique order identifier
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

        This is the standard way to get current state:
        1. Load all events from Event Store
        2. Apply each event in sequence
        3. Return hydrated order with current state

        Args:
            order_id: Which order to load
            event_store: Where to get events

        Returns:
            Order with current state

        Example:
            store = EventStore(DB_CONFIG)
            order = Order.load_from_events("order-123", store)
            print(order.total())
        """
        # Create empty order
        order = cls(order_id)

        # Load all events for this order
        events = event_store.load_events("Order", order_id)

        # Apply each event to rebuild state
        for event in events:
            order._apply_event(event)

        return order

    def _apply_event(self, event: Event):
        """
        Apply event to change order state.

        This is the ONLY way to change state.
        Each event type has its own logic.
        This method is called when replaying events.

        Args:
            event: Event to apply

        Note:
            Private method (starts with _)
            Only called internally during event replay
        """
        if event.event_type == "OrderCreated":
            # Initialize order
            self.customer_id = event.data["customer_id"]
            self.status = event.data["status"]
            self.version = event.version

        elif event.event_type == "ItemAdded":
            # Add item to order
            item_id = event.data["item_id"]
            self.items[item_id] = {
                "quantity": event.data["quantity"],
                "price": event.data["price"]
            }
            self.version = event.version

        elif event.event_type == "ItemRemoved":
            # Remove item from order
            item_id = event.data["item_id"]
            if item_id in self.items:
                del self.items[item_id]
            self.version = event.version

        elif event.event_type == "OrderPaid":
            # Mark order as paid
            self.status = event.data["status"]
            self.version = event.version

        elif event.event_type == "OrderCancelled":
            # Mark order as cancelled
            self.status = event.data["status"]
            self.version = event.version

    def total(self) -> float:
        """
        Calculate order total from current items.

        Returns:
            Total price of all items

        Example:
            order = Order.load_from_events("order-123", store)
            print(f"Total: ${order.total():.2f}")
        """
        return sum(
            item["quantity"] * item["price"]
            for item in self.items.values()
        )

    def item_count(self) -> int:
        """
        Get total number of items in order.

        Returns:
            Total quantity of all items
        """
        return sum(
            item["quantity"]
            for item in self.items.values()
        )

    def has_item(self, item_id: str) -> bool:
        """
        Check if order contains specific item.

        Args:
            item_id: Item to check

        Returns:
            True if item is in order
        """
        return item_id in self.items

    def get_item(self, item_id: str) -> Optional[dict]:
        """
        Get details for specific item.

        Args:
            item_id: Item to retrieve

        Returns:
            Item details or None if not found
        """
        return self.items.get(item_id)

    def is_paid(self) -> bool:
        """Check if order is paid."""
        return self.status == "paid"

    def is_cancelled(self) -> bool:
        """Check if order is cancelled."""
        return self.status == "cancelled"

    def is_created(self) -> bool:
        """Check if order is created but not paid."""
        return self.status == "created"

    def __repr__(self) -> str:
        """
        String representation for debugging.

        Returns:
            Human-readable order summary
        """
        return (
            f"Order("
            f"id={self.order_id}, "
            f"customer={self.customer_id}, "
            f"items={len(self.items)}, "
            f"total=${self.total():.2f}, "
            f"status={self.status}, "
            f"version={self.version}"
            f")"
        )

    def to_dict(self) -> dict:
        """
        Convert order to dictionary.

        Returns:
            Dictionary representation of order
        """
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "items": self.items,
            "total": self.total(),
            "status": self.status,
            "version": self.version
        }