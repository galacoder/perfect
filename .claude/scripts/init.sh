#!/bin/bash
#
# init.sh - Environment Setup for Claude Code Tasks
#
# Per Anthropic's "Effective Harnesses" blog recommendation:
# "init.sh script enables rapid environment setup for development servers"
#
# Supports: Node.js, Python, and hybrid projects
#
# Usage:
#   source .claude/scripts/init.sh
#   OR
#   ./.claude/scripts/init.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}  Claude Code Environment Setup  ${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Detect project root
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
echo -e "${GREEN}✓${NC} Project root: ${PROJECT_ROOT}"

# Change to project root
cd "$PROJECT_ROOT"

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Function to run a command with status
run_check() {
  local name="$1"
  local cmd="$2"
  local optional="${3:-false}"

  printf "  %-30s " "$name..."
  if eval "$cmd" >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
    return 0
  else
    if [ "$optional" = "true" ]; then
      echo -e "${YELLOW}⚠ (optional)${NC}"
      return 0
    else
      echo -e "${RED}✗${NC}"
      return 1
    fi
  fi
}

# Detect project type
PROJECT_TYPE="unknown"
if [ -f "package.json" ]; then
  PROJECT_TYPE="nodejs"
fi
if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "Pipfile" ]; then
  if [ "$PROJECT_TYPE" = "nodejs" ]; then
    PROJECT_TYPE="hybrid"
  else
    PROJECT_TYPE="python"
  fi
fi

echo -e "${GREEN}✓${NC} Project type: ${PROJECT_TYPE}"
echo ""

echo -e "${BLUE}1. Checking Prerequisites${NC}"
echo ""

# Check git (required for all)
if command_exists git; then
  GIT_VERSION=$(git --version | cut -d' ' -f3)
  echo -e "  ${GREEN}✓${NC} git: $GIT_VERSION"
else
  echo -e "  ${RED}✗${NC} git not found"
  exit 1
fi

# Node.js checks
if [ "$PROJECT_TYPE" = "nodejs" ] || [ "$PROJECT_TYPE" = "hybrid" ]; then
  if command_exists node; then
    NODE_VERSION=$(node --version)
    echo -e "  ${GREEN}✓${NC} Node.js: $NODE_VERSION"
  else
    echo -e "  ${YELLOW}⚠${NC} Node.js not found (optional for $PROJECT_TYPE)"
  fi

  if command_exists npm; then
    NPM_VERSION=$(npm --version)
    echo -e "  ${GREEN}✓${NC} npm: $NPM_VERSION"
  else
    echo -e "  ${YELLOW}⚠${NC} npm not found"
  fi
fi

# Python checks
if [ "$PROJECT_TYPE" = "python" ] || [ "$PROJECT_TYPE" = "hybrid" ]; then
  if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "  ${GREEN}✓${NC} Python: $PYTHON_VERSION"
  elif command_exists python; then
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    echo -e "  ${GREEN}✓${NC} Python: $PYTHON_VERSION"
  else
    echo -e "  ${RED}✗${NC} Python not found"
    exit 1
  fi

  if command_exists pip3; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    echo -e "  ${GREEN}✓${NC} pip: $PIP_VERSION"
  elif command_exists pip; then
    PIP_VERSION=$(pip --version | cut -d' ' -f2)
    echo -e "  ${GREEN}✓${NC} pip: $PIP_VERSION"
  else
    echo -e "  ${YELLOW}⚠${NC} pip not found"
  fi

  # Check for poetry
  if command_exists poetry; then
    POETRY_VERSION=$(poetry --version | cut -d' ' -f3)
    echo -e "  ${GREEN}✓${NC} Poetry: $POETRY_VERSION"
  fi

  # Check for uv (fast Python package manager)
  if command_exists uv; then
    UV_VERSION=$(uv --version | cut -d' ' -f2)
    echo -e "  ${GREEN}✓${NC} uv: $UV_VERSION"
  fi

  # Check for prefect (if this is a Prefect project)
  if command_exists prefect; then
    PREFECT_VERSION=$(prefect version 2>/dev/null | head -1 || echo "installed")
    echo -e "  ${GREEN}✓${NC} Prefect: $PREFECT_VERSION"
  elif grep -q "prefect" requirements.txt 2>/dev/null || grep -q "prefect" pyproject.toml 2>/dev/null; then
    echo -e "  ${YELLOW}⚠${NC} Prefect required but not installed"
  fi
fi

echo ""
echo -e "${BLUE}2. Installing Dependencies${NC}"
echo ""

# Node.js dependencies
if [ "$PROJECT_TYPE" = "nodejs" ] || [ "$PROJECT_TYPE" = "hybrid" ]; then
  if [ -f "package.json" ]; then
    run_check "npm install" "npm install" "true" || true
  fi
fi

# Python dependencies
if [ "$PROJECT_TYPE" = "python" ] || [ "$PROJECT_TYPE" = "hybrid" ]; then
  if [ -f "pyproject.toml" ] && command_exists poetry; then
    run_check "poetry install" "poetry install" "true" || true
  elif [ -f "requirements.txt" ]; then
    if command_exists uv; then
      run_check "uv pip install" "uv pip install -r requirements.txt" "true" || true
    else
      run_check "pip install" "pip3 install -r requirements.txt" "true" || true
    fi
  elif [ -f "Pipfile" ] && command_exists pipenv; then
    run_check "pipenv install" "pipenv install" "true" || true
  elif [ -f "setup.py" ]; then
    run_check "pip install -e ." "pip3 install -e ." "true" || true
  else
    echo -e "  ${YELLOW}⚠${NC} No Python dependency file found"
  fi
fi

echo ""
echo -e "${BLUE}3. Verifying Project State${NC}"
echo ""

