# Day 4: Retries, Signals & Queries

## Goal for Today

See Temporal's fault tolerance in action.
Learn to communicate with a running Workflow.

---

## Part A: Retries (The Core Value of Temporal)

### Experiment: Make an Activity Fail on Purpose

Add this to `activities.py` temporarily:

```python
@activity.defn
async def flaky_activity(order_id: str) -> str:
    info = activity.info()

    # Fail the first 2 attempts on purpose
    if info.attempt < 3:
        raise Exception(
            f"Simulated failure on attempt {info.attempt}"
        )

    return f"Succeeded on attempt {info.attempt}"
```

### What You Will See in the Web UI

```
Event #  Type                         Details
──────────────────────────────────────────────────────
5        ActivityTaskScheduled        flaky_activity
6        ActivityTaskStarted
7        ActivityTaskFailed           attempt 1 ✗
                                      waiting 1s...
8        ActivityTaskScheduled        flaky_activity
9        ActivityTaskStarted
10       ActivityTaskFailed           attempt 2 ✗
                                      waiting 2s...
11       ActivityTaskScheduled        flaky_activity
12       ActivityTaskStarted
13       ActivityTaskCompleted        attempt 3 ✓
                                      result: "Succeeded"
```

**This is the most important thing to observe in Day 4.**
Temporal retried your failed Activity automatically.
Your Workflow had no idea the failure happened.

---

### Custom Retry Policy

```python
from temporalio.common import RetryPolicy
from datetime import timedelta

await workflow.execute_activity(
    charge_payment,
    order_id,
    start_to_close_timeout=timedelta(seconds=30),
    retry_policy=RetryPolicy(
        initial_interval=timedelta(seconds=1),
        # ↑ Wait 1s before first retry
        backoff_coefficient=2.0,
        # ↑ Double wait each retry: 1s, 2s, 4s, 8s...
        maximum_interval=timedelta(seconds=30),
        # ↑ Never wait more than 30s
        maximum_attempts=5,
        # ↑ Give up after 5 attempts (0 = infinite)
        non_retryable_error_types=["ValueError"],
        # ↑ Don't retry these — they're logic errors
    ),
)
```

### Retryable vs Non-Retryable Errors

```
RETRYABLE (should retry):
  - Network timeout
  - Service unavailable
  - Database connection lost
  - Rate limit exceeded

NON-RETRYABLE (don't retry):
  - ValueError: "invalid order_id format"
  - PermissionError: "user not authorized"
  - Logic errors that won't fix themselves
```

---

## Part B: Signals — Send Messages to Running Workflows

### What is a Signal?

A Signal lets you send a message **into** a running
Workflow from outside.

```
External code        Running Workflow
(your app)               (Temporal)
    │                        │
    │  signal("approve")     │
    │───────────────────────▶│
    │                        │ ← Workflow receives it
    │                        │   and can act on it
```

### Use Cases

| Scenario                 | Signal Name        |
|--------------------------|--------------------|
| Human approves a request | `approve`          |
| Payment webhook arrives  | `payment_received` |
| Cancel a running order   | `cancel`           |
| Update shipping address  | `update_address`   |

---

### Signal Implementation

```python
# In workflows.py:

@workflow.defn
class OrderWorkflow:

    def __init__(self):
        self._approved = False  # ← internal state

    @workflow.signal  # ← marks as Signal handler
    async def approve(self) -> None:
        self._approved = True
        # Workflow is now unblocked

    @workflow.run
    async def run(self, order_id: str) -> str:
        await workflow.execute_activity(validate_order, ...)

        # Wait for approval signal (blocks here)
        await workflow.wait_condition(
            lambda: self._approved
        )
        # ↑ Workflow pauses here until approve() is called
        # ↑ Worker is NOT blocked — other workflows run fine

        await workflow.execute_activity(charge_payment, ...)
        return "approved and completed"
```

### Sending a Signal from Outside

```python
# In a separate script or API handler:

handle = client.get_workflow_handle("order-001")
await handle.signal(OrderWorkflow.approve)
```

---

## Part C: Queries — Read Workflow State

### What is a Query?

A Query reads the **current state** of a running
Workflow without modifying it.

```
External code        Running Workflow
(your app)               (Temporal)
    │                        │
    │  query("get_status")   │
    │───────────────────────▶│
    │◀───────────────────────│
    │  "waiting_for_approval"│
```

---

### Query Implementation

```python
# In workflows.py:

@workflow.defn
class OrderWorkflow:

    def __init__(self):
        self._status = "started"

    @workflow.query  # ← marks as Query handler
    def get_status(self) -> str:
        return self._status  # returns current state

    @workflow.run
    async def run(self, order_id: str) -> str:
        self._status = "validating"
        await workflow.execute_activity(validate_order, ...)

        self._status = "waiting_approval"
        await workflow.wait_condition(lambda: self._approved)

        self._status = "charging"
        await workflow.execute_activity(charge_payment, ...)

        self._status = "completed"
        return "done"
```

### Querying from Outside

```python
handle = client.get_workflow_handle("order-001")
status = await handle.query(OrderWorkflow.get_status)
print(status)  # "waiting_approval"
```

---

## Signal vs Query vs Activity — Comparison

| Feature   | Signal            | Query          | Activity          |
|-----------|-------------------|----------------|-------------------|
| Direction | In → Workflow     | Out ← Workflow | Workflow → Worker |
| Modifies? | ✅ Yes             | ❌ No           | ✅ Yes             |
| Async?    | ✅ Fire and forget | ❌ Synchronous  | ✅ Async           |
| Use for   | External events   | Status checks  | Real work         |

---

## Part D: Timers — Waiting in Workflows

```python
@workflow.run
async def run(self, order_id: str) -> str:
    await workflow.execute_activity(place_order, ...)

    # Wait 24 hours for payment confirmation
    await asyncio.sleep(...)  # ✗ WRONG
    await workflow.sleep(  # ✓ CORRECT
        timedelta(hours=24)
    )

    # Check if payment arrived
    if not self._payment_received:
        await workflow.execute_activity(cancel_order, ...)
```

**Key:** `workflow.sleep()` is durable. If the Worker
crashes during the 24-hour wait, Temporal resumes the
timer when the Worker restarts. The 24 hours is tracked
by the server, not by your process.

---

## Day 4 Checklist

- [ ] Run the flaky Activity experiment
- [ ] Watch retry attempts in the Web UI
- [ ] Understand RetryPolicy parameters
- [ ] Know what non-retryable errors are
- [ ] Understand what a Signal is and when to use it
- [ ] Understand what a Query is
- [ ] Know the difference: Signal vs Query vs Activity
- [ ] Understand `workflow.sleep()` vs `asyncio.sleep()`
- [ ] Proceed to `06-exercises.md`
