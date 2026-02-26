# Temporal Workflow Orchestration (Java)

## Key Terms — Memorize These

| Term         | Definition                                        |
|--------------|---------------------------------------------------|
| Workflow     | Orchestrator — coordinates activities             |
| Activity     | Single unit of work (can fail, will retry)        |
| Worker       | Your Java process that runs workflows + activities|
| Task Queue   | Named channel between Temporal server and Worker  |
| Signal       | External event sent INTO a running workflow       |
| Query        | Read current state FROM a running workflow        |
| Idempotent   | Safe to run twice — same result both times        |
| Durability   | Crash → resume from last step, not restart        |

---

## Project Structure

```
temporal-order-project/
├── pom.xml
├── docker-compose.yml
├── dynamicconfig/
│   └── dev-es.yaml
├── docs/
│   ├── 01-concepts.md
│   ├── 02-setup.md
│   ├── 03-day2-activities.md
│   ├── 04-day3-workflows.md
│   ├── 05-day4-retry-signals.md
│   └── 06-exercises.md
└── src/
    ├── main/java/com/example/temporal/
    │   ├── activities/
    │   │   ├── OrderActivities.java
    │   │   └── OrderActivitiesImpl.java
    │   ├── workflows/
    │   │   ├── OrderWorkflow.java
    │   │   └── OrderWorkflowImpl.java
    │   ├── model/
    │   │   ├── OrderInput.java
    │   │   └── OrderResult.java
    │   ├── Worker.java
    │   ├── Starter.java
    │   └── SendSignal.java
    └── test/java/com/example/temporal/
        └── OrderWorkflowTest.java
```

---

## 5-Day Learning Plan

| Day | Focus                        | Files to Read              |
|-----|------------------------------|----------------------------|
| 1   | Concepts + Setup             | 01-concepts.md, 02-setup.md|
| 2   | Activities (units of work)   | 03-day2-activities.md      |
| 3   | Workflows (orchestration)    | 04-day3-workflows.md       |
| 4   | Retries, Signals, Queries    | 05-day4-retry-signals.md   |
| 5   | Exercises + Challenge        | 06-exercises.md            |

---

## How to Run

```bash
# Step 1: Start Temporal server
docker-compose up -d

# Step 2: Open Web UI
open http://localhost:8080

# Step 3: Build project
mvn clean compile

# Step 4: Run tests (no server needed)
mvn test

# Step 5: Start Worker (Terminal 1)
mvn exec:java -Dexec.mainClass="com.example.temporal.Worker"

# Step 6: Start a workflow (Terminal 2)
mvn exec:java -Dexec.mainClass="com.example.temporal.Starter"

# Step 7: Send a signal (Terminal 3)
mvn exec:java -Dexec.mainClass="com.example.temporal.SendSignal"
```

---
