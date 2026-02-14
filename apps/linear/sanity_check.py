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

# ── Priority constants (matching js/data.js PRIORITIES) ──────

PRIORITIES = {
    "No priority": {"value": 0, "name": "No priority", "label": "No priority", "icon": "—",   "color": "#8b8b8b"},
    "Urgent":      {"value": 1, "name": "Urgent",      "label": "Urgent",      "icon": "!!!", "color": "#f76565"},
    "High":        {"value": 2, "name": "High",         "label": "High",        "icon": "!!",  "color": "#f59e0b"},
    "Medium":      {"value": 3, "name": "Medium",       "label": "Medium",      "icon": "!",   "color": "#3b82f6"},
    "Low":         {"value": 4, "name": "Low",          "label": "Low",         "icon": "↓",   "color": "#68b684"},
}

# ── Name-based lookup helpers ────────────────────────────────

def find_issue(state, identifier=None, title=None):
    if identifier:
        return next(i for i in state["issues"] if i["identifier"] == identifier)
    return next(i for i in state["issues"] if i["title"] == title)

def find_user(state, name):
    return next(u for u in state["users"] if u["name"] == name)

def find_team(state, team_id):
    return next(t for t in state["teams"] if t["id"] == team_id)

def find_label(state, name):
    return next(l for l in state["labels"] if l["name"] == name)

def find_project(state, name):
    return next(p for p in state["projects"] if p["name"] == name)

def find_cycle(state, name):
    return next(c for c in state["cycles"] if c["name"] == name)

# ── Seed state construction via Node ─────────────────────────

def get_seed_state():
    """Evaluate js/data.js through Node and return the seed state dict."""
    data_js_path = os.path.join(SCRIPT_DIR, "js", "data.js")
    with open(data_js_path) as f:
        js_code = f.read()

    js_code += "\nconsole.log(JSON.stringify(buildSeedData()));\n"
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

# ── Per-task solve functions ─────────────────────────────────
# Each function mutates the state dict to match what the verifier expects.

def solve_task_e1(state):
    """Create issue 'Fix login page timeout' in Engineering (team-1), High priority."""
    team = find_team(state, "team-1")
    iid = state["_nextIssueId"]; state["_nextIssueId"] += 1
    team["issueCounter"] += 1
    identifier = f"{team['identifier']}-{team['issueCounter']}"
    state["issues"].append({
        "id": f"issue-{iid}",
        "identifier": identifier,
        "title": "Fix login page timeout",
        "description": "",
        "teamId": "team-1",
        "statusId": "team-1-status-1",
        "priority": PRIORITIES["High"],
        "assigneeId": None,
        "creatorId": state["currentUserId"],
        "labelIds": [],
        "projectId": None,
        "cycleId": None,
        "parentIssueId": None,
        "estimate": None,
        "dueDate": None,
        "sortOrder": 100,
        "createdAt": "2025-02-01T00:00:00Z",
        "updatedAt": "2025-02-01T00:00:00Z",
        "archivedAt": None,
        "deletedAt": None,
    })

def solve_task_e2(state):
    """Change status of ENG-34 to 'Done'."""
    issue = find_issue(state, identifier="ENG-34")
    issue["statusId"] = "team-1-status-5"  # Done

def solve_task_e3(state):
    """Assign ENG-35 to James Chen."""
    issue = find_issue(state, identifier="ENG-35")
    user = find_user(state, "James Chen")
    issue["assigneeId"] = user["id"]

def solve_task_e4(state):
    """Set due date of DES-12 to 2025-03-15."""
    issue = find_issue(state, identifier="DES-12")
    issue["dueDate"] = "2025-03-15"

def solve_task_e5(state):
    """Add 'Bug' label to ENG-36."""
    issue = find_issue(state, identifier="ENG-36")
    bug = find_label(state, "Bug")
    if bug["id"] not in issue["labelIds"]:
        issue["labelIds"].append(bug["id"])

