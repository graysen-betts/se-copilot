"""CLI entry point for SE Co-Pilot."""

from __future__ import annotations

import argparse
import sys
import time

from se_copilot.data.sample import get_account_context
from se_copilot.orchestrator import TriggerType, format_slack_message, handle_trigger


def main():
    parser = argparse.ArgumentParser(
        prog="se-copilot",
        description="Autonomous SE Co-Pilot — generates SE-owned materials across Atlan sales stages S2-S6",
    )
    parser.add_argument(
        "--trigger",
        choices=["calendar", "stage_change", "daily_sweep"],
        default="calendar",
        help="Trigger type to simulate (default: calendar)",
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-6",
        help="Model to use for generation (default: claude-sonnet-4-6)",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Output raw content without Slack formatting",
    )
    args = parser.parse_args()

    trigger_map = {
        "calendar": TriggerType.CALENDAR_EVENT,
        "stage_change": TriggerType.STAGE_CHANGE,
        "daily_sweep": TriggerType.DAILY_SWEEP,
    }

    print("=" * 60)
    print("SE Co-Pilot — End-to-End Demo")
    print("=" * 60)

    ctx = get_account_context()
    account = ctx["account"]
    opp = ctx["opportunity"]
    meeting = ctx["upcoming_meeting"]

    print(f"\nAccount:  {account['account_name']} ({account['industry']})")
    print(f"Stage:    {opp['stage']}")
    print(f"ARR:      ${opp['amount']:,}")
    print(f"Meeting:  {meeting['title']}")
    print(f"Time:     {meeting['start_time']}")
    print(f"Trigger:  {args.trigger}")
    print(f"Model:    {args.model}")

    print(f"\nGenerating SE call prep...")
    start = time.time()

    results = handle_trigger(trigger_map[args.trigger], ctx)

    elapsed = time.time() - start

    if not results:
        print("No materials generated.")
        sys.exit(1)

    result = results[0]
    print(f"Done in {elapsed:.1f}s ({result['input_tokens']} in / {result['output_tokens']} out tokens)\n")
    print("=" * 60)

    if args.raw:
        print(result["content"])
    else:
        print(format_slack_message(result))

    print("\n" + "=" * 60)
    print(f"Confidence: {result['confidence']} — {result['confidence_reason']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
