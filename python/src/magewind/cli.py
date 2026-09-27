"""Command-line entry point."""

import argparse
import os 
import sys 
from pathlib import Path 

from magewind import __version__ 
from magewind.agent import Agent 
from magewind.model import EchoClient 


# Todo: add more arg commands 
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="magewind", description="A cli agent for the system-one era")
    parser.add_argument("prompt", nargs="*", help="one shot request; omit to start interactive session")
    parser.add_argument("-C", "--cwd", type=Path, default=Path.cwd(), help="working folder")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser.parse_args(argv)

def repl(agent: Agent) -> None: 
    print("magewind -- type a request, or 'exit' to quit.")
    while True:
        try: 
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 
        if not line: 
            continue 
        if line in {"exit", "quit"}: 
            return 
        print(agent.step(line).content)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    os.chdir(args.cwd)
    agent = Agent(EchoClient())

    if args.prompt:
        print(agent.step(" ".join(args.prompt)).content)
    else:
        repl(agent)
    return 0


if __name__ == "__main__":
    sys.exit(main())