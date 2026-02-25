"""
Event definitions for Event Store.

This module defines:
- Base Event class
- Helper functions to create domain events
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
import uuid


@dataclass
class Event:
    """
    Base class for all events.

    Attributes:
        event_id: Unique identifier (UUID)
        aggregate_type: Type of entity (e.g., "Order")
        aggregate_id: Specific entity ID (e.g., "order-123")
        event_type: What happened (e.g., "OrderCreated")
        version: Sequence number for this aggregate
        data: Event payload (dictionary)
        timestamp: When event occurred (UTC)
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

        Args:
            aggregate_type: Entity type
            aggregate_id: Entity ID
            event_type: Event name
            version: Event sequence number
            data: Event payload

        Returns:
            New Event instance

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


# Domain Event Helpers
# ---------------------

def order_created(order_id: str, customer_id: str,
                  version: int = 1) -> Event:
    """
    Create OrderCreated event.

    Args:
        order_id: Unique order identifier
        customer_id: Customer who created order
        version: Event version (default: 1)

    Returns:
        OrderCreated event
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

    Args:
        order_id: Which order
        item_id: Which item
        quantity: How many
        price: Price per item
        version: Event version

    Returns:
        ItemAdded event
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

    Args:
        order_id: Which order
        item_id: Which item to remove
        version: Event version

    Returns:
        ItemRemoved event
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

    Args:
        order_id: Which order
        payment_method: How paid (e.g., 'credit_card')
        version: Event version

    Returns:
        OrderPaid event
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

    Args:
        order_id: Which order
        reason: Why cancelled
        version: Event version

    Returns:
        OrderCancelled event
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