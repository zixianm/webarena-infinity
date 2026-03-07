#!/usr/bin/env python3
"""
Sanity check for Superhuman Mail function-test tasks.

For each task, directly applies the expected end-state (bypassing the agent),
then runs the verifier and asserts it passes.

Usage:
    python3 sanity_check_function.py                     # All tasks, sequential
    python3 sanity_check_function.py --workers N          # N parallel environments
    python3 sanity_check_function.py --task-id task_5     # Single task
    python3 sanity_check_function.py --port 9000          # Custom base port
"""
import argparse
import importlib.util
import json
import os
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

APP_DIR = Path(__file__).resolve().parent
TASKS_FILE = APP_DIR / "function-tasks.json"

# JS snippet to evaluate data.js and emit the seed state as JSON
_SEED_STATE_JS = """
const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync(process.argv[1], 'utf8');
vm.runInThisContext(code);

const state = {
    _seedVersion: SEED_DATA_VERSION,
    emails: JSON.parse(JSON.stringify(EMAILS)),
    contacts: JSON.parse(JSON.stringify(CONTACTS)),
    labels: JSON.parse(JSON.stringify(LABELS)),
    autoLabels: JSON.parse(JSON.stringify(AUTO_LABELS)),
    splits: JSON.parse(JSON.stringify(SPLITS)),
    snippets: JSON.parse(JSON.stringify(SNIPPETS)),
    calendarEvents: JSON.parse(JSON.stringify(CALENDAR_EVENTS)),
    settings: JSON.parse(JSON.stringify(SETTINGS)),
    currentUser: JSON.parse(JSON.stringify(CURRENT_USER)),
    recentOpens: JSON.parse(JSON.stringify(RECENT_OPENS)),
    bookingPages: JSON.parse(JSON.stringify(BOOKING_PAGES)),
    _nextEmailId: EMAILS.length > 0 ? Math.max(...EMAILS.map(e => e.id)) + 1 : 200,
    _nextLabelId: 30,
    _nextSnippetId: 30,
    _nextEventId: 30,
    _nextAutoLabelId: 20,
    _nextSplitId: 20,
    _nextBookingPageId: 10,
};
process.stdout.write(JSON.stringify(state));
"""


# -- helpers ------------------------------------------------------------------

def find_email_by_subject(state, subject):
    for e in state["emails"]:
        if e["subject"] == subject:
            return e
    raise ValueError(f"Email not found: subject={subject!r}")


def find_email_by_subject_and_sender(state, subject, sender_email):
    for e in state["emails"]:
        if e["subject"] == subject and e["from"]["email"] == sender_email:
            return e
    raise ValueError(f"Email not found: subject={subject!r}, from={sender_email!r}")


def find_email_by_subject_contains(state, substring):
    for e in state["emails"]:
        if substring in e["subject"]:
            return e
    raise ValueError(f"Email not found containing: {substring!r}")


def find_label_by_name(state, name):
    for l in state["labels"]:
        if l["name"] == name:
            return l
    raise ValueError(f"Label not found: {name!r}")


def find_snippet_by_name(state, name):
    for s in state["snippets"]:
        if s["name"] == name:
            return s
    raise ValueError(f"Snippet not found: {name!r}")


def find_event_by_title(state, title):
    for e in state["calendarEvents"]:
        if e["title"] == title:
            return e
    raise ValueError(f"Event not found: {title!r}")


def find_booking_page_by_title(state, title):
    for b in state["bookingPages"]:
        if b["title"] == title:
            return b
    raise ValueError(f"Booking page not found: {title!r}")


def find_auto_label_by_name(state, name):
    for a in state["autoLabels"]:
        if a["name"] == name:
            return a
    raise ValueError(f"Auto label not found: {name!r}")


def find_split_by_name(state, name):
    for s in state["splits"]:
        if s["name"] == name:
            return s
    raise ValueError(f"Split not found: {name!r}")


# -- solve functions ----------------------------------------------------------

