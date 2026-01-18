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
  sxth-mind demo                    Run interactive demo with Sales adapter
  sxth-mind demo --adapter habits   Run with Habits adapter
  sxth-mind serve                   Start HTTP server
  sxth-mind serve --adapter habits  Start with Habits adapter
  sxth-mind info                    Show package information

Learn more at https://github.com/sxth-ai/sxth-mind
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

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start HTTP server")
    serve_parser.add_argument(
        "--adapter",
        choices=["sales", "habits", "learning"],
        default="sales",
        help="Adapter to use (default: sales)",
    )
    serve_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    serve_parser.add_argument(
        "--storage",
        choices=["memory", "sqlite"],
        default="memory",
        help="Storage backend (default: memory)",
    )
    serve_parser.add_argument(
        "--db-path",
        default="sxth_mind.db",
        help="SQLite database path (default: sxth_mind.db)",
    )
    serve_parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )

    # Info command
    subparsers.add_parser("info", help="Show package information")

    args = parser.parse_args()

    if args.command == "demo":
        asyncio.run(run_demo(args.adapter, args.user_id))
    elif args.command == "serve":
        run_server(args)
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

Learn more: https://github.com/sxth-ai/sxth-mind
""")


def get_adapter(adapter_name: str):
    """Load an adapter by name."""
    if adapter_name == "sales":
        from examples.sales import SalesAdapter
        return SalesAdapter()
    elif adapter_name == "habits":
        from examples.habits import HabitCoachAdapter
        return HabitCoachAdapter()
    elif adapter_name == "learning":
        from examples.learning import LearningAdapter
        return LearningAdapter()
    else:
        raise ValueError(f"Unknown adapter: {adapter_name}")


def get_storage(storage_name: str, db_path: str = "sxth_mind.db"):
    """Load a storage backend by name."""
    if storage_name == "memory":
        from sxth_mind.storage import MemoryStorage
        return MemoryStorage()
    elif storage_name == "sqlite":
        from sxth_mind.storage import SQLiteStorage
        return SQLiteStorage(db_path)
    else:
        raise ValueError(f"Unknown storage: {storage_name}")


def run_server(args):
    """Run the HTTP server."""
    try:
        import uvicorn
    except ImportError:
        print("uvicorn not installed. Install with:")
        print("  pip install sxth-mind[api]")
        sys.exit(1)

    # Create a module that uvicorn can import
    adapter = get_adapter(args.adapter)
    storage = get_storage(args.storage, args.db_path)

    from sxth_mind.api import create_app
    app = create_app(adapter=adapter, storage=storage)

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                     sxth-mind Server                          ║
║                                                               ║
║  Adapter: {adapter.display_name:<20}                         ║
║  Storage: {args.storage:<20}                         ║
║  URL: http://{args.host}:{args.port:<24}             ║
║                                                               ║
║  Endpoints:                                                   ║
║    POST /chat          Send a message                         ║
║    POST /chat/stream   Stream a response                      ║
║    GET  /state/{{id}}    Get user state                         ║
║    GET  /explain/{{id}}  Explain state                          ║
║    GET  /nudges/{{id}}   Get pending nudges                     ║
║    GET  /health        Health check                           ║
╚══════════════════════════════════════════════════════════════╝
""")

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


async def run_demo(adapter_name: str, user_id: str):
    """Run interactive demo."""
    try:
        from sxth_mind import Mind
    except ImportError as e:
        print(f"Error importing sxth_mind: {e}")
        sys.exit(1)

    try:
        adapter = get_adapter(adapter_name)
    except ValueError as e:
        print(f"Error: {e}")
        print("Available adapters: sales, habits")
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
