from __future__ import annotations

import argparse
from pathlib import Path

from self_harness_demo.loop import SelfHarnessLoop


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the minimal Self-Harness demo loop.")
    parser.add_argument("--runtime-dir", type=Path, default=Path("./runtime"), help="Directory for temporary workspaces and logs.")
    parser.add_argument("--max-rounds", type=int, default=4, help="Maximum number of repair rounds.")
    args = parser.parse_args()

    loop = SelfHarnessLoop(runtime_root=args.runtime_dir, max_rounds=args.max_rounds)
    final_mainline = loop.run()

    print("Finished.")
    print(f"Final mainline workspace: {final_mainline}")
    print(f"Round logs: {args.runtime_dir / 'logs' / 'rounds.jsonl'}")


if __name__ == "__main__":
    main()
