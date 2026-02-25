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

- PYTHON VERSION FILE
    - Change to project directory
    ```bash
      cd event-store-project
    ```

- PYTHON VERSION FILE
    - FILE: `.python-version`
    ```
    3.11
    ```

- SAMPLE ENVIRONMENT FILE
    - FILE: `.env.example`
    ```env
    # LLM Configuration
  
    # For OpenAI:
    OPENAI_API_KEY=your-openai-key-here
    OPENAI_TRACING_ENABLED=true
    ```

- CREATE pyproject FILE
    - FILE: `pyproject.toml`
       ```
        [project]
        name = "event-store-project"
        version = "0.1.0"
        description = "Add your description here"
        requires-python = ">=3.11"
      
        dependencies = [
            "python-dotenv>=1.0.1",
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

---
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
