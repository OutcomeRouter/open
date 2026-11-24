# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["agentscope==1.0.16", "mcp==1.23.1", "sqlalchemy[asyncio]>=2,<3", "tqdm>=4,<5"]
# ///
"""Replay recorded model choices against a scripted AgentScope owner."""
import argparse
import asyncio
import json
from pathlib import Path
import sys

from agentscope.message import Msg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from replay import Rule
from revision import DATE, Som
from study import CASES


class ScopedOwner(Som):
    async def reply(self, msg):
        rule = self.rules[msg.metadata["service"]]
        if msg.metadata.get("clarify"):
            return Msg(self.name, rule.message(), "assistant")
        return Msg(self.name, "allow" if rule.allows(msg.metadata) else "hold", "assistant")


async def check(runs):
    cases = {case[0]: case for case in CASES}
    for row in runs:
        owner = ScopedOwner()
        service, _, _, limit = cases[row["service"]]
        owner.publish(service, limit)
        confirmed = False
        questions = 0
        for index, step in enumerate(row["live"]):
            assert row["checkpoints"][index]["confirmed"] == confirmed
            choice = step["choice"]
            if choice == "resolve":
                questions += 1
                answer = await owner(Msg("worker", "Confirm the revision", "user",
                                         metadata={"clarify": True, "service": service}))
                # In this benchmark each confirmation must name its own service.
                rule = Rule.from_message(answer.content)
                assert rule and rule.service == service and rule.limit == limit
                confirmed = True
            elif choice == "ask":
                questions += 1
                answer = await owner(Msg("worker", "Decide this request", "user",
                                         metadata={"service": service, "cost": step["cost"], "until": DATE}))
                assert answer.content == step["expected"]
        assert row["checkpoints"][-1]["confirmed"] == confirmed
        assert row["owner_interruptions"] == questions
    print(f"Verified owner replies and persistence for {len(runs)} recorded trajectories")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    asyncio.run(check(json.loads(args.report.read_text())["runs"]))
