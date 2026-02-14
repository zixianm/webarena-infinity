#!/usr/bin/env python3
"""
Interactive verifier testing tool.

Usage:
    python3 test_verifier.py [task_id]

Example:
    python3 test_verifier.py task_e1

If no task_id is given, lists all available tasks and prompts for selection.
Each round: resets state → waits for you to perform the task in the browser → you press Enter → runs the verifier.
Type 'q' to quit or pick a different task.
"""

import importlib.util
import json
import sys
import time

import requests

SERVER_URL = "http://localhost:8080"
TASKS_FILE = "tasks.json"


def load_tasks():
    with open(TASKS_FILE) as f:
        return json.load(f)


def load_verifier(verify_path):
    spec = importlib.util.spec_from_file_location("verifier", verify_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.verify


def reset_and_wait():
    """Reset state to seed data on the server and notify the browser."""
    resp = requests.post(f"{SERVER_URL}/api/reset")
    if resp.status_code != 200:
        print(f"  [!] Reset failed: {resp.status_code}")
        return False

    data = resp.json()
    if not data.get("seed_restored"):
        print("  [!] No seed state captured yet. Load the app in a browser first.")
        return False

    # Brief pause to let the browser process the SSE reset event
    time.sleep(0.5)
    return True


def pick_task(tasks):
    """Display task list and let user pick one."""
    print("\nAvailable tasks:")
    print("-" * 80)
    for i, t in enumerate(tasks):
        print(f"  {t['id']:10s}  [{t['difficulty']:6s}]  {t['instruction'][:55]}...")
    print("-" * 80)
    while True:
        choice = input("\nEnter task ID (e.g. task_e1) or 'q' to quit: ").strip()
        if choice == "q":
            return None
        match = next((t for t in tasks if t["id"] == choice), None)
        if match:
            return match
        print(f"  Unknown task '{choice}'. Try again.")


def run_loop(task, tasks):
    """Run reset-perform-verify loop for a task."""
    verify_fn = load_verifier(task["verify"])
    attempt = 0

    while True:
        attempt += 1
        print(f"\n{'='*70}")
        print(f"Task:       {task['id']} [{task['difficulty']}]")
        print(f"Instruction: {task['instruction']}")
        print(f"Attempt:    #{attempt}")
        print(f"{'='*70}")

        print("\n  Resetting state...", end=" ", flush=True)
        if not reset_and_wait():
            return
        print("done.")
        print("\n  >>> Perform the task in your browser now. <<<")

        cmd = (
            input(
                "\n  Press Enter when done, 'r' to re-reset, 's' to switch task, 'q' to quit: "
            )
            .strip()
            .lower()
        )
        if cmd == "q":
            return "quit"
        if cmd == "s":
            return "switch"
        if cmd == "r":
            attempt -= 1
            continue

        # Run verifier
        print("\n  Running verifier...", end=" ", flush=True)
        try:
            passed, message = verify_fn(SERVER_URL)
        except Exception as e:
            passed, message = False, f"Verifier error: {e}"

        if passed:
            print("PASSED")
            print(f"  {message}")
        else:
            print("FAILED")
            print(f"  {message}")

        cmd = (
            input("\n  Press Enter to retry, 's' to switch task, 'q' to quit: ")
            .strip()
            .lower()
        )
        if cmd == "q":
            return "quit"
        if cmd == "s":
            return "switch"


def main():
    tasks = load_tasks()

    # If task_id provided as argument, jump straight to it
    if len(sys.argv) > 1:
        task_id = sys.argv[1]
        task = next((t for t in tasks if t["id"] == task_id), None)
        if not task:
            print(
                f"Unknown task '{task_id}'. Available: {', '.join(t['id'] for t in tasks)}"
            )
            sys.exit(1)
    else:
        task = pick_task(tasks)
        if not task:
            return

    while True:
        result = run_loop(task, tasks)
        if result == "quit" or result is None:
            break
        if result == "switch":
            task = pick_task(tasks)
            if not task:
                break

    print("\nDone.")


if __name__ == "__main__":
    main()
