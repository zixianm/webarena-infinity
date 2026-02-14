#!/usr/bin/env python3
"""
Verifier sanity check — for each task, directly apply the expected state
changes via the API, run the verifier, and assert it passes.

Usage:
    python3 sanity_check.py                      # Run all 24 tasks sequentially
    python3 sanity_check.py --workers 4           # Run with 4 parallel server workers
    python3 sanity_check.py --task-id task_e1     # Run a single task
    python3 sanity_check.py --port 9000           # Custom base port
"""

import argparse
import copy
import importlib.util
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.join(SCRIPT_DIR, "tasks")

# ── Roles (matching js/data.js ROLES) ─────────────────────────

ROLES = {
    "Guest":      {"id": 10, "name": "Guest",      "label": "Guest",      "level": 10},
    "Reporter":   {"id": 20, "name": "Reporter",    "label": "Reporter",   "level": 20},
    "Developer":  {"id": 30, "name": "Developer",   "label": "Developer",  "level": 30},
    "Maintainer": {"id": 40, "name": "Maintainer",  "label": "Maintainer", "level": 40},
    "Owner":      {"id": 50, "name": "Owner",       "label": "Owner",      "level": 50},
}

# ── Name-based lookup helpers ──────────────────────────────────

def find_user(state, name):
    return next(u for u in state["users"] if u["name"] == name)

def find_group(state, name):
    return next(g for g in state["groups"] if g["name"] == name)

def find_project(state, name):
    return next(p for p in state["projects"] if p["name"] == name)

def sync_current_user_to_users(state):
    """Keep users[0] (currentUser entry) in sync with currentUser."""
    cu = state["currentUser"]
    for i, u in enumerate(state["users"]):
        if u["id"] == cu["id"]:
            state["users"][i] = copy.deepcopy(cu)
            break

# ── Seed state construction via Node ───────────────────────────

def get_seed_state():
    """Evaluate js/data.js through Node and return the seed state dict."""
    data_js_path = os.path.join(SCRIPT_DIR, "js", "data.js")
    with open(data_js_path) as f:
        js_code = f.read()

    js_code += """
console.log(JSON.stringify({
    _seedVersion: SEED_DATA_VERSION,
    currentUser: CURRENT_USER,
    users: USERS,
    organizations: ORGANIZATIONS,
    groups: GROUPS,
    projects: PROJECTS,
    groupMemberships: GROUP_MEMBERSHIPS,
    projectMemberships: PROJECT_MEMBERSHIPS,
    groupShares: GROUP_SHARES,
    projectShares: PROJECT_SHARES,
    _nextUserId: 13,
    _nextGroupId: 15,
    _nextProjectId: 21,
    _nextOrgId: 3
}));
"""
    result = subprocess.run(
        ["node", "-"],
        input=js_code,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Failed to evaluate seed data: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout.strip())

# ── Per-task solve functions ───────────────────────────────────
# Each function mutates the state dict to match what the verifier expects.

def solve_task_e1(state):
    """Create group 'DevOps Team' (public), Owner membership for currentUser."""
    gid = state["_nextGroupId"]; state["_nextGroupId"] += 1
    state["groups"].append({
        "id": gid, "name": "DevOps Team", "path": "devops-team",
        "fullPath": "acme-corp/devops-team", "description": "",
        "parentId": None, "organizationId": 1, "visibility": "public",
        "avatar": None, "avatarColor": "#6366f1",
        "createdAt": "2025-01-01T00:00:00Z", "updatedAt": "2025-01-01T00:00:00Z",
        "archived": False, "userCap": None, "preventInvitations": False,
        "disableMentions": False, "preventSharingOutsideHierarchy": False,
        "defaultBranchProtection": "fully_protected",
        "subgroupCreationLevel": "maintainer", "projectCreationLevel": "developer",
        "requireTwoFactor": False, "readme": ""
    })
    state["groupMemberships"].append({
        "groupId": gid, "userId": state["currentUser"]["id"],
        "role": ROLES["Owner"], "membershipType": "direct",
        "source": None, "expiresAt": None,
        "addedBy": state["currentUser"]["id"], "addedAt": "2025-01-01T00:00:00Z"
    })