def solve_task_1(state):
    """Mark email 'Q2 Product Roadmap - Final Review' as read."""
    email = find_email_by_subject_and_sender(state, "Q2 Product Roadmap - Final Review", "sarah.chen@acmecorp.com")
    email["isRead"] = True


def solve_task_2(state):
    """Mark email 'Re: Infrastructure Migration Plan' as unread."""
    email = find_email_by_subject_and_sender(state, "Re: Infrastructure Migration Plan", "tom.bradley@acmecorp.com")
    email["isRead"] = False


def solve_task_3(state):
    """Star email 'Partnership Opportunity - FinancePlus x Acme'."""
    email = find_email_by_subject_and_sender(state, "Partnership Opportunity - FinancePlus x Acme", "david.kim@financeplus.com")
    email["isStarred"] = True


def solve_task_4(state):
    """Unstar email 'FY2026 Budget Summary'."""
    email = find_email_by_subject_and_sender(state, "FY2026 Budget Summary", "priya.sharma@acmecorp.com")
    email["isStarred"] = False


def solve_task_5(state):
    """Mark Done email 'Global Health Initiative - Sponsorship Request'."""
    email = find_email_by_subject_and_sender(state, "Global Health Initiative - Sponsorship Request", "ana.g@globalhealth.org")
    email["isDone"] = True
    email["isRead"] = True
    email["remindAt"] = None


def solve_task_6(state):
    """Move email 'Re: Q1 Sales Numbers' from Done back to Inbox."""
    email = find_email_by_subject_and_sender(state, "Re: Q1 Sales Numbers", "sarah.chen@acmecorp.com")
    email["isDone"] = False


def solve_task_7(state):
    """Set reminder on email 'Quantum Computing Integration Prototype' for tomorrow."""
    email = find_email_by_subject_and_sender(state, "Quantum Computing Integration Prototype", "kevin.zhao@quantumlab.tech")
    email["remindAt"] = "2026-03-08T09:00:00.000Z"
    email["isRead"] = True


def solve_task_8(state):
    """Clear reminder on email 'Patent Filing Deadline - April 15'."""
    email = find_email_by_subject_and_sender(state, "Patent Filing Deadline - April 15", "james.obrien@legalwise.com")
    email["remindAt"] = None


def solve_task_9(state):
    """Move email 'Logistics Update - Office Equipment Delivery' to Trash."""
    email = find_email_by_subject_and_sender(state, "Logistics Update - Office Equipment Delivery", "carlos.m@logisticspro.net")
    email["isTrashed"] = True
    email["isDone"] = False
    email["remindAt"] = None


def solve_task_10(state):
    """Restore email 'Complete Your Survey - Win a $500 Gift Card' from Trash."""
    email = find_email_by_subject_contains(state, "Complete Your Survey")
    email["isTrashed"] = False


def solve_task_11(state):
    """Mark email about AI Startup Funding as spam."""
    email = find_email_by_subject_contains(state, "AI Startup Funding Hits Record")
    email["isSpam"] = True
    email["isDone"] = False
    email["remindAt"] = None


def solve_task_12(state):
    """Unmark email 'URGENT: Inheritance Notification' as spam."""
    email = find_email_by_subject_contains(state, "Inheritance Notification")
    email["isSpam"] = False


def solve_task_13(state):
    """Add 'Urgent' label to email 'Budget Approval Needed - Marketing Campaign'."""
    email = find_email_by_subject_and_sender(state, "Budget Approval Needed - Marketing Campaign", "priya.sharma@acmecorp.com")
    urgent = find_label_by_name(state, "Urgent")
    if urgent["id"] not in email["labels"]:
        email["labels"].append(urgent["id"])


def solve_task_14(state):
    """Remove 'Work' label from email 'Q2 Product Roadmap - Final Review'."""
    email = find_email_by_subject_and_sender(state, "Q2 Product Roadmap - Final Review", "sarah.chen@acmecorp.com")
    work = find_label_by_name(state, "Work")
    email["labels"] = [l for l in email["labels"] if l != work["id"]]


