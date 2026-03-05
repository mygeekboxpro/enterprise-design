"""
client-server/send_signal.py

PURPOSE:
  Send a Signal to a running workflow, then
  Query its current status.

  Runs on the Client server.
  Uses ONLY shared/ imports — no worker-side code.

  Signals and Queries both go through the Temporal
  Server. The Client never contacts the Worker directly.

USAGE:
  python send_signal.py order-001           # approve
  python send_signal.py order-001 cancel    # cancel
  python send_signal.py order-001 status    # query only

FLOW:
  Client ──signal/query──▶ Temporal Server
                                │
                           routes to Worker
                                │
                           Worker executes
                           signal/query handler
                                │
                           result returned
                           to Client
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from temporalio.client import Client

from order_shared.workflow_iface import OrderWorkflow

load_dotenv()


async def main(workflow_id: str, action: str) -> None:
    temporal_host = os.environ.get(
        "TEMPORAL_HOST", "localhost:7233"
    )
    namespace = os.environ.get(
        "TEMPORAL_NAMESPACE", "default"
    )

    client = await Client.connect(
        temporal_host,
        namespace=namespace,
    )

    # Get a handle to the running workflow by its ID.
    # This does NOT start a new workflow.
    handle = client.get_workflow_handle(workflow_id)

    if action == "cancel":
        print(f"Sending CANCEL signal to {workflow_id}")
        await handle.signal(OrderWorkflow.cancel)

    elif action == "status":
        # Query only — no signal sent
        pass

    else:
        # Default action: approve
        print(f"Sending APPROVE signal to {workflow_id}")
        await handle.signal(OrderWorkflow.approve)

    # Query current status after the action
    status = await handle.query(OrderWorkflow.get_status)

    print()
    print(f"Workflow ID : {workflow_id}")
    print(f"Status      : {status.status}")
    print(f"Approved    : {status.approved}")
    print(f"Cancelled   : {status.cancelled}")
    print()
    print("Check UI: http://localhost:8080")


if __name__ == "__main__":
    wf_id = sys.argv[1] if len(sys.argv) > 1 else "order-001"
    act = sys.argv[2] if len(sys.argv) > 2 else "approve"
    asyncio.run(main(wf_id, act))