def solve_task_e6(state):
    """Change priority of PRD-10 to Urgent."""
    issue = find_issue(state, identifier="PRD-10")
    issue["priority"] = PRIORITIES["Urgent"]

def solve_task_e7(state):
    """Set estimate of ENG-37 to 5 points."""
    issue = find_issue(state, identifier="ENG-37")
    issue["estimate"] = 5

def solve_task_e8(state):
    """Create workspace label 'Regression' with red color."""
    lid = state["_nextLabelId"]; state["_nextLabelId"] += 1
    state["labels"].append({
        "id": f"label-{lid}",
        "name": "Regression",
        "color": "#ef4444",
        "description": "",
        "scope": "workspace",
        "teamId": None,
        "groupId": None,
        "archived": False,
    })

def solve_task_m1(state):
    """Create issue 'Redesign settings page' in Design, Medium priority, assigned to Emma Wilson, 'Improvement' label."""
    team = find_team(state, "team-2")
    user = find_user(state, "Emma Wilson")
    improvement = find_label(state, "Improvement")
    iid = state["_nextIssueId"]; state["_nextIssueId"] += 1
    team["issueCounter"] += 1
    identifier = f"{team['identifier']}-{team['issueCounter']}"
    state["issues"].append({
        "id": f"issue-{iid}",
        "identifier": identifier,
        "title": "Redesign settings page",
        "description": "",
        "teamId": "team-2",
        "statusId": "team-2-status-1",
        "priority": PRIORITIES["Medium"],
        "assigneeId": user["id"],
        "creatorId": state["currentUserId"],
        "labelIds": [improvement["id"]],
        "projectId": None,
        "cycleId": None,
        "parentIssueId": None,
        "estimate": None,
        "dueDate": None,
        "sortOrder": 100,
        "createdAt": "2025-02-01T00:00:00Z",
        "updatedAt": "2025-02-01T00:00:00Z",
        "archivedAt": None,
        "deletedAt": None,
    })

def solve_task_m2(state):
    """Add sub-issue 'Write unit tests' to ENG-34."""
    parent = find_issue(state, identifier="ENG-34")
    team = find_team(state, parent["teamId"])
    iid = state["_nextIssueId"]; state["_nextIssueId"] += 1
    team["issueCounter"] += 1
    identifier = f"{team['identifier']}-{team['issueCounter']}"
    state["issues"].append({
        "id": f"issue-{iid}",
        "identifier": identifier,
        "title": "Write unit tests",
        "description": "",
        "teamId": parent["teamId"],
        "statusId": f"{parent['teamId']}-status-1",
        "priority": PRIORITIES["No priority"],
        "assigneeId": None,
        "creatorId": state["currentUserId"],
        "labelIds": [],
        "projectId": None,
        "cycleId": None,
        "parentIssueId": parent["id"],
        "estimate": None,
        "dueDate": None,
        "sortOrder": 100,
        "createdAt": "2025-02-01T00:00:00Z",
        "updatedAt": "2025-02-01T00:00:00Z",
        "archivedAt": None,
        "deletedAt": None,
    })

def solve_task_m3(state):
    """Mark ENG-38 as blocking ENG-39."""
    eng38 = find_issue(state, identifier="ENG-38")
    eng39 = find_issue(state, identifier="ENG-39")
    rid = state["_nextRelationId"]; state["_nextRelationId"] += 1
    state["issueRelations"].append({
        "id": f"rel-{rid}",
        "issueId": eng38["id"],
        "relatedIssueId": eng39["id"],
        "type": "blocks",
    })

