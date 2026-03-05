# Day 3: Your First Workflow

## Goal for Today

Write a Workflow that calls your Activities, run the
Worker, start the Workflow, and watch it execute in
the Web UI.

---

## What is a Workflow (Deep Dive)

```
┌─────────────────────────────────────────────────┐
│  WORKFLOW                                       │
│                                                 │
│  - A class decorated with @workflow.defn        │
│  - Has a @workflow.run method (entry point)     │
│  - Calls Activities via execute_activity()      │
│  - MUST be deterministic                        │
│  - CANNOT do direct I/O (no DB, no API calls)   │
│  - Has persistent state (survives crashes)      │
└─────────────────────────────────────────────────┘
```

---

## Determinism — The Most Important Rule

**Deterministic** means: given the same inputs and
history, the Workflow always produces the same outputs.

### WHY this matters:

Temporal replays your Workflow from history to
reconstruct state after a crash. If your Workflow
is non-deterministic, the replay produces different
results — this breaks everything.

### What is FORBIDDEN in a Workflow:

```python
# ✗ NEVER do these in a Workflow:

import random
random.randint(1, 100)        # non-deterministic

import time
time.sleep(10)                # use workflow.sleep() instead

datetime.now()                # use workflow.now() instead

import requests
requests.get("https://...")   # do this in an Activity

open("file.txt")              # do this in an Activity
```

### What to use instead:

```python
# ✓ CORRECT Workflow alternatives:

await asyncio.sleep(10)           # NO — still wrong
await workflow.sleep(10)          # YES — Temporal-aware sleep

datetime.now()                    # NO
workflow.now()                    # YES — deterministic clock

requests.get(...)                 # NO
await workflow.execute_activity(  # YES — delegate to Activity
    fetch_data, ...)
```

---

## Workflow Anatomy

```python
from temporalio import workflow
from datetime import timedelta

@workflow.defn                           # ← marks as Workflow
class OrderWorkflow:

    @workflow.run                        # ← entry point
    async def run(
        self,
        order_id: str                    # ← typed input
    ) -> str:                            # ← typed output

        # Call Activity — correct way
        result = await workflow.execute_activity(
            validate_order,              # Activity function
            order_id,                    # Activity input
            start_to_close_timeout=timedelta(seconds=10),
        )                                # ↑ REQUIRED timeout

        return f"Completed: {order_id}"
```

---

## execute_activity() Parameters

```python
await workflow.execute_activity(
    validate_order,                   # Activity to call
    order_id,                         # Input argument

    # Timeouts (at least one required):
    
    # Time from Activity start to completion
    start_to_close_timeout=timedelta(seconds=30),

    # Total time including queue wait
    schedule_to_close_timeout=timedelta(minutes=5),

    # Optional retry policy:
    retry_policy=RetryPolicy(
        maximum_attempts=3,
        initial_interval=timedelta(seconds=1),
    ),
)
```

### Timeout Types Explained

```
schedule_to_close_timeout:
  ├── schedule_to_start_timeout  (waiting in queue)
  └── start_to_close_timeout     (actually running)

Most common: use start_to_close_timeout only.
```

---

## Workflow Execution Flow

```
starter.py calls:
  client.start_workflow(OrderWorkflow.run, "order-001")
          │
          ▼
  Temporal Server receives task
          │
          ▼
  Worker polls, picks up workflow
          │
          ▼
  Workflow.run() begins:

    execute_activity(validate_order, "order-001")
          │
    ┌─────┴──────────────────────────────┐
    │ Activity runs in Worker            │
    │ Result saved to History            │
    └─────┬──────────────────────────────┘
          │ result returned to Workflow
          ▼
    execute_activity(charge_payment, "order-001")
          │
    ┌─────┴──────────────────────────────┐
    │ Activity runs                      │
    │ Result saved to History            │
    └─────┬──────────────────────────────┘
          ▼
    ... continues until Workflow returns
          │
          ▼
  Temporal marks Workflow COMPLETED
  Result stored in History
```

---

## Running Your First Workflow (Step by Step)

### Terminal 1: Start the Worker
```bash
cd temporal-order-project/src
python worker.py
```

Expected output:
```
Worker started on task queue: order-task-queue
Waiting for workflows and activities...
```

### Terminal 2: Start a Workflow
```bash
cd temporal-order-project/src
python starter.py
```

Expected output:
```
Started workflow order-001
Waiting for result...
Result: Order order-001 completed successfully
```

### Browser: Check the Web UI
1. Open `http://localhost:8080`
2. Click "Workflows"
3. Find `order-001`
4. Click it
5. You will see the full execution history

---

## Reading the Web UI History

```
Event #  Type                        Details
────────────────────────────────────────────────────
1        WorkflowExecutionStarted    input: "order-001"
2        WorkflowTaskScheduled
3        WorkflowTaskStarted
4        WorkflowTaskCompleted
5        ActivityTaskScheduled       validate_order
6        ActivityTaskStarted
7        ActivityTaskCompleted       result: true
8        ActivityTaskScheduled       charge_payment
9        ActivityTaskStarted
10       ActivityTaskCompleted       result: "charged"
...
N        WorkflowExecutionCompleted  result: "Completed"
```

Each row is one entry in the History.
This is what Temporal replays after a crash.

---

## Day 3 Checklist

- [ ] Understand why Workflows must be deterministic
- [ ] Know what is FORBIDDEN in a Workflow
- [ ] Know the `execute_activity()` parameters
- [ ] Read `workflows.py` source code
- [ ] Read `worker.py` source code
- [ ] Run the Worker (Terminal 1)
- [ ] Run the Workflow (Terminal 2)
- [ ] Check the Web UI and read the History
- [ ] Proceed to `05-day4-retry-signals.md`