# Check git status
run_check "Git repository" "git status" || true

# Check for uncommitted changes
UNCOMMITTED=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
if [ "$UNCOMMITTED" -gt 0 ]; then
  echo -e "  ${YELLOW}⚠${NC} Uncommitted changes: $UNCOMMITTED files"
else
  echo -e "  ${GREEN}✓${NC} Working directory clean"
fi

# Check for .env file
if [ -f ".env" ]; then
  echo -e "  ${GREEN}✓${NC} .env file found"
else
  if [ -f ".env.example" ]; then
    echo -e "  ${YELLOW}⚠${NC} No .env file (copy from .env.example)"
  fi
fi

echo ""
echo -e "${BLUE}4. Running Quality Checks${NC}"
echo ""

# Node.js quality checks
if [ "$PROJECT_TYPE" = "nodejs" ] || [ "$PROJECT_TYPE" = "hybrid" ]; then
  if [ -f "package.json" ]; then
    # Run tests
    if grep -q '"test"' package.json 2>/dev/null; then
      run_check "npm test" "npm test" "true"
    fi

    # Run linter
    if grep -q '"lint"' package.json 2>/dev/null; then
      run_check "npm run lint" "npm run lint" "true"
    fi

    # Run type check
    if [ -f "tsconfig.json" ]; then
      if grep -q '"type-check"' package.json 2>/dev/null; then
        run_check "Type checking" "npm run type-check" "true"
      elif command_exists tsc; then
        run_check "Type checking" "tsc --noEmit" "true"
      fi
    fi
  fi
fi

# Python quality checks
if [ "$PROJECT_TYPE" = "python" ] || [ "$PROJECT_TYPE" = "hybrid" ]; then
  # Run pytest
  if command_exists pytest; then
    run_check "pytest" "pytest --co -q" "true"  # Just collect, don't run
  elif [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
    echo -e "  ${YELLOW}⚠${NC} pytest configured but not installed"
  fi

  # Run ruff (fast Python linter)
  if command_exists ruff; then
    run_check "ruff check" "ruff check . --quiet" "true"
  fi

  # Run mypy (type checking)
  if command_exists mypy; then
    run_check "mypy" "mypy . --ignore-missing-imports" "true"
  elif [ -f "mypy.ini" ] || grep -q "mypy" pyproject.toml 2>/dev/null; then
    echo -e "  ${YELLOW}⚠${NC} mypy configured but not installed"
  fi

  # Run black (formatter check)
  if command_exists black; then
    run_check "black --check" "black --check . --quiet" "true"
  fi
fi

echo ""
echo -e "${BLUE}5. Checking Active Tasks${NC}"
echo ""

# Check for active tasks
TASK_DIR=$(ls -td .claude/tasks/active/*/ 2>/dev/null | head -1)
if [ -n "$TASK_DIR" ]; then
  TASK_SLUG=$(basename "$TASK_DIR")
  echo -e "  ${GREEN}✓${NC} Active task: $TASK_SLUG"

  # Check for JSON state files (Anthropic best practice)
  if [ -f "$TASK_DIR/feature_list.json" ]; then
    # Parse progress from JSON
    PROGRESS=$(grep -o '"percentage":[^,}]*' "$TASK_DIR/feature_list.json" | cut -d':' -f2 | tr -d ' ')
    echo -e "  ${GREEN}✓${NC} feature_list.json found (${PROGRESS}% complete)"
  else
    echo -e "  ${YELLOW}⚠${NC} No feature_list.json (using legacy markdown format)"
    echo -e "      Consider generating JSON state for better tracking"
  fi

  if [ -f "$TASK_DIR/tests.json" ]; then
    echo -e "  ${GREEN}✓${NC} tests.json found"
  fi
else
  echo -e "  ${YELLOW}⚠${NC} No active tasks"
fi

echo ""
echo -e "${BLUE}6. Development Servers${NC}"
echo ""

# Node.js dev server
if [ -f "package.json" ] && grep -q '"dev"' package.json 2>/dev/null; then
  echo -e "  ${BLUE}→${NC} Node dev server: npm run dev"
fi

# Python/FastAPI/Flask servers
if [ -f "server.py" ] || [ -f "app.py" ] || [ -f "main.py" ]; then
  if grep -q "fastapi\|FastAPI" *.py 2>/dev/null; then
    echo -e "  ${BLUE}→${NC} FastAPI server: uvicorn server:app --reload"
  elif grep -q "flask\|Flask" *.py 2>/dev/null; then
    echo -e "  ${BLUE}→${NC} Flask server: flask run"
  fi
fi

# Prefect server
if command_exists prefect; then
  echo -e "  ${BLUE}→${NC} Prefect: prefect server start"
fi

# Docker compose
if [ -f "docker-compose.yml" ] || [ -f "docker-compose.yaml" ]; then
  echo -e "  ${BLUE}→${NC} Docker Compose: docker-compose up -d"
fi

echo ""
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}  Environment Ready for Claude  ${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo "Quick commands:"
echo "  /start \"description\"  - Start new task"
echo "  /execute              - Continue current task"
echo "  /verify               - Validate task completion"
echo ""

# Export useful variables for the shell session
export CLAUDE_PROJECT_ROOT="$PROJECT_ROOT"
export CLAUDE_TASK_DIR="$TASK_DIR"
export CLAUDE_TASK_SLUG="$TASK_SLUG"
export CLAUDE_PROJECT_TYPE="$PROJECT_TYPE"

echo -e "Exported: CLAUDE_PROJECT_ROOT, CLAUDE_TASK_DIR, CLAUDE_TASK_SLUG, CLAUDE_PROJECT_TYPE"
echo ""
