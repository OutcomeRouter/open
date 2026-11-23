"""Compare two complete Open Harness Bench Inspect logs, pairing by task and epoch."""
import argparse
import json
from collections import Counter
from inspect_ai.log import read_eval_log


def attempts(log):
    if log.status != "success" or not log.samples:
        raise ValueError("Each arm needs a completed log with scored samples.")
    records = {}
    for sample in log.samples:
        scores = list((sample.scores or {}).values())
        if sample.error or len(scores) != 1 or not scores[0].metadata:
            raise ValueError(f"Missing verdict for {sample.id}, epoch {sample.epoch}")
        verdict = scores[0].metadata.get("verdict")
        meta = sample.metadata
        required = ("fixture_sha256", "runner_sha256", "inspect_version", "sandbox", "tier",
                    "timeout_minutes", "command_sha256", "agent", "worker_layers")
        if verdict not in {"pass", "fail"} or any(field not in meta for field in required):
            raise ValueError(f"Incomplete benchmark metadata for {sample.id}; rerun with the current runner")
        key = (str(sample.id), sample.epoch)
        if key in records:
            raise ValueError(f"Duplicate attempt {key}")
        records[key] = (verdict, meta)
    return records


def compare(left_log, right_log):
    left, right = attempts(left_log), attempts(right_log)
    if left.keys() != right.keys():
        raise ValueError("Task IDs or epochs differ between arms.")
    outcomes = Counter()
    arms = [set(), set()]
    changes = []
    for key in sorted(left):
        (before, a), (after, b) = left[key], right[key]
        for field in ("fixture_sha256", "runner_sha256", "inspect_version", "sandbox", "tier", "timeout_minutes"):
            if a[field] != b[field]:
                raise ValueError(f"Unmatched {field} for {key}")
        for values, row in zip(arms, (a, b)):
            values.add(json.dumps({k: row[k] for k in ("agent", "command_sha256", "worker_layers")}, sort_keys=True))
        outcomes[(before, after)] += 1
        if before != after:
            changes.append({"task": key[0], "epoch": key[1], "left": before, "right": after})
    if any(len(values) != 1 for values in arms):
        raise ValueError("Worker configuration changed within an arm.")
    return {
        "arms": [json.loads(next(iter(values))) for values in arms],
        "paired_attempts": len(left),
        "both_pass": outcomes["pass", "pass"], "both_fail": outcomes["fail", "fail"],
        "left_only": outcomes["pass", "fail"], "right_only": outcomes["fail", "pass"],
        "changed_verdicts": changes,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left")
    parser.add_argument("right")
    args = parser.parse_args()
    try:
        print(json.dumps(compare(read_eval_log(args.left), read_eval_log(args.right)), indent=2))
    except ValueError as exc:
        parser.exit(2, f"{exc}\n")
