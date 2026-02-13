import asyncio
import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from browser_use import Agent, BrowserSession
from browser_use.llm.openai.chat import ChatOpenAI
from browser_use.llm.google.chat import ChatGoogle
from browser_use.llm.anthropic.chat import ChatAnthropic

load_dotenv()

MODELS = {
    "gpt": lambda: ChatOpenAI(model="gpt-4o"),
    "gemini": lambda: ChatGoogle(model="gemini-2.0-flash"),
    "claude": lambda: ChatAnthropic(model="claude-sonnet-4-5-20250929"),
}


async def main(model_name: str, task: str, max_steps: int, output_dir: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(output_dir) / f"{model_name}_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    llm = MODELS[model_name]()
    session = BrowserSession(headless=True)

    agent = Agent(
        task=task,
        llm=llm,
        browser_session=session,
        use_vision=False,
        save_conversation_path=str(run_dir / "conversations"),
        max_steps=max_steps,
    )

    history = await agent.run()

    # Save trajectory (agent thoughts, actions, results, interacted elements)
    history.save_to_file(run_dir / "history.json")

    # Copy screenshots from the agent's temp dir into our run dir
    screenshots_dst = run_dir / "screenshots"
    for path_str in history.screenshot_paths():
        if path_str and Path(path_str).exists():
            screenshots_dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path_str, screenshots_dst / Path(path_str).name)

    # Save a human-readable summary
    summary = {
        "task": task,
        "model": model_name,
        "timestamp": timestamp,
        "total_steps": len(history.history),
        "is_done": history.is_done(),
        "is_successful": history.is_successful(),
        "final_result": history.final_result(),
        "errors": history.errors(),
        "urls": history.urls(),
    }
    with open(run_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nTrajectory saved to: {run_dir}")
    print(f"  history.json        - full trajectory (thoughts, actions, results)")
    print(f"  conversations/      - full LLM messages per step (includes DOM tree)")
    print(f"  screenshots/        - screenshot PNGs per step")
    print(f"  summary.json        - run metadata")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=MODELS.keys(), default="gpt")
    parser.add_argument("--task", default="Go to google.com and search for 'browser-use python'")
    parser.add_argument("--max-steps", type=int, default=50)
    parser.add_argument("--output-dir", default="./results")
    args = parser.parse_args()
    asyncio.run(main(args.model, args.task, args.max_steps, args.output_dir))
