"""Task loading, filtering, verification, and single-task execution."""

import asyncio
import importlib.util
import json
import shutil
import time
from pathlib import Path

import requests

from browser_use import Agent, BrowserSession

TASK_TIMEOUT = 300  # seconds per task wall-clock limit


def load_tasks(web_app_dir: str) -> list[dict]:
    with open(Path(web_app_dir) / "tasks.json") as f:
        return json.load(f)


def filter_tasks(
    tasks: list[dict],
    task_id: str | None = None,
    difficulty: str | None = None,
) -> list[dict]:
    if task_id:
        return [t for t in tasks if t["id"] == task_id]
    if difficulty:
        return [t for t in tasks if t["difficulty"] == difficulty]
    return tasks


def load_verifier(web_app_dir: str, verify_path: str):
    full_path = str(Path(web_app_dir) / verify_path)
    spec = importlib.util.spec_from_file_location("verifier", full_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.verify


def reset_state(server_url: str):
    resp = requests.post(f"{server_url}/api/reset")
    resp.raise_for_status()
    time.sleep(0.5)


async def seed_first_load(server_url: str, session: BrowserSession):
    """Navigate the browser to the app so the server captures the seed state.

    The app's JS pushes initial state via PUT /api/state on first load.
    No agent/LLM call needed — just a direct page navigation.
    """
    await session.start()
    page = await session.get_current_page()
    await page.goto(server_url)
    # Give the app JS time to push state to the server
    await asyncio.sleep(2.0)
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        raise RuntimeError(
            "Seed state not captured after first load. "
            f"GET /api/state returned {resp.status_code}"
        )


async def run_task(
    task: dict,
    llm,
    session: BrowserSession,
    server_url: str,
    web_app_dir: str,
    task_dir: Path,
    max_steps: int,
    use_vision: bool,
) -> dict:
    """Reset state, run the agent, save trajectory, verify, return result dict."""
    task_id = task["id"]
    instruction = (
        f"You are interacting with a GitLab organization management web "
        f"application at {server_url}. Your task: {task['instruction']}"
    )

    # 1. Reset
    reset_state(server_url)

    # 2. Run agent
    agent = Agent(
        task=instruction,
        llm=llm,
        browser_session=session,
        use_vision=use_vision,
        save_conversation_path=str(task_dir / "conversations"),
        max_steps=max_steps,
    )

    t0 = time.time()
    history = await asyncio.wait_for(agent.run(), timeout=TASK_TIMEOUT)
    elapsed = time.time() - t0

    # 3. Save trajectory
    history.save_to_file(task_dir / "history.json")
    screenshots_dst = task_dir / "screenshots"
    for step_idx, path_str in enumerate(history.screenshot_paths()):
        if path_str and Path(path_str).exists():
            screenshots_dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path_str, screenshots_dst / f"step_{step_idx}.png")

    # 4. Verify
    try:
        verify_fn = load_verifier(web_app_dir, task["verify"])
        passed, verifier_message = verify_fn(server_url)
    except Exception as e:
        passed, verifier_message = False, f"Verifier exception: {e}"

    result = {
        "task_id": task_id,
        "difficulty": task["difficulty"],
        "instruction": task["instruction"],
        "passed": passed,
        "verifier_message": verifier_message,
        "elapsed": round(elapsed, 1),
        "steps": len(history.history),
        "is_done": history.is_done(),
        "final_result": history.final_result(),
        "errors": history.errors(),
    }

    with open(task_dir / "result.json", "w") as f:
        json.dump(result, f, indent=2)

    return result
