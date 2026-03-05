# Day 5: Exercises

## How to Use This Document

- Complete exercises in order
- Each builds on the previous
- Check the Web UI after every exercise
- Do not look at the solution until you have tried

---

## Exercise 1 — Run the Base Workflow

**Goal:** Run the provided workflow end-to-end.

**Steps:**

1. Start Docker: `docker-compose up -d`
2. Start Worker: `python src/worker.py`
3. Start Workflow: `python src/starter.py`
4. Open `http://localhost:8080`
5. Find `order-001` in the Workflows list
6. Click it and read every event in the History

**You succeed when:**

- [ ] Workflow shows status: Completed
- [ ] You can name each Activity that ran
- [ ] You can see the result in the History

---

## Exercise 2 — Observe a Failure and Retry

**Goal:** Watch Temporal retry a failing Activity.

**Steps:**

1. Open `src/activities.py`
2. Add this temporary function:

```python
@activity.defn
async def flaky_payment(order_id: str) -> str:
    info = activity.info()
    if info.attempt < 3:
        raise Exception(
            f"Temporary failure attempt {info.attempt}"
        )
    return f"Paid on attempt {info.attempt}"
```

3. In `workflows.py`, temporarily replace
   `charge_payment` with `flaky_payment`
4. Run the workflow again with a new ID:
   `python src/starter.py order-002`
5. Open Web UI and watch the retries happen

**You succeed when:**

- [ ] You see 2 failed Activity attempts in the History
- [ ] You see the 3rd attempt succeed
- [ ] The Workflow completes despite the failures

**Restore:** Remove `flaky_payment`, put back
`charge_payment` when done.

---

## Exercise 3 — Add a Custom Retry Policy

**Goal:** Control how Temporal retries a specific Activity.

**Steps:**

1. Open `src/workflows.py`
2. Find the `charge_payment` execute_activity call
3. Add a custom RetryPolicy:
    - maximum_attempts: 3
    - initial_interval: 2 seconds
    - backoff_coefficient: 1.5
    - non_retryable_error_types: `["ValueError"]`
4. Run workflow `order-003`
5. Check the Web UI — the History should show
   your retry settings

**You succeed when:**

- [ ] Workflow runs with new policy in place
- [ ] You can explain what each policy parameter does

---

## Exercise 4 — Add a Status Query

**Goal:** Query a running Workflow for its current status.

**Steps:**

1. In `workflows.py`, add a `_status` field to
   `OrderWorkflow.__init__`
2. Update `_status` at each step:
   `"validating"`, `"charging"`, `"confirming"`,
   `"completed"`
3. Add a `@workflow.query` method `get_status`
   that returns `self._status`
4. Create `src/query_workflow.py`:

```python
import asyncio
from temporalio.client import Client
from workflows import OrderWorkflow


async def main():
    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle("order-001")
    status = await handle.query(OrderWorkflow.get_status)
    print(f"Status: {status}")


asyncio.run(main())
```

5. While the Worker is running a long workflow,
   run `python src/query_workflow.py`

**You succeed when:**

- [ ] You can print the current status of a workflow
- [ ] You see different statuses at different times

---

## Exercise 5 — Add an Approval Signal

**Goal:** Pause a Workflow and resume it with a Signal.

**Steps:**

1. In `workflows.py`, add:
    - `self._approved = False` in `__init__`
    - `@workflow.signal` method `approve()`
      that sets `self._approved = True`
    - After `validate_order`, add:
      `await workflow.wait_condition(lambda: self._approved)`
2. Create `src/send_signal.py`:

```python
import asyncio
from temporalio.client import Client
from workflows import OrderWorkflow


async def main(workflow_id: str):
    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle(workflow_id)
    await handle.signal(OrderWorkflow.approve)
    print(f"Sent approve signal to {workflow_id}")


asyncio.run(main("order-004"))
```

3. Start `order-004`
4. Check Web UI — it should show "Running" (waiting)
5. Run `python src/send_signal.py`
6. Check Web UI — Workflow should resume and complete

**You succeed when:**

- [ ] Workflow pauses waiting for Signal
- [ ] You see "Running" status in Web UI
- [ ] After Signal, Workflow completes

---

## Exercise 6 — Handle a Non-Retryable Error

**Goal:** Understand when NOT to retry.

**Steps:**

1. In `activities.py`, modify `validate_order`:

```python
@activity.defn
async def validate_order(order_id: str) -> bool:
    if not order_id:
        raise ValueError("order_id cannot be empty")
        # ↑ This is a logic error — retrying won't fix it
    if order_id == "bad-order":
        raise Exception("Payment service unavailable")
        # ↑ This is transient — retrying might fix it
    return True
```

2. In your RetryPolicy for `validate_order`, add:
   `non_retryable_error_types=["ValueError"]`

3. Run two workflows:
    - `python src/starter.py ""` (empty ID)
    - `python src/starter.py "bad-order"`

4. Compare the Web UI behavior for each

**You succeed when:**

- [ ] Empty ID fails immediately (no retries)
- [ ] "bad-order" shows multiple retry attempts
- [ ] You understand the difference

---

## Exercise 7 — Use workflow.sleep()

**Goal:** Add a durable timer to a Workflow.

**Steps:**

1. In `workflows.py`, after `validate_order`,
   add a 10-second sleep:

```python
await workflow.sleep(timedelta(seconds=10))
```

2. Run `order-005`
3. While it's sleeping, check the Web UI
   — it shows "Running" (waiting on timer)
4. After 10 seconds, it should continue

**Bonus:** Kill the Worker during the sleep.
Restart it. See that the workflow resumes
from where it left off — not from the start.

**You succeed when:**

- [ ] Workflow pauses for 10 seconds on timer
- [ ] After restart, Workflow continues (not restarts)
- [ ] You can explain why this works

---

## Challenge Exercise — Build a New Workflow

**Goal:** Apply everything from the week.

**Build:** An `ApplicationWorkflow` that:

1. Takes `applicant_id: str` as input
2. Validates the applicant (Activity)
3. Runs a background check (Activity, may fail → retry)
4. Waits for manual approval (Signal)
5. Exposes current stage via Query
6. On approval, sends an acceptance notification (Activity)
7. On rejection (another Signal), sends rejection

**Deliverables:**

- `src/application_activities.py`
- `src/application_workflow.py`
- `tests/test_application_workflow.py`
- Run it end-to-end with a real approval flow

---

## Week 2 Summary — What You Learned

| Concept        | Can you explain it?                                |
|----------------|----------------------------------------------------|
| Workflow       | Orchestrates; no direct I/O; must be deterministic |
| Activity       | Does real work; retriable; can fail                |
| Worker         | Runs both; polls Task Queue                        |
| Retry Policy   | Controls how/when Temporal retries                 |
| Non-retryable  | Errors that should fail immediately                |
| Signal         | External message into a running Workflow           |
| Query          | Read current state without modifying               |
| workflow.sleep | Durable timer — survives crashes                   |
| Determinism    | Same inputs → same output; required for Workflows  |
| History        | Temporal's log; used for replay and crash recovery |

---

## Week 3 Preview

Week 3 connects everything:

- Temporal Workflow calls your Week 1 Event Store
- Add Provenance: track data lineage
- Add Run Registry: catalog all workflow runs
- Add Checkpoints: named save points in Workflow