def solve_task_15(state):
    """Add 'Finance' label to email 'Partnership Opportunity - FinancePlus x Acme'."""
    email = find_email_by_subject_and_sender(state, "Partnership Opportunity - FinancePlus x Acme", "david.kim@financeplus.com")
    finance = find_label_by_name(state, "Finance")
    if finance["id"] not in email["labels"]:
        email["labels"].append(finance["id"])


def solve_task_16(state):
    """Send email to marcus.w@designhub.io."""
    next_id = state.get("_nextEmailId", 200)
    new_email = {
        "id": next_id,
        "threadId": f"thread_{next_id + 1}",
        "from": {
            "name": state["currentUser"]["name"],
            "email": state["currentUser"]["email"],
        },
        "to": [{"name": "Marcus Williams", "email": "marcus.w@designhub.io"}],
        "cc": [],
        "bcc": [],
        "subject": "Design Review Follow-up",
        "snippet": "Thanks for the design review. The new components look great.",
        "body": "Thanks for the design review. The new components look great.",
        "date": "2026-03-07T12:00:00.000Z",
        "isRead": True,
        "isStarred": False,
        "isDone": False,
        "isTrashed": False,
        "isSpam": False,
        "isDraft": False,
        "labels": [],
        "hasAttachments": False,
        "attachments": [],
        "splitCategory": "important",
        "remindAt": None,
        "readReceipt": {"opened": False},
        "autoLabel": None,
        "replyDraftingTeammate": None,
        "threadMessages": None,
    }
    state["emails"].insert(0, new_email)
    state["_nextEmailId"] = next_id + 1


def solve_task_17(state):
    """Save draft to kevin.zhao@quantumlab.tech."""
    next_id = state.get("_nextEmailId", 200)
    new_draft = {
        "id": next_id,
        "threadId": f"thread_{next_id + 1}",
        "from": {
            "name": state["currentUser"]["name"],
            "email": state["currentUser"]["email"],
        },
        "to": [{"name": "Kevin Zhao", "email": "kevin.zhao@quantumlab.tech"}],
        "cc": [],
        "bcc": [],
        "subject": "Integration Discussion",
        "snippet": "Let us discuss the quantum integration prototype.",
        "body": "Let us discuss the quantum integration prototype.",
        "date": "2026-03-07T12:00:00.000Z",
        "isRead": True,
        "isStarred": False,
        "isDone": False,
        "isTrashed": False,
        "isSpam": False,
        "isDraft": True,
        "labels": [],
        "hasAttachments": False,
        "attachments": [],
        "splitCategory": "important",
        "remindAt": None,
        "readReceipt": None,
        "autoLabel": None,
        "replyDraftingTeammate": None,
        "threadMessages": None,
    }
    state["emails"].insert(0, new_draft)
    state["_nextEmailId"] = next_id + 1


def solve_task_18(state):
    """Unsubscribe from notifications@github.com."""
    email = find_email_by_subject_contains(state, "Memory leak in WebSocket")
    email["isDone"] = True
    email["isRead"] = True
    if "blockedSenders" not in state["settings"]:
        state["settings"]["blockedSenders"] = []
    if "notifications@github.com" not in state["settings"]["blockedSenders"]:
        state["settings"]["blockedSenders"].append("notifications@github.com")


def solve_task_19(state):
    """Mark Done email 'EuroDesign Conference - Speaker Invitation'."""
    email = find_email_by_subject_and_sender(state, "EuroDesign Conference - Speaker Invitation", "sophie.l@eurodesign.fr")
    email["isDone"] = True
    email["isRead"] = True
    email["remindAt"] = None


def solve_task_20(state):
    """Create label 'Partnerships' with color '#FF5722'."""
    next_id = state.get("_nextLabelId", 30)
    new_label = {
        "id": f"label_{next_id}",
        "name": "Partnerships",
        "type": "user",
        "color": "#FF5722",
    }
    state["labels"].append(new_label)
    state["_nextLabelId"] = next_id + 1


