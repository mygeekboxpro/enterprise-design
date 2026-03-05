# Day 1 (Part 2): Environment Setup

## What You Will Install

```
┌─────────────────────────────────────────┐
│  Your Machine                           │
│                                         │
│  Docker:                                │
│  ┌─────────────────────────────────┐    │
│  │  Temporal Server  (port 7233)   │    │
│  │  Temporal Web UI  (port 8080)   │    │
│  │  Elasticsearch    (port 9200)   │    │
│  └─────────────────────────────────┘    │
│                                         │
│  Python (you run these):                │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │  worker.py  │  │   starter.py    │   │
│  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────┘
```

---

## Step 1: Create Project Directory

```bash
mkdir temporal-order-project
cd temporal-order-project
mkdir docs src tests
```

---

## Step 2: Create docker-compose.yml

Copy from the `docker-compose.yml` artifact into the
project root.

Start services:

```bash
docker-compose up -d
```

Wait 30 seconds. Then verify:

```bash
docker ps
```

Expected output (all should show "Up"):

```
temporalio/ui:2.21.3           Up
temporalio/auto-setup:1.22.0   Up
elasticsearch:7.16.2           Up
postgres:13                    Up
```

---

## Step 3: Open the Web UI

Open browser: `http://localhost:8080`

You should see the Temporal Web UI with no workflows yet.

```
✓ If you see the UI → setup is working
✗ If blank page → wait 30 more seconds, refresh
✗ If error → check: docker ps (are containers running?)
```

---

## Step 4: Install Python Dependencies

```bash
pip install temporalio pytest pytest-asyncio
```

Verify:

```bash
python -c "import temporalio; print('OK')"
```

---

## Step 5: Verify File Structure

```
temporal-order-project/
├── docker-compose.yml   ← created in Step 2
├── requirements.txt     ← pip list
├── docs/
│   ├── 01-concepts.md
│   ├── 02-setup.md      ← you are here
│   ├── 03-day2-activities.md
│   ├── 04-day3-workflows.md
│   ├── 05-day4-retry-signals.md
│   └── 06-exercises.md
├── dynamicconfig/
│   ├── dev-es.yaml
├── src/
│   ├── activities.py
│   ├── workflows.py
│   ├── worker.py
│   └── starter.py
└── tests/
    └── test_workflows.py
```

---

## Troubleshooting

| Problem                  | Fix                                  |
|--------------------------|--------------------------------------|
| Port 8080 already in use | Stop other services: `lsof -i :8080` |
| UI not loading           | Wait 60s, retry                      |
| Docker not running       | Start Docker Desktop first           |
| Import error temporalio  | `pip install temporalio`             |
| Connection refused 7233  | `docker-compose up -d` again         |

---

## Setup Checklist

- [ ] Project directory created
- [ ] Docker containers running (`docker ps`)
- [ ] Web UI accessible at `http://localhost:8080`
- [ ] Python `import temporalio` works
- [ ] File structure matches above

**Next:** `docs/03-day2-activities.md`
