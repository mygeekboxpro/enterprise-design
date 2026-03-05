"""
worker-server/workflows.py

PURPOSE:
  Full implementation of OrderWorkflow.
  Extends the interface defined in shared/workflow_iface.py.

  This file lives ONLY on the Worker server.
  The Client server uses only shared/workflow_iface.py.

ENTERPRISE PATTERN:
  The shared interface declares the "what".
  This file implements the "how".
  Client only needs the "what".
"""

from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

# Import the shared interface — this makes the
# worker's class register under the same Workflow
# type name as the client expects.
from order_shared.workflow_iface import OrderWorkflow
from order_shared.models import OrderInput, WorkflowStatus

# Activities imported inside sandbox guard.
# This prevents accidental direct I/O in the Workflow.
with workflow.unsafe.imports_passed_through():
    from activities import (
        validate_order,
        charge_payment,
        confirm_order,
        record_event,
        send_notification,
    )


# Re-declare @workflow.defn on the same class.
# This registers the implementation under the same
# workflow type name ("OrderWorkflow") that the
# client uses to start it.
@workflow.defn
class OrderWorkflow(OrderWorkflow):  # type: ignore[no-redef]
    """
    Full OrderWorkflow implementation.
    Only runs on the Worker server.
    """

    def __init__(self) -> None:
        self._status: str = "started"
        self._approved: bool = False
        self._cancelled: bool = False
        self._order_id: str = ""

    # ── Signals ───────────────────────────────────

    @workflow.signal
    async def approve(self) -> None:
        workflow.logger.info(
            f"[{self._order_id}] Received: approve"
        )
        self._approved = True

    @workflow.signal
    async def cancel(self) -> None:
        workflow.logger.info(
            f"[{self._order_id}] Received: cancel"
        )
        self._cancelled = True

    # ── Queries ───────────────────────────────────

    @workflow.query
    def get_status(self) -> WorkflowStatus:
        return WorkflowStatus(
            status=self._status,
            approved=self._approved,
            cancelled=self._cancelled,
            order_id=self._order_id,
        )

    # ── Entry Point ───────────────────────────────

    @workflow.run
    async def run(self, order: OrderInput) -> str:
        self._order_id = order.order_id
        workflow.logger.info(
            f"Starting workflow for {order.order_id}"
        )

        # ── STEP 1: Validate ──────────────────────
        self._status = "validating"
        await workflow.execute_activity(
            validate_order,
            order,
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                backoff_coefficient=2.0,
                non_retryable_error_types=["ValueError"],
            ),
        )

        # ── STEP 2: Record received event ─────────
        self._status = "recording_received"
        await workflow.execute_activity(
            record_event,
            args=[
                "OrderReceived",
                order.order_id,
                {
                    "customer_id": order.customer_id,
                    "amount": order.amount,
                },
            ],
            start_to_close_timeout=timedelta(seconds=5),
        )

        # ── STEP 3: Wait for approval signal ──────
        self._status = "waiting_approval"
        workflow.logger.info(
            f"[{order.order_id}] Waiting for approval..."
        )
        await workflow.wait_condition(
            lambda: self._approved or self._cancelled,
            timeout=timedelta(minutes=5),
        )

        if self._cancelled:
            self._status = "cancelled"
            await workflow.execute_activity(
                record_event,
                args=[
                    "OrderCancelled",
                    order.order_id,
                    {"reason": "cancelled via signal"},
                ],
                start_to_close_timeout=timedelta(seconds=5),
            )
            return f"Order {order.order_id} was cancelled"

        if not self._approved:
            self._status = "timed_out"
            return f"Order {order.order_id} timed out"

        # ── STEP 4: Charge payment ─────────────────
        self._status = "charging"
        payment = await workflow.execute_activity(
            charge_payment,
            order,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                maximum_attempts=5,
                initial_interval=timedelta(seconds=1),
                backoff_coefficient=2.0,
                maximum_interval=timedelta(seconds=30),
            ),
        )

        # ── STEP 5: Confirm order ──────────────────
        self._status = "confirming"
        confirmation = await workflow.execute_activity(
            confirm_order,
            args=[order.order_id, payment.transaction_id],
            start_to_close_timeout=timedelta(seconds=10),
        )

        # ── STEP 6: Record completion event ───────
        self._status = "recording_completed"
        await workflow.execute_activity(
            record_event,
            args=[
                "OrderCompleted",
                order.order_id,
                {
                    "transaction_id": payment.transaction_id,
                    "amount": payment.amount,
                },
            ],
            start_to_close_timeout=timedelta(seconds=5),
        )

        # ── STEP 7: Send notification ──────────────
        self._status = "notifying"
        await workflow.execute_activity(
            send_notification,
            args=[
                order.customer_id,
                f"Order {order.order_id} confirmed!",
            ],
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        self._status = "completed"
        return (
            f"Order {order.order_id} completed: "
            f"{confirmation}"
        )