def solve_task_m4(state):
    """Move issue ENG-40 to Product team."""
    issue = find_issue(state, identifier="ENG-40")
    new_team = find_team(state, "team-3")
    issue["teamId"] = "team-3"
    # Remap status: find matching status name or fall back to first status
    old_status_id = issue["statusId"]
    old_team = find_team(state, "team-1")
    old_status = next((s for s in old_team["statuses"] if s["id"] == old_status_id), None)
    if old_status:
        new_status = next((s for s in new_team["statuses"] if s["name"] == old_status["name"]), None)
        if new_status:
            issue["statusId"] = new_status["id"]
        else:
            # Fall back to first status in same category
            new_status = next((s for s in new_team["statuses"] if s["category"] == old_status["category"]), new_team["statuses"][0])
            issue["statusId"] = new_status["id"]
    # Update identifier
    new_team["issueCounter"] += 1
    issue["identifier"] = f"{new_team['identifier']}-{new_team['issueCounter']}"
    # Clear team-scoped data
    issue["cycleId"] = None
    # Remove team-scoped labels
    team_label_ids = {l["id"] for l in state["labels"] if l.get("scope") == "team" and l.get("teamId") == "team-1"}
    issue["labelIds"] = [lid for lid in issue.get("labelIds", []) if lid not in team_label_ids]

def solve_task_m5(state):
    """Create label group 'Severity' and label 'Critical' (red) in that group."""
    gid = state["_nextLabelGroupId"]; state["_nextLabelGroupId"] += 1
    group_id = f"lg-{gid}"
    state["labelGroups"].append({
        "id": group_id,
        "name": "Severity",
        "scope": "workspace",
        "teamId": None,
        "color": "#ef4444",
    })
    lid = state["_nextLabelId"]; state["_nextLabelId"] += 1
    state["labels"].append({
        "id": f"label-{lid}",
        "name": "Critical",
        "color": "#ef4444",
        "description": "",
        "scope": "workspace",
        "teamId": None,
        "groupId": group_id,
        "archived": False,
    })

def solve_task_m6(state):
    """Add comment to DES-14: 'The mockups look great, approved for development.'"""
    issue = find_issue(state, identifier="DES-14")
    cid = state["_nextCommentId"]; state["_nextCommentId"] += 1
    state["comments"].append({
        "id": f"comment-{cid}",
        "issueId": issue["id"],
        "body": "The mockups look great, approved for development.",
        "userId": state["currentUserId"],
        "parentCommentId": None,
        "resolved": False,
        "createdAt": "2025-02-01T00:00:00Z",
        "updatedAt": "2025-02-01T00:00:00Z",
    })

def solve_task_m7(state):
    """Enable estimates for Design team, set scale to T-Shirt."""
    team = find_team(state, "team-2")
    team["settings"]["estimatesEnabled"] = True
    team["settings"]["estimateScale"] = "T-Shirt"

def solve_task_m8(state):
    """Delete issue CS-20 (set deletedAt)."""
    issue = find_issue(state, identifier="CS-20")
    issue["deletedAt"] = "2025-02-01T00:00:00Z"