def solve_task_e2(state):
    """Remove project 'legacy-monolith' and clean up references."""
    proj = find_project(state, "legacy-monolith")
    pid = proj["id"]
    state["projects"] = [p for p in state["projects"] if p["id"] != pid]
    state["projectMemberships"] = [
        m for m in state["projectMemberships"] if m["projectId"] != pid
    ]
    state["projectShares"] = [
        s for s in state["projectShares"] if s["targetProjectId"] != pid
    ]

def solve_task_e3(state):
    """Set bio on currentUser and sync to users array."""
    state["currentUser"]["bio"] = "Full-stack developer with 10 years of experience"
    sync_current_user_to_users(state)

def solve_task_e4(state):
    """Append secondary email."""
    state["currentUser"]["secondaryEmails"].append("alex.backup@gmail.com")

def solve_task_e5(state):
    """Disable 2FA on currentUser and sync."""
    state["currentUser"]["twoFactorEnabled"] = False
    sync_current_user_to_users(state)

def solve_task_e6(state):
    """Unarchive the 'Archived Projects' group."""
    find_group(state, "Archived Projects")["archived"] = False

def solve_task_e7(state):
    """Remove 'alex.personal@email.com' from secondary emails."""
    emails = state["currentUser"]["secondaryEmails"]
    state["currentUser"]["secondaryEmails"] = [
        e for e in emails if e != "alex.personal@email.com"
    ]

def solve_task_e8(state):
    """Set status message='On vacation', busy=true."""
    state["currentUser"]["status"]["message"] = "On vacation"
    state["currentUser"]["status"]["busy"] = True

def solve_task_m1(state):
    """Create project 'monitoring-service' in Observability group."""
    obs = find_group(state, "Observability")
    pid = state["_nextProjectId"]; state["_nextProjectId"] += 1
    state["projects"].append({
        "id": pid, "name": "monitoring-service", "path": "monitoring-service",
        "fullPath": obs["fullPath"] + "/monitoring-service",
        "description": "", "groupId": obs["id"], "visibility": "private",
        "createdAt": "2025-01-01T00:00:00Z", "updatedAt": "2025-01-01T00:00:00Z",
        "stars": 0, "forks": 0, "defaultBranch": "main",
        "topics": [], "archived": False, "empty": True
    })

def solve_task_m2(state):
    """Add Emma Wilson as Developer to CI/CD group."""
    emma = find_user(state, "Emma Wilson")
    cicd = find_group(state, "CI/CD")
    state["groupMemberships"].append({
        "groupId": cicd["id"], "userId": emma["id"],
        "role": ROLES["Developer"], "membershipType": "direct",
        "source": None, "expiresAt": None,
        "addedBy": state["currentUser"]["id"], "addedAt": "2025-01-01T00:00:00Z"
    })

def solve_task_m3(state):
    """Change James Chen's role in Terraform Modules to Owner."""
    james = find_user(state, "James Chen")
    tf = find_group(state, "Terraform Modules")
    for m in state["groupMemberships"]:
        if m["groupId"] == tf["id"] and m["userId"] == james["id"]:
            m["role"] = ROLES["Owner"]
            break

def solve_task_m4(state):
    """Add groupShare: Open Source → Product Development, Reporter."""
    oss = find_group(state, "Open Source")
    pd = find_group(state, "Product Development")
    state["groupShares"].append({
        "sourceGroupId": oss["id"], "targetGroupId": pd["id"],
        "maxRole": ROLES["Reporter"], "expiresAt": None,
        "addedBy": state["currentUser"]["id"], "addedAt": "2025-01-01T00:00:00Z"
    })

def solve_task_m5(state):
    """Remove Maria Rodriguez's direct membership from Product Development."""
    maria = find_user(state, "Maria Rodriguez")
    pd = find_group(state, "Product Development")
    state["groupMemberships"] = [
        m for m in state["groupMemberships"]
        if not (m["groupId"] == pd["id"] and m["userId"] == maria["id"]
                and m.get("membershipType") == "direct")
    ]

