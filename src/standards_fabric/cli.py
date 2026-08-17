"""standards-fabric command line.

  python -m standards_fabric snapshot            # refresh SEK catalogue snapshot for all committees used by topics
  python -m standards_fabric build               # build site/data/*.json + site/index.html
  python -m standards_fabric report weekly       # run the agents (collectors + optional LLM) → reports/
  python -m standards_fabric report monthly
  python -m standards_fabric gate                # acceptance gate (exit 0 = green)
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from . import twin


def cmd_snapshot(args: argparse.Namespace) -> int:
    from .sek_client import fetch_committees, snapshot
    topics, _ = twin.load_topics()
    wanted = twin.committees_needed(topics)
    if args.committee:
        wanted = [args.committee]
    print(f"snapshotting {len(wanted)} committees → {twin.SNAP}", flush=True)
    counts = snapshot(wanted, twin.SNAP)
    for k, v in counts.items():
        print(f"  {k:12s} {v:5d}")
    if not args.committee:
        cs = fetch_committees()
        with open(os.path.join(twin.SNAP, "_committees.json"), "w", encoding="utf-8") as f:
            json.dump([c.__dict__ for c in cs], f, ensure_ascii=False, indent=1)
        print(f"  committees: {len(cs)}")
    with open(os.path.join(twin.SNAP, "_snapshot_meta.json"), "w", encoding="utf-8") as f:
        json.dump({"counts": counts, "source": "https://elstandard.se/api/search/standard"}, f, ensure_ascii=False, indent=1)
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    from .site import render_site
    payload = twin.build_all()
    print(f"  docs={len(payload['docs'])} curated={len(payload['curated'])} topics={len(payload['topics'])}")
    for rid, p in payload["realities"].items():
        t = p["totals"]
        print(f"  {rid:28s} past={t['past']['total']:5d} now={t['now']['total']:5d} future={t['future']['total']:5d} (pipeline {t['future']['pipeline']}, missing topics {len(p['missing_topics'])})")
    path = render_site(payload)
    print(f"site → {path}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    from .agents.orchestrator import run
    return run(cadence=args.cadence, use_llm=not args.no_llm)


def cmd_gate(args: argparse.Namespace) -> int:
    from .gate import run_gate
    return run_gate()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="standards_fabric")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot")
    s.add_argument("--committee")
    s.set_defaults(fn=cmd_snapshot)
    b = sub.add_parser("build")
    b.set_defaults(fn=cmd_build)
    r = sub.add_parser("report")
    r.add_argument("cadence", choices=["weekly", "monthly"])
    r.add_argument("--no-llm", action="store_true")
    r.set_defaults(fn=cmd_report)
    g = sub.add_parser("gate")
    g.set_defaults(fn=cmd_gate)
    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
