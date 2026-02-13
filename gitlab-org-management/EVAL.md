# Overview

This document describes how to automatically construct evaluation tasks for browser-use agents based on the implementation of a website.

# Expected Output

You will generate a list of tasks, each paired with a corresponding programmatic verifier.

## Task Requirements

You must design tasks across three difficulty levels: **easy**, **medium**, and **hard**.

The difficulty level should be determined by:

1. **Task complexity** — approximately measured by the number of steps required to complete the task. This depends on both:
   - The workflow design of the website.
   - The inherent complexity of the task itself.

2. **Dependencies and prerequisites** — some tasks may appear simple on the surface but are challenging due to:
   - Implicit or unspoken prerequisites.
   - Data structure constraints.
   - Validation rules.
   - System-specific workflow designs that must be satisfied during execution.

Take these factors into account when defining and categorizing tasks.

The number of tasks per difficulty level will be decided separately. Task design should prioritize coverage and variety of workflows.

## Agent Constraints

The browser-use agent being evaluated can **only interact with the website through the front-end UI**. Specifically, the agent can:

- Click elements
- Type text into inputs
- Scroll the page
- Read visible text and element attributes

The agent **cannot**:

- Execute JavaScript in the page context (e.g., `page.evaluate()`)
- Directly manipulate `localStorage`, `AppState`, or any internal state
- Make HTTP requests to API endpoints

All tasks must be completable through the UI alone.

## Task Schema

Each task is defined as a JSON object:

```json
{
  "id": "task_001",
  "difficulty": "easy | medium | hard",
  "instruction": "Natural language instruction for the agent.",
  "verify": "path/to/verifier.py"
}
```

- **id**: Unique identifier.
- **difficulty**: One of `easy`, `medium`, `hard`.
- **instruction**: The task description given to the agent. Should be unambiguous but should not reveal internal implementation details.
- **verify**: Path to the Python verifier script/function.

# Guide for Programmatic Verifiers

## Privileged Access

You are able to write robust verifiers because you have privileged access to the website implementation. You can:

- Access the backend directly.
- Inspect the database, filesystem, or application state.
- Check internal website state.
- Add new APIs if necessary to simplify verification.

## Understanding the Data Store

The location and nature of the data store is **website-dependent**. Each website implementation determines where its authoritative data lives — it could be a SQL database, a filesystem, a key-value store, browser storage, or something else entirely.

Before writing verifiers, you must determine:

1. **Where does the data live?** (database, files, browser storage, server memory, etc.)
2. **How can a Python verifier access it?** (direct file reads, HTTP API, database queries, etc.)
3. **What bridge infrastructure is needed?** (API endpoints, state sync mechanisms, etc.)

For this specific website, the data store is the browser's `localStorage`, which is not directly accessible from Python. A state synchronization mechanism has been implemented (see below).

## Verification Architecture (This Website)

### State Sync: Browser → Server

The application's `AppState` is the single source of truth. On every mutation, the browser:

1. Writes to `localStorage` (for page-reload persistence)
2. Pushes the full state to the server via `PUT /api/state` (for external access)

This means the server always holds a current copy of the application state.

### Server API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/state` | `GET` | Read the current application state as JSON |
| `/api/state` | `PUT` | Update the server-side state copy (called by browser) |
| `/api/reset` | `POST` | Reset app to seed data (clears browser + server state) |
| `/api/events` | `GET` | SSE stream for pushing commands to the browser |

### Running the Server

```bash
python3 server.py              # default port 8000
python3 server.py --port 9000  # custom port
```

The core logic, data flow, and navigation of system components are described in `./ARCHITECTURE.md`. Make sure you fully understand the system architecture before designing verifiers. You are also encouraged to navigate the codebase inside `./js` and `./css` whenever the description is not clear to you.

## Verifier Interface

All verifiers must implement the following Python function signature:

```python
def verify(server_url: str) -> tuple[bool, str]:
    """
    Verify that a task was completed successfully.

    Args:
        server_url: Base URL of the running server (e.g., 'http://localhost:8000')

    Returns:
        A tuple of (passed, message):
        - passed: True if the task was completed successfully, False otherwise.
        - message: Human-readable explanation of the result.
    """
```

### Example Verifier

```python
import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Check that a group named 'Test Group' exists
    match = [g for g in state['groups'] if g['name'] == 'Test Group']
    if not match:
        return False, "Group 'Test Group' not found."

    group = match[0]
    if group['visibility'] != 'public':
        return False, f"Expected visibility 'public', got '{group['visibility']}'."

    return True, "Group 'Test Group' exists with correct visibility."
```

## Verifier Design Principles

1. **Check internal state, not UI**: Verifiers must validate that the operation genuinely completed by inspecting `AppState` via `GET /api/state`, not by checking what the browser displays.

2. **Prevent shortcuts**: The agent should not be able to pass verification without actually performing the task through the UI. Since the agent cannot call APIs or run JavaScript, and the verifier checks server-side state, this is enforced by design.

3. **Be specific**: Check not just that an entity exists, but that its properties are correct (name, visibility, parent, membership roles, etc.).

4. **Check side effects**: Many operations have cascading effects. For example:
   - Creating a group also creates an Owner membership for the current user.
   - Deleting a group removes its descendants, their projects, and all associated memberships/shares.
   - Transferring a group may reduce its visibility.

   Verifiers should check these side effects where relevant.

5. **Handle ID unpredictability**: New entities get auto-incremented IDs. Verifiers should search by name/path rather than hardcoding IDs.

## State Reset

State reset between tasks is handled by the **evaluation harness**, not by individual verifiers. The harness calls `POST /api/reset` before each task, which:

1. Broadcasts a reset signal to the browser via SSE
2. The browser calls `AppState.resetToSeedData()`, restoring all seed data
3. The browser pushes the seed state back to the server via `PUT /api/state`
4. Clears the server-side state copy

Verifiers should assume they run against a state that started from seed data and was modified only by the agent's actions.