def solve_task_m6(state):
    """Create subgroup 'Performance Testing' under Web Application with Owner membership."""
    wa = find_group(state, "Web Application")
    gid = state["_nextGroupId"]; state["_nextGroupId"] += 1
    state["groups"].append({
        "id": gid, "name": "Performance Testing", "path": "performance-testing",
        "fullPath": wa["fullPath"] + "/performance-testing", "description": "",
        "parentId": wa["id"], "organizationId": wa["organizationId"],
        "visibility": wa["visibility"],
        "avatar": None, "avatarColor": "#6366f1",
        "createdAt": "2025-01-01T00:00:00Z", "updatedAt": "2025-01-01T00:00:00Z",
        "archived": False, "userCap": None, "preventInvitations": False,
        "disableMentions": False, "preventSharingOutsideHierarchy": False,
        "defaultBranchProtection": "fully_protected",
        "subgroupCreationLevel": "maintainer", "projectCreationLevel": "developer",
        "requireTwoFactor": False, "readme": ""
    })
    state["groupMemberships"].append({
        "groupId": gid, "userId": state["currentUser"]["id"],
        "role": ROLES["Owner"], "membershipType": "direct",
        "source": None, "expiresAt": None,
        "addedBy": state["currentUser"]["id"], "addedAt": "2025-01-01T00:00:00Z"
    })

def solve_task_m7(state):
    """Update Platform Engineering: description + requireTwoFactor."""
    pe = find_group(state, "Platform Engineering")
    pe["description"] = "Core infrastructure and platform services"
    pe["requireTwoFactor"] = True

def solve_task_m8(state):
    """Remove groupShare: Security → Platform Engineering."""
    sec = find_group(state, "Security")
    pe = find_group(state, "Platform Engineering")
    state["groupShares"] = [
        s for s in state["groupShares"]
        if not (s["sourceGroupId"] == sec["id"] and s["targetGroupId"] == pe["id"])
    ]

def solve_task_h1(state):
    """Create 'community-tools' in Open Source (public), share with Product Development (Developer)."""
    oss = find_group(state, "Open Source")
    pd = find_group(state, "Product Development")
    pid = state["_nextProjectId"]; state["_nextProjectId"] += 1
    state["projects"].append({
        "id": pid, "name": "community-tools", "path": "community-tools",
        "fullPath": oss["fullPath"] + "/community-tools",
        "description": "", "groupId": oss["id"], "visibility": "public",
        "createdAt": "2025-01-01T00:00:00Z", "updatedAt": "2025-01-01T00:00:00Z",
        "stars": 0, "forks": 0, "defaultBranch": "main",
        "topics": [], "archived": False, "empty": True
    })
    state["projectShares"].append({
        "sourceGroupId": pd["id"], "targetProjectId": pid,
        "maxRole": ROLES["Developer"], "expiresAt": None,
        "addedBy": state["currentUser"]["id"], "addedAt": "2025-01-01T00:00:00Z"
    })

def solve_task_h2(state):
    """Create subgroup 'Threat Intelligence' under Security, add Priya Sharma as Developer."""
    sec = find_group(state, "Security")
    priya = find_user(state, "Priya Sharma")
    gid = state["_nextGroupId"]; state["_nextGroupId"] += 1
    state["groups"].append({
        "id": gid, "name": "Threat Intelligence", "path": "threat-intelligence",
        "fullPath": sec["fullPath"] + "/threat-intelligence", "description": "",
        "parentId": sec["id"], "organizationId": sec["organizationId"],
        "visibility": sec["visibility"],
        "avatar": None, "avatarColor": "#6366f1",
        "createdAt": "2025-01-01T00:00:00Z", "updatedAt": "2025-01-01T00:00:00Z",
        "archived": False, "userCap": None, "preventInvitations": False,
        "disableMentions": False, "preventSharingOutsideHierarchy": False,
        "defaultBranchProtection": "fully_protected",
        "subgroupCreationLevel": "maintainer", "projectCreationLevel": "developer",
        "requireTwoFactor": False, "readme": ""
    })
    state["groupMemberships"].append({
        "groupId": gid, "userId": priya["id"],
        "role": ROLES["Developer"], "membershipType": "direct",
        "source": None, "expiresAt": None,
        "addedBy": state["currentUser"]["id"], "addedAt": "2025-01-01T00:00:00Z"
    })