def solve_task_21(state):
    """Delete label 'Receipts' and remove from all emails."""
    label_id = "label_13"
    state["labels"] = [l for l in state["labels"] if l["id"] != label_id]
    for email in state["emails"]:
        email["labels"] = [l for l in email["labels"] if l != label_id]


def solve_task_22(state):
    """Create snippet 'Project Update'."""
    next_id = state.get("_nextSnippetId", 30)
    new_snippet = {
        "id": f"snip_{next_id}",
        "name": "Project Update",
        "body": "Hi {first_name}, here is the latest update on {project_name}. Please review and let me know your thoughts.",
        "variables": ["first_name", "project_name"],
        "isShared": False,
        "author": state["currentUser"]["name"],
        "authorId": state["currentUser"]["id"],
        "createdAt": "2026-03-07T12:00:00.000Z",
        "metrics": {"sends": 0, "openRate": 0, "responseRate": 0},
    }
    state["snippets"].append(new_snippet)
    state["_nextSnippetId"] = next_id + 1


def solve_task_23(state):
    """Delete snippet 'Decline Politely'."""
    state["snippets"] = [s for s in state["snippets"] if s["name"] != "Decline Politely"]


def solve_task_24(state):
    """Toggle sharing on for snippet 'Scheduling Request'."""
    snippet = find_snippet_by_name(state, "Scheduling Request")
    snippet["isShared"] = True


def solve_task_25(state):
    """Toggle sharing off for snippet '[Sales] Product Demo'."""
    snippet = find_snippet_by_name(state, "[Sales] Product Demo")
    snippet["isShared"] = False


def solve_task_26(state):
    """Create calendar event 'Team Lunch'."""
    next_id = state.get("_nextEventId", 30)
    new_event = {
        "id": f"evt_{next_id}",
        "title": "Team Lunch",
        "date": "2026-03-10",
        "startTime": "12:00",
        "endTime": "13:00",
        "location": "Cafe Gratitude",
        "description": "",
        "attendees": [],
        "meetingLink": None,
        "isAllDay": False,
        "calendarId": "work",
        "organizer": state["currentUser"]["email"],
        "status": "confirmed",
        "color": "#6C4FF7",
    }
    state["calendarEvents"].append(new_event)
    state["_nextEventId"] = next_id + 1


def solve_task_27(state):
    """Delete calendar event 'Yoga Class'."""
    state["calendarEvents"] = [e for e in state["calendarEvents"] if not (e["title"] == "Yoga Class" and e["date"] == "2026-03-07")]


def solve_task_28(state):
    """Create booking page 'Strategy Session'."""
    next_id = state.get("_nextBookingPageId", 10)
    new_bp = {
        "id": f"bp_{next_id}",
        "title": "Strategy Session",
        "duration": 60,
        "location": "Zoom",
        "description": "",
        "availability": {"days": ["Mon", "Tue", "Wed", "Thu", "Fri"], "startTime": "09:00", "endTime": "17:00"},
        "link": "https://cal.superhuman.com/alex.morgan/strategy-session",
        "isActive": True,
    }
    state["bookingPages"].append(new_bp)
    state["_nextBookingPageId"] = next_id + 1


def solve_task_29(state):
    """Toggle booking page 'Quick Sync' to active."""
    bp = find_booking_page_by_title(state, "Quick Sync")
    bp["isActive"] = True


def solve_task_30(state):
    """Delete booking page 'Product Demo'."""
    state["bookingPages"] = [b for b in state["bookingPages"] if b["title"] != "Product Demo"]


def solve_task_31(state):
    """Create auto label 'Engineering Alerts'."""
    next_id = state.get("_nextAutoLabelId", 20)
    new_al = {
        "id": f"al_{next_id}",
        "name": "Engineering Alerts",
        "type": "custom",
        "enabled": True,
        "criteria": {"from": "@sentry.io"},
    }
    state["autoLabels"].append(new_al)
    state["_nextAutoLabelId"] = next_id + 1


