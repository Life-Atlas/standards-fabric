"""Record a scheduled run in data/mvt_evidence.json — so MVT criteria M3 and M10 close themselves.

Called by the weekly/monthly workflows. Only records when the run was triggered by `schedule`;
a human pressing "Run workflow" is not evidence of autonomy.

    python scripts/record_run.py --minutes 6
"""
import argparse
import json
import os
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
P = os.path.join(ROOT, "data", "mvt_evidence.json")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=None)
    ap.add_argument("--cadence", default=os.environ.get("SF_CADENCE", "weekly"))
    a = ap.parse_args()

    event = os.environ.get("GITHUB_EVENT_NAME", "")
    if event != "schedule":
        print(f"not a scheduled run (event={event or 'local'}) - nothing recorded")
        return 0

    with open(P, encoding="utf-8") as f:
        ev = json.load(f)
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "Life-Atlas/standards-fabric")
    entry = {"cadence": a.cadence, "run_id": run_id,
             "url": f"https://github.com/{repo}/actions/runs/{run_id}" if run_id else None,
             "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "minutes": a.minutes}
    ev.setdefault("scheduled_runs_observed", []).append(entry)
    ev["scheduled_runs_observed"] = ev["scheduled_runs_observed"][-50:]
    with open(P, "w", encoding="utf-8") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)
    print(f"recorded scheduled {a.cadence} run {run_id} ({a.minutes} min)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