def solve_task_h3(state):
    """Remove Liam O'Shea from web-frontend, add Sofia Petrov as Developer."""
    proj = find_project(state, "web-frontend")
    liam = find_user(state, "Liam O'Shea")
    sofia = find_user(state, "Sofia Petrov")
    state["projectMemberships"] = [
        m for m in state["projectMemberships"]
        if not (m["projectId"] == proj["id"] and m["userId"] == liam["id"])
    ]
    state["projectMemberships"].append({
        "projectId": proj["id"], "userId": sofia["id"],
        "role": ROLES["Developer"], "membershipType": "direct",
        "expiresAt": None, "addedBy": state["currentUser"]["id"],
        "addedAt": "2025-01-01T00:00:00Z"
    })

def solve_task_h4(state):
    """Update currentUser: username='alex.m', name='Alex M.', sync to users array."""
    state["currentUser"]["username"] = "alex.m"
    state["currentUser"]["name"] = "Alex M."
    sync_current_user_to_users(state)

def solve_task_h5(state):
    """Add Omar Hassan as Maintainer to Terraform Modules, expires 2027-12-31."""
    omar = find_user(state, "Omar Hassan")
    tf = find_group(state, "Terraform Modules")
    state["groupMemberships"].append({
        "groupId": tf["id"], "userId": omar["id"],
        "role": ROLES["Maintainer"], "membershipType": "direct",
        "source": None, "expiresAt": "2027-12-31T00:00:00Z",
        "addedBy": state["currentUser"]["id"], "addedAt": "2025-01-01T00:00:00Z"
    })

def solve_task_h6(state):
    """Update Observability: name, subgroupCreationLevel, projectCreationLevel, disableMentions."""
    obs = find_group(state, "Observability")
    obs["name"] = "Monitoring & Observability"
    obs["subgroupCreationLevel"] = "owner"
    obs["projectCreationLevel"] = "noone"
    obs["disableMentions"] = True

def solve_task_h7(state):
    """Add projectShare: Analytics Platform → design-system, Reporter, expires 2027-06-15."""
    ap = find_group(state, "Analytics Platform")
    ds = find_project(state, "design-system")
    state["projectShares"].append({
        "sourceGroupId": ap["id"], "targetProjectId": ds["id"],
        "maxRole": ROLES["Reporter"],
        "expiresAt": "2027-06-15T00:00:00Z",
        "addedBy": state["currentUser"]["id"], "addedAt": "2025-01-01T00:00:00Z"
    })

def solve_task_h8(state):
    """Update web-frontend: name, description, topics, visibility."""
    proj = find_project(state, "web-frontend")
    proj["name"] = "web-app-frontend"
    proj["description"] = "Main customer-facing web application"
    proj["topics"] = ["react", "vue", "frontend"]
    proj["visibility"] = "private"

SOLVERS = {
    "task_e1": solve_task_e1, "task_e2": solve_task_e2,
    "task_e3": solve_task_e3, "task_e4": solve_task_e4,
    "task_e5": solve_task_e5, "task_e6": solve_task_e6,
    "task_e7": solve_task_e7, "task_e8": solve_task_e8,
    "task_m1": solve_task_m1, "task_m2": solve_task_m2,
    "task_m3": solve_task_m3, "task_m4": solve_task_m4,
    "task_m5": solve_task_m5, "task_m6": solve_task_m6,
    "task_m7": solve_task_m7, "task_m8": solve_task_m8,
    "task_h1": solve_task_h1, "task_h2": solve_task_h2,
    "task_h3": solve_task_h3, "task_h4": solve_task_h4,
    "task_h5": solve_task_h5, "task_h6": solve_task_h6,
    "task_h7": solve_task_h7, "task_h8": solve_task_h8,
}

# ── Server lifecycle ───────────────────────────────────────────