def solve_task_32(state):
    """Enable auto label 'Shipping Update'."""
    al = find_auto_label_by_name(state, "Shipping Update")
    al["enabled"] = True


def solve_task_33(state):
    """Disable auto label 'Team Update'."""
    al = find_auto_label_by_name(state, "Team Update")
    al["enabled"] = False


def solve_task_34(state):
    """Delete auto label 'Support Ticket'."""
    state["autoLabels"] = [a for a in state["autoLabels"] if a["name"] != "Support Ticket"]


def solve_task_35(state):
    """Create split 'Investors' based on auto label 'Investor'."""
    next_id = state.get("_nextSplitId", 20)
    new_split = {
        "id": f"split_{next_id}",
        "name": "Investors",
        "position": len(state["splits"]),
        "isDefault": False,
        "criteria": {"autoLabel": "Investor"},
    }
    state["splits"].append(new_split)
    state["_nextSplitId"] = next_id + 1


def solve_task_36(state):
    """Delete split 'Feeds'."""
    state["splits"] = [s for s in state["splits"] if s["name"] != "Feeds"]


# -- Settings toggle solvers --

def solve_task_37(state):
    state["settings"]["notifications"]["desktop"] = False

def solve_task_38(state):
    state["settings"]["notifications"]["sound"] = False

def solve_task_39(state):
    state["settings"]["instantReply"]["enabled"] = False

def solve_task_40(state):
    state["settings"]["smartSend"]["enabled"] = False

def solve_task_41(state):
    state["settings"]["readReceipts"]["enabled"] = False

def solve_task_42(state):
    state["settings"]["readReceipts"]["teamSharing"] = False

def solve_task_43(state):
    state["settings"]["autoDrafts"]["ccTeammate"] = True

def solve_task_44(state):
    state["settings"]["notifications"]["calendarAlerts"] = False

def solve_task_45(state):
    state["settings"]["meetingLink"]["autoAdd"] = False

def solve_task_46(state):
    state["settings"]["keyboard"]["shortcuts"] = False

def solve_task_47(state):
    state["settings"]["autoArchive"]["enabled"] = False

def solve_task_48(state):
    state["settings"]["autoReminders"]["enabled"] = False

def solve_task_49(state):
    state["settings"]["autoDrafts"]["enabled"] = False

def solve_task_50(state):
    state["settings"]["askAi"]["enabled"] = False


# -- Settings dropdown solvers --

def solve_task_51(state):
    state["settings"]["theme"] = "dark"

def solve_task_52(state):
    state["settings"]["swipeLeft"] = "trash"

def solve_task_53(state):
    state["settings"]["swipeRight"] = "star"

def solve_task_54(state):
    state["settings"]["autoReminders"]["defaultTime"] = "14:00"

def solve_task_55(state):
    state["settings"]["notifications"]["alertMinutes"] = 30

def solve_task_56(state):
    state["settings"]["meetingLink"]["provider"] = "google-meet"

def solve_task_57(state):
    state["settings"]["timezone"] = "America/Los_Angeles"

def solve_task_58(state):
    state["settings"]["secondaryTimezone"] = ""


# -- Settings radio solvers --

def solve_task_59(state):
    state["settings"]["autoReminders"]["mode"] = "external"

def solve_task_60(state):
    state["settings"]["autoDrafts"]["type"] = "scheduling"


SOLVERS = {f"task_{i}": globals()[f"solve_task_{i}"] for i in range(1, 61)}


# -- server management -------------------------------------------------------