def solve_task_h1(state):
    """Create 'Implement OAuth2 authentication' (High, ENG) + 2 sub-issues."""
    team = find_team(state, "team-1")

    # Parent issue
    pid = state["_nextIssueId"]; state["_nextIssueId"] += 1
    team["issueCounter"] += 1
    parent_id = f"issue-{pid}"
    state["issues"].append({
        "id": parent_id,
        "identifier": f"{team['identifier']}-{team['issueCounter']}",
        "title": "Implement OAuth2 authentication",
        "description": "",
        "teamId": "team-1",
        "statusId": "team-1-status-1",
        "priority": PRIORITIES["High"],
        "assigneeId": None,
        "creatorId": state["currentUserId"],
        "labelIds": [],
        "projectId": None,
        "cycleId": None,
        "parentIssueId": None,
        "estimate": None,
        "dueDate": None,
        "sortOrder": 100,
        "createdAt": "2025-02-01T00:00:00Z",
        "updatedAt": "2025-02-01T00:00:00Z",
        "archivedAt": None,
        "deletedAt": None,
    })

    # Sub-issue 1
    sid1 = state["_nextIssueId"]; state["_nextIssueId"] += 1
    team["issueCounter"] += 1
    state["issues"].append({
        "id": f"issue-{sid1}",
        "identifier": f"{team['identifier']}-{team['issueCounter']}",
        "title": "Set up OAuth2 provider",
        "description": "",
        "teamId": "team-1",
        "statusId": "team-1-status-1",
        "priority": PRIORITIES["No priority"],
        "assigneeId": None,
        "creatorId": state["currentUserId"],
        "labelIds": [],
        "projectId": None,
        "cycleId": None,
        "parentIssueId": parent_id,
        "estimate": None,
        "dueDate": None,
        "sortOrder": 101,
        "createdAt": "2025-02-01T00:00:00Z",
        "updatedAt": "2025-02-01T00:00:00Z",
        "archivedAt": None,
        "deletedAt": None,
    })

    # Sub-issue 2
    sid2 = state["_nextIssueId"]; state["_nextIssueId"] += 1
    team["issueCounter"] += 1
    state["issues"].append({
        "id": f"issue-{sid2}",
        "identifier": f"{team['identifier']}-{team['issueCounter']}",
        "title": "Implement token refresh flow",
        "description": "",
        "teamId": "team-1",
        "statusId": "team-1-status-1",
        "priority": PRIORITIES["No priority"],
        "assigneeId": None,
        "creatorId": state["currentUserId"],
        "labelIds": [],
        "projectId": None,
        "cycleId": None,
        "parentIssueId": parent_id,
        "estimate": None,
        "dueDate": None,
        "sortOrder": 102,
        "createdAt": "2025-02-01T00:00:00Z",
        "updatedAt": "2025-02-01T00:00:00Z",
        "archivedAt": None,
        "deletedAt": None,
    })

def solve_task_h2(state):
    """Create label group 'Environment' + 'Staging'(orange) + 'Production'(red), apply Production to ENG-34."""
    gid = state["_nextLabelGroupId"]; state["_nextLabelGroupId"] += 1
    group_id = f"lg-{gid}"
    state["labelGroups"].append({
        "id": group_id,
        "name": "Environment",
        "scope": "workspace",
        "teamId": None,
        "color": "#6366f1",
    })

    # Staging label (orange)
    lid1 = state["_nextLabelId"]; state["_nextLabelId"] += 1
    staging_id = f"label-{lid1}"
    state["labels"].append({
        "id": staging_id,
        "name": "Staging",
        "color": "#f97316",
        "description": "",
        "scope": "workspace",
        "teamId": None,
        "groupId": group_id,
        "archived": False,
    })

    # Production label (red)
    lid2 = state["_nextLabelId"]; state["_nextLabelId"] += 1
    prod_id = f"label-{lid2}"
    state["labels"].append({
        "id": prod_id,
        "name": "Production",
        "color": "#ef4444",
        "description": "",
        "scope": "workspace",
        "teamId": None,
        "groupId": group_id,
        "archived": False,
    })

    # Apply Production to ENG-34
    eng34 = find_issue(state, identifier="ENG-34")
    if prod_id not in eng34["labelIds"]:
        eng34["labelIds"].append(prod_id)

def solve_task_h3(state):
    """Create 'Database migration script' in ENG, assign Priya, Urgent, Backend label, comment."""
    team = find_team(state, "team-1")
    priya = find_user(state, "Priya Sharma")
    backend = find_label(state, "Backend")

    iid = state["_nextIssueId"]; state["_nextIssueId"] += 1
    team["issueCounter"] += 1
    issue_id = f"issue-{iid}"
    state["issues"].append({
        "id": issue_id,
        "identifier": f"{team['identifier']}-{team['issueCounter']}",
        "title": "Database migration script",
        "description": "",
        "teamId": "team-1",
        "statusId": "team-1-status-1",
        "priority": PRIORITIES["Urgent"],
        "assigneeId": priya["id"],
        "creatorId": state["currentUserId"],
        "labelIds": [backend["id"]],
        "projectId": None,
        "cycleId": None,
        "parentIssueId": None,
        "estimate": None,
        "dueDate": None,
        "sortOrder": 100,
        "createdAt": "2025-02-01T00:00:00Z",
        "updatedAt": "2025-02-01T00:00:00Z",
        "archivedAt": None,
        "deletedAt": None,
    })

    # Add comment
    cid = state["_nextCommentId"]; state["_nextCommentId"] += 1
    state["comments"].append({
        "id": f"comment-{cid}",
        "issueId": issue_id,
        "body": "Critical for Q1 release",
        "userId": state["currentUserId"],
        "parentCommentId": None,
        "resolved": False,
        "createdAt": "2025-02-01T00:00:00Z",
        "updatedAt": "2025-02-01T00:00:00Z",
    })

