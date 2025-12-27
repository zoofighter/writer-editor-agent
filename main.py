#!/usr/bin/env python3
"""
Main entry point for the Writer-Editor review loop system.

This script provides command-line access to both simple and multi-agent workflows.
"""

import argparse
import sys
from pathlib import Path

from src.ui import CLI
from src.llm.client import LMStudioClient
from src.config.settings import settings


def test_lm_studio_connection() -> bool:
    """
    Test connection to LM Studio.

    Returns:
        True if connection successful, False otherwise
    """
    print(f"Testing connection to LM Studio at {settings.lm_studio_base_url}...")

    try:
        client = LMStudioClient(
            base_url=settings.lm_studio_base_url,
            model_name=settings.lm_studio_model
        )

        if client.test_connection():
            print(f"✓ Successfully connected to LM Studio")
            print(f"  Model: {settings.lm_studio_model}")
            return True
        else:
            print("✗ Failed to connect to LM Studio")
            print("\nTroubleshooting:")
            print("1. Make sure LM Studio is running")
            print("2. Check that the local server is started (port 1234)")
            print("3. Verify the model is loaded")
            return False

    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure LM Studio is running")
        print("2. Check that the local server is started")
        print("3. Verify the base URL in .env file")
        return False


def ensure_data_directory():
    """Ensure the data directory exists for checkpoints."""
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
        print(f"Created data directory: {data_dir}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Writer-Editor Review Loop System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test LM Studio connection
  python main.py --test-connection

  # Start multi-agent workflow (default)
  python main.py

  # Specify a topic
  python main.py --topic "AI in healthcare"

  # Use simple workflow (Writer-Editor only)
  python main.py --mode simple

  # Resume a previous session
  python main.py --thread-id abc-123-def

  # Custom iteration limits
  python main.py --max-iterations 5 --max-outline-revisions 2
        """
    )

    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test connection to LM Studio and exit"
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["simple", "multi-agent"],
        default="multi-agent",
        help="Workflow mode (default: multi-agent)"
    )

    parser.add_argument(
        "--topic",
        type=str,
        help="Content topic (prompts if not provided)"
    )

    parser.add_argument(
        "--thread-id",
        type=str,
        help="Session ID to resume a previous session"
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        help=f"Maximum draft revision iterations (default: {settings.max_iterations})"
    )

    parser.add_argument(
        "--max-outline-revisions",
        type=int,
        help=f"Maximum outline revision iterations (default: {settings.max_outline_revisions})"
    )

    args = parser.parse_args()

    # Test connection mode
    if args.test_connection:
        success = test_lm_studio_connection()
        sys.exit(0 if success else 1)

    # Ensure data directory exists
    ensure_data_directory()

    # Create CLI and start session
    try:
        cli = CLI(mode=args.mode)

        cli.start_session(
            topic=args.topic,
            thread_id=args.thread_id,
            max_iterations=args.max_iterations,
            max_outline_revisions=args.max_outline_revisions
        )

    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Session state has been saved.")
        print("You can resume this session using --thread-id")
        sys.exit(0)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
