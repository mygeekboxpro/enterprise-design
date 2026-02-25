"""
Unit tests for Order aggregate.

Run with: pytest tests/test_order.py -v
"""

import pytest
from datetime import datetime
from events import Event, order_created, item_added, order_paid
from order import Order


class TestOrder:
    """Test suite for Order aggregate."""

    def test_empty_order(self):
        """Test creating empty order."""
        order = Order("order-test-1")

        assert order.order_id == "order-test-1"
        assert order.customer_id is None
        assert order.status == "not_created"
        assert order.version == 0
        assert len(order.items) == 0
        assert order.total() == 0.0

    def test_apply_order_created(self):
        """Test applying OrderCreated event."""
        order = Order("order-test-2")

        event = order_created(
            order_id="order-test-2",
            customer_id="customer-123",
            version=1
        )

        order._apply_event(event)

        assert order.customer_id == "customer-123"
        assert order.status == "created"
        assert order.version == 1

    def test_apply_item_added(self):
        """Test applying ItemAdded event."""
        order = Order("order-test-3")

        # First create order
        event1 = order_created(
            order_id="order-test-3",
            customer_id="customer-123",
            version=1
        )
        order._apply_event(event1)

        # Then add item
        event2 = item_added(
            order_id="order-test-3",
            item_id="apple",
            quantity=3,
            price=1.50,
            version=2
        )
        order._apply_event(event2)

        assert len(order.items) == 1
        assert "apple" in order.items
        assert order.items["apple"]["quantity"] == 3
        assert order.items["apple"]["price"] == 1.50
        assert order.version == 2

    def test_calculate_total(self):
        """Test total calculation."""
        order = Order("order-test-4")

        # Create order
        event1 = order_created(
            order_id="order-test-4",
            customer_id="customer-123",
            version=1
        )
        order._apply_event(event1)

        # Add first item: 3 × $1.50 = $4.50
        event2 = item_added(
            order_id="order-test-4",
            item_id="apple",
            quantity=3,
            price=1.50,
            version=2
        )
        order._apply_event(event2)

        # Add second item: 2 × $2.00 = $4.00
        event3 = item_added(
            order_id="order-test-4",
            item_id="banana",
            quantity=2,
            price=2.00,
            version=3
        )
        order._apply_event(event3)

        # Total should be $8.50
        assert order.total() == 8.50

    def test_order_paid(self):
        """Test order payment."""
        order = Order("order-test-5")

        # Create order
        event1 = order_created(
            order_id="order-test-5",
            customer_id="customer-123",
            version=1
        )
        order._apply_event(event1)

        # Pay for order
        event2 = order_paid(
            order_id="order-test-5",
            payment_method="credit_card",
            version=2
        )
        order._apply_event(event2)

        assert order.status == "paid"
        assert order.is_paid() is True
        assert order.is_created() is False
        assert order.version == 2

    def test_has_item(self):
        """Test checking if order has item."""
        order = Order("order-test-6")

        # Create order and add item
        event1 = order_created(
            order_id="order-test-6",
            customer_id="customer-123",
            version=1
        )
        order._apply_event(event1)

        event2 = item_added(
            order_id="order-test-6",
            item_id="apple",
            quantity=3,
            price=1.50,
            version=2
        )
        order._apply_event(event2)

        assert order.has_item("apple") is True
        assert order.has_item("banana") is False

    def test_get_item(self):
        """Test retrieving item details."""
        order = Order("order-test-7")

        # Create order and add item
        event1 = order_created(
            order_id="order-test-7",
            customer_id="customer-123",
            version=1
        )
        order._apply_event(event1)

        event2 = item_added(
            order_id="order-test-7",
            item_id="apple",
            quantity=3,
            price=1.50,
            version=2
        )
        order._apply_event(event2)

        item = order.get_item("apple")
        assert item is not None
        assert item["quantity"] == 3
        assert item["price"] == 1.50

        missing_item = order.get_item("banana")
        assert missing_item is None

    def test_item_count(self):
        """Test counting total items."""
        order = Order("order-test-8")

        # Create order
        event1 = order_created(
            order_id="order-test-8",
            customer_id="customer-123",
            version=1
        )
        order._apply_event(event1)

        # Add items
        event2 = item_added(
            order_id="order-test-8",
            item_id="apple",
            quantity=3,
            price=1.50,
            version=2
        )
        order._apply_event(event2)

        event3 = item_added(
            order_id="order-test-8",
            item_id="banana",
            quantity=2,
            price=2.00,
            version=3
        )
        order._apply_event(event3)

        # Total quantity: 3 + 2 = 5
        assert order.item_count() == 5

    def test_to_dict(self):
        """Test converting order to dictionary."""
        order = Order("order-test-9")

        # Create order and add item
        event1 = order_created(
            order_id="order-test-9",
            customer_id="customer-123",
            version=1
        )
        order._apply_event(event1)

        event2 = item_added(
            order_id="order-test-9",
            item_id="apple",
            quantity=3,
            price=1.50,
            version=2
        )
        order._apply_event(event2)

        order_dict = order.to_dict()

        assert order_dict["order_id"] == "order-test-9"
        assert order_dict["customer_id"] == "customer-123"
        assert order_dict["status"] == "created"
        assert order_dict["version"] == 2
        assert order_dict["total"] == 4.50
        assert "apple" in order_dict["items"]

    def test_repr(self):
        """Test string representation."""
        order = Order("order-test-10")

        # Create order
        event = order_created(
            order_id="order-test-10",
            customer_id="customer-123",
            version=1
        )
        order._apply_event(event)

        repr_str = repr(order)

        assert "order-test-10" in repr_str
        assert "customer-123" in repr_str
        assert "created" in repr_str
        assert "version=1" in repr_str


if __name__ == "__main__":
    """Run tests with pytest."""
    pytest.main([__file__, "-v"])