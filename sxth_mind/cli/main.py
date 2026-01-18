"""
sxth-mind CLI

Command-line interface for running and testing sxth-mind.
"""

import argparse
import asyncio
import sys


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="sxth-mind: The understanding layer for adaptive AI products",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sxth-mind demo              Run interactive demo with Sales adapter
  sxth-mind demo --adapter habits   Run with Habits adapter
  sxth-mind info              Show package information

Learn more at https://github.com/toywobot/sxth-mind
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run interactive demo")
    demo_parser.add_argument(
        "--adapter",
        choices=["sales", "habits", "learning"],
        default="sales",
        help="Adapter to use (default: sales)",
    )
    demo_parser.add_argument(
        "--user-id",
        default="demo_user",
        help="User ID for the demo (default: demo_user)",
    )

    # Info command
    subparsers.add_parser("info", help="Show package information")

    args = parser.parse_args()

    if args.command == "demo":
        asyncio.run(run_demo(args.adapter, args.user_id))
    elif args.command == "info":
        show_info()
    else:
        parser.print_help()


def show_info():
    """Show package information."""
    from sxth_mind import __version__

    print(f"""
sxth-mind v{__version__}
The understanding layer for adaptive AI products

The Mind accumulates state, detects patterns, and adapts over time.

Quick Start:
  from sxth_mind import Mind
  from examples.sales import SalesAdapter

  mind = Mind(adapter=SalesAdapter())
  response = await mind.chat("user_1", "Hello!")

Learn more: https://github.com/toywobot/sxth-mind
""")


async def run_demo(adapter_name: str, user_id: str):
    """Run interactive demo."""
    try:
        from sxth_mind import Mind
    except ImportError as e:
        print(f"Error importing sxth_mind: {e}")
        sys.exit(1)

    # Load adapter
    if adapter_name == "sales":
        try:
            from examples.sales import SalesAdapter
            adapter = SalesAdapter()
        except ImportError:
            print("Sales adapter not found. Using base demo.")
            return
    else:
        print(f"Adapter '{adapter_name}' not yet implemented.")
        print("Available: sales")
        return

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                     sxth-mind Demo                            ║
║                                                               ║
║  Adapter: {adapter.display_name:<20}                         ║
║  User: {user_id:<23}                         ║
║                                                               ║
║  Type 'quit' to exit, 'state' to see current state           ║
╚══════════════════════════════════════════════════════════════╝
""")

    try:
        mind = Mind(adapter=adapter)
    except ImportError as e:
        print(f"\nError: {e}")
        print("\nTo run the demo, install an LLM provider:")
        print("  pip install sxth-mind[openai]")
        return

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("\nGoodbye!")
            break

        if user_input.lower() == "state":
            state_summary = await mind.explain_state(user_id)
            print(f"\n{state_summary}")
            continue

        try:
            response = await mind.chat(user_id, user_input)
            print(f"\nAssistant: {response}")
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
