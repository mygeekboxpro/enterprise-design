"""
worker-server/tests/test_activities.py

Tests the Activity implementations directly.
No Temporal Server needed — Activities are plain
async functions.

Run:
  cd worker-server
  pytest tests/test_activities.py -v
"""

import pytest
from shared.models import OrderInput, ValidationResult, PaymentResult
from activities import (
    validate_order,
    charge_payment,
    confirm_order,
    record_event,
    send_notification,
)


def make_order(
    order_id: str = "order-test-001",
    customer_id: str = "customer-alice",
    amount: float = 99.99,
) -> OrderInput:
    return OrderInput(
        order_id=order_id,
        customer_id=customer_id,
        amount=amount,
    )


# ── validate_order ───────────────────────────────

@pytest.mark.asyncio
async def test_validate_success():
    result = await validate_order(make_order())
    assert isinstance(result, ValidationResult)
    assert result.valid is True


@pytest.mark.asyncio
async def test_validate_empty_order_id():
    with pytest.raises(ValueError, match="order_id"):
        await validate_order(make_order(order_id=""))


@pytest.mark.asyncio
async def test_validate_empty_customer_id():
    with pytest.raises(ValueError, match="customer_id"):
        await validate_order(make_order(customer_id=""))


@pytest.mark.asyncio
async def test_validate_zero_amount():
    with pytest.raises(ValueError, match="amount"):
        await validate_order(make_order(amount=0.0))


@pytest.mark.asyncio
async def test_validate_negative_amount():
    with pytest.raises(ValueError, match="amount"):
        await validate_order(make_order(amount=-10.0))


# ── charge_payment ───────────────────────────────

@pytest.mark.asyncio
async def test_charge_success():
    result = await charge_payment(make_order())
    assert isinstance(result, PaymentResult)
    assert result.charged is True
    assert result.amount == 99.99
    assert "txn-" in result.transaction_id


@pytest.mark.asyncio
async def test_charge_idempotent():
    """Same order_id → same transaction_id (idempotent)."""
    order = make_order()
    r1 = await charge_payment(order)
    r2 = await charge_payment(order)
    assert r1.transaction_id == r2.transaction_id


# ── confirm_order ────────────────────────────────

@pytest.mark.asyncio
async def test_confirm_success():
    result = await confirm_order("order-001", "txn-abc")
    assert "order-001" in result
    assert "txn-abc" in result


# ── record_event ─────────────────────────────────

@pytest.mark.asyncio
async def test_record_event_success():
    result = await record_event(
        "OrderReceived", "order-001", {"amount": 99.99}
    )
    assert "OrderReceived" in result
    assert "order-001" in result


@pytest.mark.asyncio
async def test_record_event_idempotent():
    r1 = await record_event(
        "OrderReceived", "order-001", {"amount": 99.99}
    )
    r2 = await record_event(
        "OrderReceived", "order-001", {"amount": 99.99}
    )
    assert r1 == r2


# ── send_notification ────────────────────────────

@pytest.mark.asyncio
async def test_send_notification_success():
    result = await send_notification(
        "customer-alice", "Your order is confirmed!"
    )
    assert result is True