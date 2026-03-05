"""
client-server/starter.py

PURPOSE:
  Starts an OrderWorkflow execution from the Client server.

  This file:
    - Imports ONLY from shared/ (no worker-side code)
    - Reads TEMPORAL_HOST from environment
    - Connects to Temporal Server (remote)
    - Starts the workflow by referencing the shared
      workflow interface class

  The Client server has NO knowledge of:
    - activities.py (worker implementation detail)
    - workflows.py  (worker implementation detail)

USAGE:
  python starter.py                  # order-001
  python starter.py order-002        # custom ID
  python starter.py simulate-payment-fail  # retry demo

ENVIRONMENT VARIABLES (from .env):
  TEMPORAL_HOST      — host:port of Temporal Server
  TEMPORAL_NAMESPACE — Temporal namespace
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from temporalio.client import Client

# Only shared imports — no worker-side imports
from order_shared.workflow_iface import OrderWorkflow, TASK_QUEUE
from order_shared.models import OrderInput

load_dotenv()


async def main(order_id: str) -> None:
    temporal_host = os.environ.get(
        "TEMPORAL_HOST", "localhost:7233"
    )
    namespace = os.environ.get(
        "TEMPORAL_NAMESPACE", "default"
    )

    print(f"Connecting to Temporal at {temporal_host}")

    client = await Client.connect(
        temporal_host,
        namespace=namespace,
    )

    order = OrderInput(
        order_id=order_id,
        customer_id="customer-alice",
        amount=99.99,
    )

    print(f"Starting workflow: {order_id}")
    print(f"Check UI: http://localhost:8080")

    # start_workflow returns immediately.
    # The workflow is now queued on Temporal Server.
    # The Worker server will pick it up and execute it.
    handle = await client.start_workflow(
        OrderWorkflow.run,           # from shared/
        order,                       # from shared/models
        id=order_id,
        task_queue=TASK_QUEUE,       # from shared/
    )

    print(f"Workflow started. ID: {handle.id}")
    print()
    print("Workflow is WAITING FOR APPROVAL.")
    print("On the client server, run:")
    print(f"  python send_signal.py {order_id}")
    print()
    print("Waiting for result...")

    result = await handle.result()
    print(f"Result: {result}")


if __name__ == "__main__":
    oid = sys.argv[1] if len(sys.argv) > 1 else "order-001"
    asyncio.run(main(oid))