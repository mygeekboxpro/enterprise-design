# Event Store Project - Setup Guide

### Prerequisites

- macOS (Intel)
- uv installed

### 1. Verify CPU architecture

```bash
uname -m
```

#### Expected

- x86_64

### 2. Verify `uv`

```bash
which uv
uv --version
```

#### If missing, run

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Restart terminal after install.

### 3. Check Docker

```bash
uv run docker --version
```

**Expected output:**

```
Docker version 20.10.0 or higher
```

### 4. Check Docker Compose

```bash
uv run docker-compose --version
```

**Expected output:**

```
docker-compose version 1.29.0 or higher
```

---

## Step 1: Create Project Directory

```bash
# Create project folder
mkdir event-store-project
cd event-store-project

# Create subdirectories
mkdir docs src tests

# Verify structure
tree -L 1
```

**Expected output:**

```
event-store-project/
├── docs/
├── src/
└── tests/
```

## Step 2: Create files needed for environment configuration

- TASK 1a: PYTHON VERSION FILE
    - Change to project directory
    ```bash
      cd event-store-project
    ```

- TASK 1b: PYTHON VERSION FILE
    - FILE: `.python-version`
    ```
    3.11
    ```

- TASK 1c: SAMPLE ENVIRONMENT FILE
    - FILE: `.env.example`
    ```env
    # LLM Configuration
  
    # For OpenAI:
    OPENAI_API_KEY=your-openai-key-here
    OPENAI_TRACING_ENABLED=true
    ```

- TASK 1d: CREATE REQUIREMENTS FILE
    - FILE: `pyproject.toml`
       ```
        [project]
        name = "event-store-project"
        version = "0.1.0"
        description = "Add your description here"
        requires-python = ">=3.11"
      
        dependencies = [
            "psycopg2-binary>=2.9.9",
            "pytest>=7.4.3",
            "python-dateutil>=2.8.2",
        ]
      
        [build-system]
        requires = ["setuptools>=78.1.0"]
        build-backend = "setuptools.build_meta"
      
        [tool.setuptools]
        package-dir = { "" = "src" }
      
        [tool.setuptools.packages.find]
        where = ["src"]
       ```
    - **What each package does:**
       ```
       ┌─────────────────┬──────────────────────────────────┐
       │ Package         │ Purpose                          │
       ├─────────────────┼──────────────────────────────────┤
       │ psycopg2-binary │ PostgreSQL database driver       │
       │ pytest          │ Testing framework                │
       │ python-dateutil │ Date/time parsing utilities      │
       └─────────────────┴──────────────────────────────────┘
       ```
## Step 3: Create Python Virtual Environment
- **Copy environment variables**
  ```bash
  cp .env.example .env
  ```
- **Enable environment configuration**
  ```bash
  set -a
  source .env
  set +a
  ```
- **Test environment configuration:**
   ```bash
      uv run python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key loaded:', 'ANTHROPIC_API_KEY' in os.environ)"
   ```
  > **Expected**  
  API Key loaded: True <br/><br/>
  **SUCCESS CRITERIA** <br/>
  >- ✅ .env file exists with real API key
  >- ✅ .gitignore prevents .env from being committed
  >- ✅ Environment variables load successfully

- **Install `.venv`**
  ```bash
  rm -rf .venv
  uv venv
  ```
- **Activate `.venv`**
  ```bash
  source .venv/bin/activate
  ```
- **Verify Python Installation**
  ```bash
  which python
  uv run python --version
  ```
  > **Expected**<br/>
  .../.venv/bin/python <br/>
  Python 3.11.14<br/>

- Install Dependencies
    - Run from project root directory
    ```bash
    uv pip install -e ".[dev]"
    ```
  **Expected**
    ```
    No errors
    ```

---

## Step 4: Create Docker Compose File

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: event-store-db
    environment:
      POSTGRES_DB: eventstore
      POSTGRES_USER: eventstore
      POSTGRES_PASSWORD: eventstore123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U eventstore"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

**Configuration breakdown:**
```
┌──────────────────┬──────────────────────────────────┐
│ Setting          │ Explanation                      │
├──────────────────┼──────────────────────────────────┤
│ image            │ PostgreSQL version 15            │
│ container_name   │ Name for easy reference          │
│ POSTGRES_USER    │ Database username                │
│ POSTGRES_PASSWORD│ Database password                │
│ POSTGRES_DB      │ Database name                    │
│ ports            │ 5432:5432 = host:container       │
│ volumes          │ Persist data between restarts    │
│ healthcheck      │ Verify database is ready         │
└──────────────────┴──────────────────────────────────┘
```

## Step 5: Start PostgreSQL

```bash
# Start database
docker-compose up -d

# Verify it's running
docker-compose ps
```

Expected output:
```
NAME              STATUS         PORTS
event-store-db    Up (healthy)   0.0.0.0:5432->5432/tcp
```

## Step 6: Create Database Schema

Create `schema.sql` in project root:

```sql
-- Events table: stores all events
CREATE TABLE IF NOT EXISTS events (
    event_id UUID PRIMARY KEY,
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL,
    data JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE(aggregate_type, aggregate_id, version)
);

-- Index for fast aggregate lookup
CREATE INDEX idx_aggregate 
ON events(aggregate_type, aggregate_id, version);

-- Index for event type queries
CREATE INDEX idx_event_type 
ON events(event_type);

-- Index for time-based queries
CREATE INDEX idx_timestamp 
ON events(timestamp DESC);
```

