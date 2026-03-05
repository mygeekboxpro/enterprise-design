"""
worker-server/activities.py

PURPOSE:
  Implements all Temporal Activities for the
  Order Processing domain.

  This file lives ONLY on the Worker server.
  The Client server never imports this file.

IMPORT RULE:
  - Data classes come from shared.models
  - No imports from client-server code
  - No imports from workflows.py (avoid circular deps)
"""

import asyncio
from temporalio import activity
from order_shared.models import (
    OrderInput,
    ValidationResult,
    PaymentResult,
)


# ─────────────────────────────────────────────────
# ACTIVITY 1: validate_order
# ─────────────────────────────────────────────────

@activity.defn
async def validate_order(
    order: OrderInput,
) -> ValidationResult:
    """
    Validate order input.

    ValueError  → non-retryable (logic error)
    RuntimeError → retryable   (transient error)
    """
    info = activity.info()
    activity.logger.info(
        f"[{info.workflow_id}] Validating order "
        f"{order.order_id} attempt={info.attempt}"
    )

    if not order.order_id:
        raise ValueError("order_id cannot be empty")

    if not order.customer_id:
        raise ValueError("customer_id cannot be empty")

    if order.amount <= 0:
        raise ValueError(
            f"amount must be > 0, got {order.amount}"
        )

    if order.order_id == "simulate-unavailable":
        raise RuntimeError("Fraud service unavailable")

    return ValidationResult(valid=True)


# ─────────────────────────────────────────────────
# ACTIVITY 2: charge_payment
# ─────────────────────────────────────────────────

@activity.defn
async def charge_payment(
    order: OrderInput,
) -> PaymentResult:
    """
    Charge the customer.

    Idempotent: order_id is the idempotency key.
    Retrying with the same order_id will not
    double-charge the customer.
    """
    info = activity.info()
    activity.logger.info(
        f"[{info.workflow_id}] Charging "
        f"${order.amount} for {order.order_id} "
        f"attempt={info.attempt}"
    )

    await asyncio.sleep(0.5)

    # Simulate transient failure for learning purposes
    if order.order_id == "simulate-payment-fail":
        if info.attempt < 3:
            raise RuntimeError(
                "Payment gateway timeout "
                f"(attempt {info.attempt})"
            )

    # Deterministic transaction ID using order_id
    # ensures idempotency across retries
    txn_id = f"txn-{order.order_id}-{order.customer_id}"

    return PaymentResult(
        charged=True,
        transaction_id=txn_id,
        amount=order.amount,
    )


# ─────────────────────────────────────────────────
# ACTIVITY 3: confirm_order
# ─────────────────────────────────────────────────

@activity.defn
async def confirm_order(
    order_id: str,
    transaction_id: str,
) -> str:
    """
    Mark the order as confirmed in the system.
    Returns a human-readable confirmation string.
    """
    activity.logger.info(
        f"Confirming order {order_id} "
        f"txn={transaction_id}"
    )
    await asyncio.sleep(0.1)
    return (
        f"Order {order_id} confirmed. "
        f"Transaction: {transaction_id}"
    )


# ─────────────────────────────────────────────────
# ACTIVITY 4: record_event
# ─────────────────────────────────────────────────

@activity.defn
async def record_event(
    event_type: str,
    order_id: str,
    data: dict,
) -> str:
    """
    Write an event to the event log.
    Idempotent: event_type + order_id = event_id.
    """
    activity.logger.info(
        f"Recording {event_type} for {order_id}"
    )
    await asyncio.sleep(0.1)
    return f"{event_type}:{order_id}"


# ─────────────────────────────────────────────────
# ACTIVITY 5: send_notification
# ─────────────────────────────────────────────────

@activity.defn
async def send_notification(
    customer_id: str,
    message: str,
) -> bool:
    """
    Send a notification to the customer.
    Non-critical: failure here should not fail the
    entire workflow — handled via retry policy in
    the Workflow.
    """
    activity.logger.info(
        f"Notifying {customer_id}: {message}"
    )
    await asyncio.sleep(0.2)
    return True