def solve_task_h4(state):
    """Create template 'Performance Issue' (High), then create issue from it."""
    # Create template
    tid = state["_nextTemplateId"]; state["_nextTemplateId"] += 1
    state["templates"].append({
        "id": f"template-{tid}",
        "name": "Performance Issue",
        "description": "Template for performance issues",
        "teamId": None,
        "defaultPriority": PRIORITIES["High"],
        "defaultLabelIds": [],
        "defaultEstimate": None,
        "templateDescription": "",
        "createdAt": "2025-02-01T00:00:00Z",
    })

    # Create issue from template
    team = find_team(state, "team-1")
    iid = state["_nextIssueId"]; state["_nextIssueId"] += 1
    team["issueCounter"] += 1
    state["issues"].append({
        "id": f"issue-{iid}",
        "identifier": f"{team['identifier']}-{team['issueCounter']}",
        "title": "Optimize API response times",
        "description": "",
        "teamId": "team-1",
        "statusId": "team-1-status-1",
        "priority": PRIORITIES["High"],
        "assigneeId": None,
        "creatorId": state["currentUserId"],
        "labelIds": [],
        "projectId": None,
        "cycleId": None,
        "parentIssueId": None,
        "estimate": None,
        "dueDate": None,
        "sortOrder": 100,
        "createdAt": "2025-02-01T00:00:00Z",
        "updatedAt": "2025-02-01T00:00:00Z",
        "archivedAt": None,
        "deletedAt": None,
    })

def solve_task_h5(state):
    """Create 'Upgrade database driver' (High, ENG), mark it blocking ENG-38, add ENG-39 as related."""
    team = find_team(state, "team-1")
    eng38 = find_issue(state, identifier="ENG-38")
    eng39 = find_issue(state, identifier="ENG-39")

    iid = state["_nextIssueId"]; state["_nextIssueId"] += 1
    team["issueCounter"] += 1
    issue_id = f"issue-{iid}"
    state["issues"].append({
        "id": issue_id,
        "identifier": f"{team['identifier']}-{team['issueCounter']}",
        "title": "Upgrade database driver",
        "description": "",
        "teamId": "team-1",
        "statusId": "team-1-status-1",
        "priority": PRIORITIES["High"],
        "assigneeId": None,
        "creatorId": state["currentUserId"],
        "labelIds": [],
        "projectId": None,
        "cycleId": None,
        "parentIssueId": None,
        "estimate": None,
        "dueDate": None,
        "sortOrder": 100,
        "createdAt": "2025-02-01T00:00:00Z",
        "updatedAt": "2025-02-01T00:00:00Z",
        "archivedAt": None,
        "deletedAt": None,
    })

    # Blocks ENG-38
    rid1 = state["_nextRelationId"]; state["_nextRelationId"] += 1
    state["issueRelations"].append({
        "id": f"rel-{rid1}",
        "issueId": issue_id,
        "relatedIssueId": eng38["id"],
        "type": "blocks",
    })

    # Related to ENG-39
    rid2 = state["_nextRelationId"]; state["_nextRelationId"] += 1
    state["issueRelations"].append({
        "id": f"rel-{rid2}",
        "issueId": issue_id,
        "relatedIssueId": eng39["id"],
        "type": "related",
    })

