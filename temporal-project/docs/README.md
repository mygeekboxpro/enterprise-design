# Week 2: Temporal Workflow Orchestration

## What You Will Learn

| Term        | Definition                                          |
|-------------|-----------------------------------------------------|
| Temporal    | Platform for durable, fault-tolerant workflows      |
| Workflow    | Orchestrator — decides what to do and in what order |
| Activity    | A single unit of real work (call API, write DB)     |
| Worker      | Your process that runs Workflows and Activities     |
| Task Queue  | Named channel that Workers listen on for work       |
| Workflow ID | Stable business ID (e.g. "order-123")               |
| Run ID      | Unique ID for one specific execution                |
| Signal      | External message sent into a running Workflow       |
| Query       | Read current state of a running Workflow            |
| History     | Temporal's append-only log of all Workflow events   |

---

## How Temporal Fits into Your Learning Path

```
Week 1                          Week 2
─────────────────────────────────────────────────────
Event Store:                    Temporal:
"What happened to data"         "How work was executed"
PostgreSQL stores events        Temporal stores workflow
                                execution history
You append events manually      Activities append events
No retry logic                  Automatic retries built-in
No fault tolerance              Crash = resume, not restart
```

---

## Learning Structure (5-Day Plan)

```
Day 1 ─── Core Concepts + Web UI Tour
Day 2 ─── Your First Activity (no Workflow yet)
Day 3 ─── Wrap Activity in a Workflow
Day 4 ─── Retries, Failures, Signals, Queries
Day 5 ─── Full Order Workflow + Tests + Exercises
```

---

## Project Structure

```
temporal-order-project/
├── README.md
├── docker-compose.yml
├── pyproject.toml
├── docs/
│   ├── 01-concepts.md            ← Start here (Day 1)
│   ├── 02-setup.md               ← Environment setup
│   ├── 03-day2-activities.md     ← Day 2
│   ├── 04-day3-workflows.md      ← Day 3
│   ├── 05-day4-retry-signals.md  ← Day 4
│   └── 06-exercises.md           ← Day 5 exercises
├── src/                          
│   ├── activities.py             ← All Activity functions
│   ├── workflows.py              ← Workflow orchestrator
│   ├── worker.py                 ← Worker process
│   └── starter.py                ← Start a workflow run
└── tests/                        
    └── test_workflows.py         ← Unit tests
```

---

## Estimated Time

| Day | Focus                      | Hours    |
|-----|----------------------------|----------|
| 1   | Concepts + UI tour + setup | 2–3      |
| 2   | First Activity             | 1–2      |
| 3   | First Workflow             | 1–2      |
| 4   | Retries, Signals, Queries  | 2–3      |
| 5   | Full project + exercises   | 3–4      |
|     | **Total**                  | **9–14** |

---

## Week 3 Preview

Week 3 integrates Week 1 + Week 2:

- Temporal Workflow triggers Event Store writes
- Provenance: track data lineage through workflow
- Run Registry: catalog all workflow runs
- Checkpoints: save state at key steps
