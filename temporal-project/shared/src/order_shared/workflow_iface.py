"""
shared/workflow_iface.py

PURPOSE:
  Defines the Workflow interface shared between
  the Client server and the Worker server.

  Client server uses this to:
    - Start the workflow by class reference
    - Send signals by method reference
    - Send queries by method reference

  Worker server uses this to:
    - Implement the workflow (inherits nothing,
      but registers under the same class name)

ENTERPRISE PATTERN:
  The client never needs the Activity implementations.
  It only needs to know:
    1. The Workflow class name (for routing)
    2. The signal method names
    3. The query method names
    4. The input/output types (from models.py)

  This file provides exactly that — the "API contract"
  without pulling in any worker-side dependencies.

IMPORTANT:
  The @workflow.defn decorated class here is the
  SAME class imported by both client and worker.
  Temporal uses the class name as the workflow type
  identifier on the server.
"""

from temporalio import workflow
from order_shared.models import OrderInput, WorkflowStatus

# Task Queue name — must match on Worker and Client
# Single source of truth: defined here, imported by both
TASK_QUEUE = "order-task-queue"


@workflow.defn
class OrderWorkflow:
    """
    Workflow interface for OrderWorkflow.

    This class is:
      - Imported by client-server to start/signal/query
      - Imported by worker-server as the base for the
        full implementation (worker overrides run())

    Signal and Query decorators are defined here so
    the client can reference them without importing
    worker-side code.
    """

    @workflow.run
    async def run(self, order: OrderInput) -> str:
        """Entry point. Implemented in worker-server."""
        raise NotImplementedError

    @workflow.signal
    async def approve(self) -> None:
        """Signal: approve this order."""
        raise NotImplementedError

    @workflow.signal
    async def cancel(self) -> None:
        """Signal: cancel this order."""
        raise NotImplementedError

    @workflow.query
    def get_status(self) -> WorkflowStatus:
        """Query: return current workflow status."""
        raise NotImplementedError