# Day 1: Temporal Core Concepts

## 1. The Problem Temporal Solves

### Without Temporal

```
Your code:
  Step 1: Validate order      ✓ succeeds
  Step 2: Charge payment      ✓ succeeds
  Step 3: Send confirmation   ✗ SERVER CRASHES

Result:
  - Payment was charged
  - Email never sent
  - No automatic retry
  - You must handle this manually
  - Your code has no memory of what happened
```

### With Temporal

```
Your code:
  Step 1: Validate order      ✓ succeeds  ← saved
  Step 2: Charge payment      ✓ succeeds  ← saved
  Step 3: Send confirmation   ✗ CRASHES

  [ Server restarts ]

  Temporal resumes:
  Step 3: Send confirmation   ✓ retried automatically

Result:
  - Payment is NOT charged again
  - Email IS sent
  - Temporal remembered where you were
```

**Key insight:** Temporal gives your code a persistent memory.

---

## 2. Core Architecture

```
┌─────────────────────────────────────────────────┐
│                TEMPORAL SERVER                  │
│                                                 │
│  ┌──────────────┐      ┌───────────────────┐    │
│  │  Task Queue  │      │  Workflow History │    │
│  │  "orders"    │      │  (append-only log)│    │
│  └──────┬───────┘      └───────────────────┘    │
└─────────│───────────────────────────────────────┘
          │ polls
          ▼
┌─────────────────────┐
│      WORKER         │  ← YOUR process (you run this)
│                     │
│  ┌───────────────┐  │
│  │   Workflow    │  │  ← orchestration logic
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │   Activity    │  │  ← real work (DB, API calls)
│  └───────────────┘  │
└─────────────────────┘
          ▲
          │ starts workflows
┌─────────────────────┐
│    STARTER / APP    │  ← your trigger (API, CLI, cron)
└─────────────────────┘
```

---

## 3. Component Breakdown

### Temporal Server

- Runs in Docker (you don't write this)
- Manages all workflow state
- Stores execution history
- Decides what to run next
- Accessible at: `localhost:7233`
- Web UI at: `localhost:8080`

---

### Workflow

- A Python function decorated with `@workflow.defn`
- **Orchestrates** other steps (Activities)
- **Does NOT** do real work itself
- **Must be deterministic** — no random, no direct I/O
- Temporal replays it to reconstruct state

```python
# Workflow = conductor of an orchestra
# It tells others what to play, but doesn't play itself

@workflow.defn
class OrderWorkflow:
    @workflow.run
    async def run(self, order_id: str):
        # WRONG — don't do I/O here directly
        # requests.post(...)  ← NEVER in a Workflow

        # CORRECT — delegate to Activities
        await workflow.execute_activity(validate_order, ...)
        await workflow.execute_activity(charge_payment, ...)
        await workflow.execute_activity(send_confirmation, ...)
```

---

### Activity

- A plain Python function decorated with `@activity.defn`
- **Does the real work**: calls APIs, writes to DB, etc.
- **Can fail** — Temporal will retry it automatically
- Each Activity call is independently retried

```python
# Activity = musician in the orchestra
# It does the actual work

@activity.defn
async def charge_payment(order_id: str) -> str:
    # Real I/O here is FINE
    result = await payment_api.charge(order_id)
    return result
```

---

### Worker

- A Python process YOU run (`python worker.py`)
- Polls the Task Queue for work
- Executes both Workflows and Activities
- Can run multiple Workers for scale

---

### Task Queue

- A named string: `"order-task-queue"`
- Connects the Temporal Server to your Workers
- Workflows and Workers must use the **same name**

---

## 4. Workflow vs Activity — Key Differences

| Property             | Workflow              | Activity             |
|----------------------|-----------------------|----------------------|
| Purpose              | Orchestrate steps     | Do real work         |
| I/O allowed?         | ❌ No                  | ✅ Yes                |
| Deterministic?       | ✅ Must be             | ❌ Not required       |
| Retried by Temporal? | ✅ Replayed            | ✅ Retried on failure |
| Calls DB/API?        | ❌ Never directly      | ✅ Always here        |
| Has state?           | ✅ Via signals/queries | ❌ Stateless          |

---

## 5. Execution Flow (Step by Step)

```
1. You call: starter.py
   └─ Sends "start OrderWorkflow" to Temporal Server

2. Temporal Server:
   └─ Assigns workflow to Task Queue "order-task-queue"

3. Your Worker (running):
   └─ Polls Task Queue → picks up the workflow task

4. Worker executes Workflow function:
   └─ Workflow calls: execute_activity(validate_order)

5. Temporal Server:
   └─ Schedules validate_order on Task Queue

6. Worker executes Activity: validate_order()
   └─ Returns result to Temporal Server
   └─ Temporal saves result to History ← CHECKPOINT

7. Workflow continues:
   └─ Calls next Activity: charge_payment()

8. Repeat until Workflow completes
   └─ Final result stored in History
```

---

## 6. Durability — How Crash Recovery Works

```
TIMELINE:

  t=0  Workflow starts
  t=1  Activity 1 completes ──────────────── SAVED in History
  t=2  Activity 2 completes ──────────────── SAVED in History
  t=3  WORKER CRASHES ✗
  t=4  Worker restarts
  t=5  Temporal replays Workflow:
         Activity 1? Already in History → skip, return saved result
         Activity 2? Already in History → skip, return saved result
         Activity 3? Not in History → execute it now ✓
  t=6  Workflow continues from Activity 3
```

**Term to memorize:** `Idempotent` — safe to run multiple
times with the same result. Your Activities should be
idempotent so retries don't cause double charges, etc.

---

## 7. The Temporal Web UI

Open `http://localhost:8080` after setup.

```
┌────────────────────────────────────────────────┐
│  TEMPORAL WEB UI                               │
│                                                │
│  Workflows                                     │
│  ┌─────────────────────────────────────────┐  │
│  │ ID: order-001   Status: ✓ Completed     │  │
│  │ ID: order-002   Status: ⟳ Running       │  │
│  │ ID: order-003   Status: ✗ Failed        │  │
│  └─────────────────────────────────────────┘  │
│                                                │
│  Click any workflow to see:                    │
│  - Full execution history                      │
│  - Which Activity failed                       │
│  - Retry count                                 │
│  - Input/output of each step                  │
│  - Exact error message                         │
└────────────────────────────────────────────────┘
```

**Rule:** After running any code, always check the Web UI.
It is your primary debugging tool.

---

## 8. Key Terms to Memorize

| Term          | One-Line Definition                           |
|---------------|-----------------------------------------------|
| Workflow      | Orchestrates steps; no direct I/O             |
| Activity      | Does real work; can fail and be retried       |
| Worker        | Your process that runs both                   |
| Task Queue    | Named channel between server and worker       |
| History       | Append-only log of everything that happened   |
| Deterministic | Same inputs → always same outputs             |
| Idempotent    | Safe to run twice; same result both times     |
| Signal        | External message sent into a running workflow |
| Query         | Read current state without changing it        |
| Durability    | Survives crashes; resumes where it left off   |

---

## Day 1 Checklist

- [ ] Read this document fully
- [ ] Understand Workflow vs Activity difference
- [ ] Know what a Worker does
- [ ] Know what a Task Queue is
- [ ] Understand how crash recovery works
- [ ] Proceed to `02-setup.md`
