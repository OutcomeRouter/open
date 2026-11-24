# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["agentscope==1.0.16", "mcp==1.23.1", "sqlalchemy[asyncio]>=2,<3", "tqdm>=4,<5"]
# ///
"""Measure correct autonomous behavior after an amendment using non-training probes."""
import argparse
import asyncio
import json
from pathlib import Path

from agentscope.message import Msg
from amendment import PolicyOwner, Reader
from revision import DATE

# None of the probe dollar amounts occur in the original amendment task stream.
# Labels are fixed before evaluation, independently of the agent and its parser.
PROBES = (99, 100, 101, 199, 200, 201, 299, 300, 301)
PHASES = (
    (100, "For checkout, halve the two-hundred-dollar cap. Friday still stands.",
     ("allow", "allow", "hold", "hold", "hold", "hold", "hold", "hold", "hold")),
    (300, "Raise the checkout cap to three hundred through Friday.",
     ("allow", "allow", "allow", "allow", "allow", "allow", "allow", "allow", "hold")),
)
MODES = ("search_older", "ask_per_request", "clarify_revision", "structured")


async def decision(owner, posts, memory, mode, cost):
    worker = Reader("fresh worker", owner, posts, memory, mode)
    request = Msg("driver", "Capacity request", "user",
                  metadata={"service": "checkout", "cost": cost, "until": DATE})
    result = await worker(request)
    return result.content, worker.asked


async def evaluate(mode):
    owner = PolicyOwner()
    posts = [owner.chat[0]]
    memory = {}
    phases = []
    for limit, wording, labels in PHASES:
        owner.publish("checkout", limit)
        posts.append(Msg(owner.name, wording, "assistant"))
        checkpoints = []
        questions = 0
        for prefix in range(5):
            mismatches = extra_questions = 0
            for cost, expected in zip(PROBES, labels, strict=True):
                # Counterfactual probes each see the same live state. Discard any learned answer.
                choice, asked = await decision(owner, posts, memory.copy(), mode, cost)
                mismatches += choice != expected
                extra_questions += asked
            checkpoints.append({"requests_seen": prefix, "mismatches": mismatches,
                                "questions_on_probes": extra_questions})
            if prefix < 4:
                _, asked = await decision(owner, posts, memory, mode, (80, 150, 250, 350)[prefix])
                questions += asked
        stable_from = next((i for i in range(len(checkpoints))
                            if all(c["mismatches"] == c["questions_on_probes"] == 0
                                   for c in checkpoints[i:])), None)
        phases.append({"limit": limit, "live_questions": questions, "stable_from_request_count": stable_from,
                       "checkpoints": checkpoints})
    return phases


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    results = {mode: await evaluate(mode) for mode in MODES}
    report = {"probe_costs": PROBES, "live_requests_per_revision": 4, "modes": results}
    for mode, phases in results.items():
        print(mode, [(p["stable_from_request_count"], p["live_questions"],
                      p["checkpoints"][-1]["mismatches"]) for p in phases])
    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    asyncio.run(main())