def solve_task_h6(state):
    """Create 'Implement caching layer' (Medium, ENG), assign Yuki, project Q1 Launch, cycle Sprint 13."""
    team = find_team(state, "team-1")
    yuki = find_user(state, "Yuki Tanaka")
    project = find_project(state, "Q1 Launch")
    cycle = find_cycle(state, "Sprint 13")

    iid = state["_nextIssueId"]; state["_nextIssueId"] += 1
    team["issueCounter"] += 1
    state["issues"].append({
        "id": f"issue-{iid}",
        "identifier": f"{team['identifier']}-{team['issueCounter']}",
        "title": "Implement caching layer",
        "description": "",
        "teamId": "team-1",
        "statusId": "team-1-status-1",
        "priority": PRIORITIES["Medium"],
        "assigneeId": yuki["id"],
        "creatorId": state["currentUserId"],
        "labelIds": [],
        "projectId": project["id"],
        "cycleId": cycle["id"],
        "parentIssueId": None,
        "estimate": None,
        "dueDate": None,
        "sortOrder": 100,
        "createdAt": "2025-02-01T00:00:00Z",
        "updatedAt": "2025-02-01T00:00:00Z",
        "archivedAt": None,
        "deletedAt": None,
    })

def solve_task_h7(state):
    """Delete CS-22 then restore it (deletedAt null, updatedAt changed from seed)."""
    issue = find_issue(state, identifier="CS-22")
    # After delete+restore, deletedAt should be null but updatedAt should differ from seed
    issue["deletedAt"] = None
    issue["updatedAt"] = "2025-02-01T00:00:00Z"

def solve_task_h8(state):
    """Create customer 'NovaTech', CS issue 'NovaTech onboarding setup', linked request."""
    # Create customer
    cust_id = state["_nextCustomerId"]; state["_nextCustomerId"] += 1
    customer_id = f"customer-{cust_id}"
    state["customers"].append({
        "id": customer_id,
        "name": "NovaTech",
        "domain": "novatech.io",
        "tier": "Business",
        "contactName": "",
        "contactEmail": "",
        "revenue": 0,
        "createdAt": "2025-02-01T00:00:00Z",
    })

    # Create issue in Customer Success
    team = find_team(state, "team-4")
    iid = state["_nextIssueId"]; state["_nextIssueId"] += 1
    team["issueCounter"] += 1
    issue_id = f"issue-{iid}"
    state["issues"].append({
        "id": issue_id,
        "identifier": f"{team['identifier']}-{team['issueCounter']}",
        "title": "NovaTech onboarding setup",
        "description": "",
        "teamId": "team-4",
        "statusId": "team-4-status-1",
        "priority": PRIORITIES["No priority"],
        "assigneeId": None,
        "creatorId": state["currentUserId"],
        "labelIds": [],
        "projectId": None,
        "cycleId": None,
        "parentIssueId": None,
        "estimate": None,
        "dueDate": None,
        "sortOrder": 100,
        "createdAt": "2025-02-01T00:00:00Z",
        "updatedAt": "2025-02-01T00:00:00Z",
        "archivedAt": None,
        "deletedAt": None,
    })

    # Create customer request linking them
    crid = state["_nextCustomerRequestId"]; state["_nextCustomerRequestId"] += 1
    state["customerRequests"].append({
        "id": f"cr-{crid}",
        "customerId": customer_id,
        "issueId": issue_id,
        "title": "NovaTech onboarding setup",
        "description": "",
        "priority": "medium",
        "createdAt": "2025-02-01T00:00:00Z",
    })

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

# ── Server lifecycle ─────────────────────────────────────────

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

# ── Verifier loading ─────────────────────────────────────────

def load_verifier(task_id):
    path = os.path.join(TASKS_DIR, f"{task_id}.py")
    spec = importlib.util.spec_from_file_location(task_id, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.verify

# ── Worker: run a batch of tasks on one server ───────────────

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

# ── Main ─────────────────────────────────────────────────────

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
    print("Loading seed state via Node...")
    seed_state = get_seed_state()
    print(f"Seed loaded: {len(seed_state['issues'])} issues, "
          f"{len(seed_state['teams'])} teams, "
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