def generate_seed_state():
    data_js = str(APP_DIR / "js" / "data.js")
    result = subprocess.run(
        ["node", "-e", _SEED_STATE_JS, data_js],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to generate seed state:\n{result.stderr}")
    return json.loads(result.stdout)


def seed_server(server_url, seed_state):
    resp = requests.put(
        f"{server_url}/api/state",
        json=seed_state,
        headers={"Content-Type": "application/json"},
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to seed server: HTTP {resp.status_code}")


def find_free_port(start=9500):
    port = start
    while port < start + 200:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError(f"No free port found in range {start}-{start+200}")


def start_server(port):
    proc = subprocess.Popen(
        [sys.executable, "server.py", "--port", str(port)],
        cwd=str(APP_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        try:
            requests.get(f"http://localhost:{port}/", timeout=1)
            return proc
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(0.2)
    proc.kill()
    raise RuntimeError(f"Server failed to start on port {port}")


def stop_server(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


# -- task runner --------------------------------------------------------------

def load_tasks():
    with open(TASKS_FILE) as f:
        return json.load(f)


def load_verifier(verify_path):
    full_path = APP_DIR / verify_path
    spec = importlib.util.spec_from_file_location("verifier", str(full_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.verify


def run_single_task(task, server_url):
    task_id = task["id"]
    solver = SOLVERS.get(task_id)
    if not solver:
        return task_id, False, f"No solver defined for {task_id}"

    try:
        # 1. Reset to seed state
        resp = requests.post(f"{server_url}/api/reset")
        if resp.status_code != 200:
            return task_id, False, f"Reset failed: HTTP {resp.status_code}"

        time.sleep(0.3)

        # 2. Read seed state
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return task_id, False, f"Could not read state after reset: HTTP {resp.status_code}"
        state = resp.json()

        # 3. Apply the solve function
        solver(state)

        # 4. Write solved state back
        resp = requests.put(
            f"{server_url}/api/state",
            json=state,
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code != 200:
            return task_id, False, f"Could not write state: HTTP {resp.status_code}"

        # 5. Run the verifier
        verify_fn = load_verifier(task["verify"])
        passed, message = verify_fn(server_url)
        return task_id, passed, message

    except Exception as e:
        return task_id, False, f"Exception: {e}"


def run_tasks_sequential(tasks, port, seed_state):
    proc = start_server(port)
    server_url = f"http://localhost:{port}"
    results = []
    try:
        seed_server(server_url, seed_state)
        for task in tasks:
            result = run_single_task(task, server_url)
            results.append(result)
            status = "\033[32m  PASS\033[0m" if result[1] else "\033[31m  FAIL\033[0m"
            print(f"{status}  {result[0]:12s}  {result[2]}")
    finally:
        stop_server(proc)
    return results


def run_tasks_parallel(tasks, workers, base_port, seed_state):
    results = []

    def worker_fn(task, port):
        proc = start_server(port)
        server_url = f"http://localhost:{port}"
        try:
            seed_server(server_url, seed_state)
            return run_single_task(task, server_url)
        finally:
            stop_server(proc)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for i, task in enumerate(tasks):
            port = base_port + i
            future = executor.submit(worker_fn, task, port)
            futures[future] = task["id"]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            status = "\033[32m  PASS\033[0m" if result[1] else "\033[31m  FAIL\033[0m"
            print(f"{status}  {result[0]:12s}  {result[2]}")

    return results


# -- main ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Superhuman Mail function-task sanity check")
    parser.add_argument("--task-id", type=str, help="Run a single task by ID")
    parser.add_argument("--workers", type=int, default=1, help="Number of parallel workers")
    parser.add_argument("--port", type=int, default=9500, help="Base port for servers")
    args = parser.parse_args()

    tasks = load_tasks()
    if args.task_id:
        tasks = [t for t in tasks if t["id"] == args.task_id]
        if not tasks:
            print(f"Task '{args.task_id}' not found.")
            sys.exit(1)

    print("Generating seed state from JS data...")
    seed_state = generate_seed_state()
    print(f"Running {len(tasks)} task(s)...\n")

    if args.workers <= 1:
        port = find_free_port(args.port)
        results = run_tasks_sequential(tasks, port, seed_state)
    else:
        results = run_tasks_parallel(tasks, args.workers, args.port, seed_state)

    # Summary
    passed = sum(1 for _, p, _ in results if p)
    total = len(results)
    failed = [tid for tid, p, _ in results if not p]

    print(f"\n{passed}/{total} passed")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