**Schema explanation:**
```
┌──────────────────┬──────────────────────────────────┐
│ Column           │ Purpose                          │
├──────────────────┼──────────────────────────────────┤
│ event_id         │ Unique identifier (UUID)         │
│ aggregate_type   │ Entity type (e.g., "Order")      │
│ aggregate_id     │ Specific entity (e.g., "123")    │
│ event_type       │ What happened (e.g., "Created")  │
│ version          │ Sequence number for aggregate    │
│ data             │ Event payload (JSON)             │
│ timestamp        │ When event occurred              │
├──────────────────┼──────────────────────────────────┤
│ UNIQUE constraint│ Prevent duplicate versions       │
│ Indexes          │ Fast queries by aggregate/time   │
└──────────────────┴──────────────────────────────────┘
```
**Sample Event:**
```
{
  "event_id": "uuid-1234",
  "event_type": "OrderCreated",
  "aggregate_id": "order-123",
  "aggregate_type": "Order",
  "data": {
    "customer_id": "cust-456",
    "created_at": "2024-02-17T10:00:00Z"
  },
  "version": 1,
  "timestamp": "2024-02-17T10:00:00Z"
}
```

Apply schema:
```bash
# Connect to database and run schema
docker exec -i event-store-db psql -U eventstore \
  -d eventstore < sql/schema.sql

# Verify tables created
docker exec -it event-store-db psql -U eventstore \
  -d eventstore -c "\dt"
```

Expected output:
```
           List of relations
 Schema |  Name  | Type  |   Owner    
--------+--------+-------+------------
 public | events | table | eventstore
```

## Step 7: Test Database Connection

Create `test_connection.py` in project root:

```python
import psycopg2

# Connection parameters
conn_params = {
    'host': 'localhost',
    'port': 5432,
    'database': 'eventstore',
    'user': 'eventstore',
    'password': 'eventstore123'
}

try:
    # Connect to database
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()
    
    # Test query
    cursor.execute('SELECT version()')
    db_version = cursor.fetchone()
    
    print("✓ Database connection successful!")
    print(f"✓ PostgreSQL version: {db_version[0]}")
    
    # Close connection
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

Run test:
```bash
cd .. 
uv run python sql/test_connection.py
```

Expected output:
```
✓ Database connection successful!
✓ PostgreSQL version: PostgreSQL 15.x ...
```

## Step 8: Verify Complete Setup

Run this checklist:

```bash
# 1. Virtual environment active?
echo $VIRTUAL_ENV
# Should show path to venv

# 2. Packages installed?
uv pip list | grep psycopg2
# Should show psycopg2-binary

# 3. Database running?
docker-compose ps
# Should show "Up (healthy)"

# 4. Schema created?
docker exec -it event-store-db psql -U eventstore \
  -d eventstore -c "SELECT COUNT(*) FROM events"
# Should show "0" (empty table)

# 5. Connection works?
python test_connection.py
# Should show success messages
```

All checks should pass.

## Project Structure (Final)

```
event-store-project/
├── venv/                    # Virtual environment
├── docs/
│   ├── 01-concepts.md       # ← You already read this
│   ├── 02-setup.md          # ← You are here
│   ├── 03-implementation.md # ← Next
│   └── 04-exercises.md
├── src/
│   ├── __init__.py          # (create empty file)
│   ├── event_store.py       # (will create next)
│   ├── events.py            # (will create next)
│   ├── order.py             # (will create next)
│   └── main.py              # (will create next)
├── tests/
│   ├── __init__.py          # (create empty file)
│   └── test_order.py        # (will create next)
├── docker-compose.yml
├── requirements.txt
├── schema.sql
└── test_connection.py
```

Create empty `__init__.py` files:
```bash
touch src/__init__.py
touch tests/__init__.py
```

## Common Issues & Solutions

### Issue 1: Port 5432 Already in Use
```
Error: port 5432 is already allocated
```

**Solution:**
```bash
# Stop other PostgreSQL instances
docker ps | grep postgres
docker stop <container-id>

# Or change port in docker-compose.yml
ports:
  - "5433:5432"  # Use 5433 on host
```

### Issue 2: Permission Denied (Docker)
```
Error: permission denied while trying to connect
```

**Solution:**
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in

# Or run with sudo
sudo docker-compose up -d
```

### Issue 3: psycopg2 Installation Fails
```
Error: pg_config executable not found
```

**Solution:**
```bash
# Use binary version (already in requirements.txt)
pip install psycopg2-binary

# Or install PostgreSQL dev headers
# Ubuntu/Debian:
sudo apt-get install libpq-dev
# Mac:
brew install postgresql
```

## Troubleshooting Commands

```bash
# View database logs
docker-compose logs postgres

# Connect to database manually
docker exec -it event-store-db psql -U eventstore \
  -d eventstore

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
docker exec -i event-store-db psql -U eventstore \
  -d eventstore < schema.sql

# Stop database
docker-compose down

# Start database
docker-compose up -d
```

## Database Credentials Summary

```
┌──────────────┬─────────────────┐
│ Parameter    │ Value           │
├──────────────┼─────────────────┤
│ Host         │ localhost       │
│ Port         │ 5432            │
│ Database     │ eventstore      │
│ User         │ eventstore      │
│ Password     │ eventstore123   │
└──────────────┴─────────────────┘

IMPORTANT: These are for local development only.
Never use these credentials in production.
```

## Next Steps

✓ Environment is ready
✓ Database is running
✓ Schema is created
✓ Connection is tested

Next: Read 03-implementation.md to build the Event Store.


---

---

## 📌 FAQ

#### Regenerate the lock after updating pyproject.toml:

```bash
uv lock --upgrade
uv sync
```

#### If you want to force just one dependency line to move:

```bash
uv lock --upgrade-package openai-agents
uv sync
```