def start_server(port):
    return subprocess.Popen(
        [sys.executable, "server.py", "--port", str(port)],
        cwd=SCRIPT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

def wait_for_server(port, timeout=10):
    url = f"http://localhost:{port}/"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                return True
        except requests.ConnectionError:
            pass
        time.sleep(0.3)
    return False

def stop_server(proc):
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

# ── Verifier loading ──────────────────────────────────────────

def load_verifier(task_id):
    path = os.path.join(TASKS_DIR, f"{task_id}.py")
    spec = importlib.util.spec_from_file_location(task_id, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.verify

# ── Worker: run a batch of tasks on one server ────────────────

def run_tasks(task_ids, port, seed_state):
    """Start a server on *port*, run each task, return list of (task_id, passed, message)."""
    results = []
    proc = start_server(port)
    try:
        if not wait_for_server(port):
            for tid in task_ids:
                results.append((tid, False, "Server failed to start"))
            return results

        base = f"http://localhost:{port}"

        # First PUT sets _seed_state on the server
        r = requests.put(f"{base}/api/state", json=seed_state, timeout=5)
        if r.status_code != 200:
            for tid in task_ids:
                results.append((tid, False, "Failed to seed server state"))
            return results

        for tid in task_ids:
            try:
                # Reset to seed
                requests.post(f"{base}/api/reset", timeout=5)

                # Fetch clean seed state
                state = requests.get(f"{base}/api/state", timeout=5).json()

                # Apply expected changes
                SOLVERS[tid](state)

                # Push solved state
                requests.put(f"{base}/api/state", json=state, timeout=5)

                # Run the verifier
                verify = load_verifier(tid)
                passed, message = verify(base)
                results.append((tid, passed, message))
            except Exception as e:
                results.append((tid, False, f"Error: {e}"))
    finally:
        stop_server(proc)
    return results

# ── Main ───────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Verifier sanity check")
    parser.add_argument("--workers", type=int, default=1,
                        help="Number of parallel server workers (default: 1)")
    parser.add_argument("--task-id", type=str,
                        help="Run a single task (e.g. task_e1)")
    parser.add_argument("--port", type=int, default=18000,
                        help="Base port for servers (default: 18000)")
    args = parser.parse_args()

    # Determine which tasks to run
    if args.task_id:
        task_ids = [args.task_id]
    else:
        with open(os.path.join(SCRIPT_DIR, "tasks.json")) as f:
            task_ids = [t["id"] for t in json.load(f)]

    for tid in task_ids:
        if tid not in SOLVERS:
            print(f"Unknown task: {tid}", file=sys.stderr)
            sys.exit(1)

    # Build seed state from js/data.js
    print("Loading seed state via Node…")
    seed_state = get_seed_state()
    print(f"Seed loaded: {len(seed_state['groups'])} groups, "
          f"{len(seed_state['projects'])} projects, "
          f"{len(seed_state['users'])} users")

    num_workers = min(args.workers, len(task_ids))
    all_results = []

    if num_workers <= 1:
        # Sequential — single server
        all_results = run_tasks(task_ids, args.port, seed_state)
    else:
        # Parallel — one server per worker, tasks round-robin partitioned
        chunks = [[] for _ in range(num_workers)]
        for i, tid in enumerate(task_ids):
            chunks[i % num_workers].append(tid)

        with ThreadPoolExecutor(max_workers=num_workers) as pool:
            futures = {
                pool.submit(run_tasks, chunk, args.port + i, seed_state): i
                for i, chunk in enumerate(chunks) if chunk
            }
            for f in as_completed(futures):
                all_results.extend(f.result())

    # Sort by original task order
    order = {tid: i for i, tid in enumerate(task_ids)}
    all_results.sort(key=lambda r: order.get(r[0], 999))

    # Print results
    print()
    passed_count = 0
    failed = []
    for tid, passed, message in all_results:
        status = "PASS" if passed else "FAIL"
        if passed:
            passed_count += 1
        else:
            failed.append(tid)
        print(f"  {status}  {tid:12s}  {message}")

    total = len(all_results)
    print(f"\n{passed_count}/{total} passed")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("All verifiers passed!")

if __name__ == "__main__":
    main()
