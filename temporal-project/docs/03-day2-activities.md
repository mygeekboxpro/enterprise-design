# Day 2: Your First Activity

## Goal for Today

Write a single Activity, run it via a Worker, and
observe it in the Web UI. No Workflow yet.

---

## What is an Activity (Deep Dive)

```
┌─────────────────────────────────────────────┐
│  ACTIVITY                                   │
│                                             │
│  - A plain async Python function            │
│  - Decorated with @activity.defn            │
│  - Does ONE thing (validate, charge, save)  │
│  - Can fail → Temporal retries it           │
│  - Has NO knowledge of the Workflow         │
│  - Gets input, returns output               │
└─────────────────────────────────────────────┘
```

---

## Activity Anatomy

```python
from temporalio import activity

@activity.defn                      # ← marks this as Activity
async def validate_order(           # ← plain async function
    order_id: str                   # ← typed input
) -> bool:                          # ← typed output

    # Real I/O is fine here
    # DB queries, API calls, file reads — all OK

    if not order_id:
        raise ValueError("order_id is required")
    return True
```

### Rules for Activities

| Rule                          | Why                              |
|-------------------------------|----------------------------------|
| Use `@activity.defn`          | Temporal needs to register it    |
| Type your inputs and outputs  | Temporal serializes to JSON      |
| Raise exceptions to fail      | Temporal will catch and retry    |
| Keep each Activity focused    | One job per Activity             |
| Make them idempotent          | They may run more than once      |

---

## Retry Policy — How Temporal Handles Failures

```
Activity raises exception:

  Attempt 1 → ✗ fails
              wait 1 second
  Attempt 2 → ✗ fails
              wait 2 seconds
  Attempt 3 → ✗ fails
              wait 4 seconds
  ...
  Attempt N → ✓ succeeds OR max retries reached

Default behavior:
  - Retries forever (infinite by default)
  - Initial interval: 1 second
  - Max interval: 100 seconds
  - Backoff coefficient: 2x (doubles each time) - exponential backoff
```

You can customize this (covered in Day 4).

---

## Activity Context

Inside an Activity, you can access metadata:

```python
@activity.defn
async def process_order(order_id: str) -> str:
    info = activity.info()

    print(info.workflow_id)      # "order-001"
    print(info.attempt)          # 1, 2, 3... (retry count)
    print(info.task_queue)       # "order-task-queue"

    # Use attempt to handle retry logic:
    if info.attempt > 1:
        print("This is a retry — check for duplicates!")

    return "processed"
```

---

## Heartbeating — For Long-Running Activities

If your Activity takes more than 10 seconds, use
heartbeat to tell Temporal "I'm still alive":

```python
@activity.defn
async def long_running_task(items: list) -> int:
    count = 0
    for item in items:
        process(item)
        count += 1
        activity.heartbeat(f"Processed {count} items")
        # ↑ Without this, Temporal may assume it crashed
    return count
```

**Term:** `heartbeat_timeout` — if no heartbeat received
within this time, Temporal cancels and retries the Activity.

---

## Your 4 Order Activities

The order system has these Activities:

```
validate_order  ─── Check order_id exists and amount > 0
charge_payment  ─── Simulate charging a payment
confirm_order   ─── Mark order as confirmed
record_event    ─── Write an event to the Event Store
```

```
Flow:
  validate_order
       │
       ▼
  charge_payment
       │
       ▼
  confirm_order
       │
       ▼
  record_event
```

---

## Code: activities.py

See the `activities.py` artifact for complete code.

Key things to notice:

1. Each function has `@activity.defn`
2. Each has typed input/output
3. Each raises specific exceptions to trigger retries
4. `record_event` is idempotent (safe to run twice)

---

## Running an Activity Standalone (Day 2 Exercise)

At this stage, you cannot run an Activity alone —
it must run inside a Worker. But you can test it
without a Workflow:

```python
# tests/test_activities_standalone.py
import pytest
from src.activities import validate_order

@pytest.mark.asyncio
async def test_validate_order_success():
    result = await validate_order("order-001")
    assert result is True

@pytest.mark.asyncio
async def test_validate_order_fail():
    with pytest.raises(ValueError):
        await validate_order("")
```

Run:
```bash
pytest tests/test_activities_standalone.py -v
```

No Temporal server needed for unit tests.

---

## Day 2 Checklist

- [ ] Read all of this document
- [ ] Understand what `@activity.defn` does
- [ ] Understand retry behavior
- [ ] Know what `activity.info()` gives you
- [ ] Know what heartbeating is for
- [ ] Read `activities.py` source code
- [ ] Run standalone tests
- [ ] Proceed to `04-day3-workflows.md`
