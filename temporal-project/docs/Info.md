═══════════════════════════════════════════════════════════
WEEK 2 — TEMPORAL (REVISED STRUCTURE) — COMPLETE PACKAGE
═══════════════════════════════════════════════════════════

DOCUMENTATION (6 files)
────────────────────────
✓ README.md                  — overview, terminology,
                               5-day plan
✓ docs/01-concepts.md        — Day 1: deep concepts,
                               architecture diagrams,
                               Web UI tour
✓ docs/02-setup.md           — Day 1: environment setup,
                               Docker, verification
✓ docs/03-day2-activities.md — Day 2: Activities deep dive,
                               retry behavior, heartbeating
✓ docs/04-day3-workflows.md  — Day 3: Workflows, determinism,
                               run your first workflow
✓ docs/05-day4-retry-signals.md — Day 4: Retries, Signals,
                               Queries, Timers
✓ docs/06-exercises.md       — Day 5: 7 exercises +
                               challenge project

CODE FILES (5 files)
─────────────────────
✓ src/activities.py          — 5 Activities with full
                               annotations and idempotency
✓ src/workflows.py           — OrderWorkflow with Signals,
                               Queries, RetryPolicy
✓ src/worker.py              — Worker process (run first)
✓ src/starter.py             — Starts a workflow
✓ src/send_signal.py         — Sends approve/cancel signal

TESTS (1 file)
───────────────
✓ tests/test_workflows.py    — 10 unit tests, no server
                               needed

SETUP FILES (3 files)
──────────────────────
✓ docker-compose.yml         — Temporal + PostgreSQL +
                               Elasticsearch + Web UI
✓ dynamicconfig/dev-es.yaml  — Required Temporal config
✓ requirements.txt           — Python dependencies

═══════════════════════════════════════════════════════════
KEY IMPROVEMENTS VS ORIGINAL WEEK 2
═══════════════════════════════════════════════════════════

  1. 5-Day phased structure — concepts before code
  2. Web UI introduced Day 1 — visual from the start
  3. Dedicated retry/failure exercise — see it happen
  4. Signals + Queries added — full Temporal feature set
  5. NO Event Store integration yet — that is Week 3
  6. Deeper documentation per concept

═══════════════════════════════════════════════════════════
HOW TO START
═══════════════════════════════════════════════════════════

Step 1: Create project structure
  mkdir temporal-order-project
  cd temporal-order-project
  mkdir docs src tests dynamicconfig

Step 2: Copy all files into correct directories

Step 3: Start Docker services
  docker-compose up -d

Step 4: Install Python dependencies
  pip install -r requirements.txt

Step 5: Open Web UI
  http://localhost:8080

Step 6: Read docs in order
  Day 1: 01-concepts.md → 02-setup.md
  Day 2: 03-day2-activities.md
  Day 3: 04-day3-workflows.md
  Day 4: 05-day4-retry-signals.md
  Day 5: 06-exercises.md

Step 7: Run tests (Day 2 onward)
  pytest tests/test_workflows.py -v

Step 8: Run the workflow (Day 3)
  Terminal 1: python src/worker.py
  Terminal 2: python src/starter.py
  Terminal 3: python src/send_signal.py order-001

═══════════════════════════════════════════════════════════