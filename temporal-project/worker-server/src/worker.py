"""
worker-server/worker.py

PURPOSE:
  Starts the Temporal Worker process on the Worker server.

  This process:
    1. Reads TEMPORAL_HOST from environment
    2. Connects to the Temporal Server (remote)
    3. Registers all Workflows and Activities
    4. Polls the Task Queue and executes work

ENVIRONMENT VARIABLES (from .env):
  TEMPORAL_HOST       — host:port of Temporal Server
  TEMPORAL_NAMESPACE  — Temporal namespace (default)
  WORKER_IDENTITY     — label shown in Web UI

RUN:
  cd worker-server
  python worker.py
"""

import asyncio
import os

from dotenv import load_dotenv
from temporalio.client import Client
from temporalio.worker import Worker

from activities import (
    validate_order,
    charge_payment,
    confirm_order,
    record_event,
    send_notification,
)
from order_shared.workflow_iface import TASK_QUEUE
from workflows import OrderWorkflow

# Load .env file from the worker-server directory
load_dotenv()


async def main() -> None:
    temporal_host = os.environ.get(
        "TEMPORAL_HOST", "localhost:7233"
    )
    namespace = os.environ.get(
        "TEMPORAL_NAMESPACE", "default"
    )
    identity = os.environ.get(
        "WORKER_IDENTITY", "worker-server-1"
    )

    print(f"Connecting to Temporal at {temporal_host}")
    print(f"Namespace : {namespace}")
    print(f"Task queue: {TASK_QUEUE}")
    print(f"Identity  : {identity}")

    # Connect to the REMOTE Temporal Server
    client = await Client.connect(
        temporal_host,
        namespace=namespace,
    )

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[OrderWorkflow],
        activities=[
            validate_order,
            charge_payment,
            confirm_order,
            record_event,
            send_notification,
        ],
        # identity is shown in the Web UI under
        # each task execution — useful for debugging
        # which physical server ran the task
        identity=identity,
    )

    print("\nWorker running. Press Ctrl+C to stop.\n")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())