# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["agentscope==1.0.16", "mcp==1.23.1", "sqlalchemy[asyncio]>=2,<3", "tqdm>=4,<5"]
# ///
"""Replay a policy revision before, during, or after a capacity decision."""
import argparse
import asyncio
import itertools
import json
from collections import Counter
from pathlib import Path

from agentscope.agent import AgentBase
from agentscope.message import Msg
from replay import Rule

MODES = ("snapshot", "recheck_at_handoff", "ask_on_edit", "current_chat", "current_rule")
ORDERS = ("edit read handoff apply", "read edit handoff apply", "read handoff edit apply", "read handoff apply edit")
EDITS = {"tighten": ("checkout", 100), "loosen": ("checkout", 300), "unrelated": ("billing", 100)}
DATE = "2026-11-27"


class Som(AgentBase):
    def __init__(self):
        super().__init__()
        self.name = "Som"
        self.rules = {}
        self.chat = []
        self.publish("checkout", 200)
        self.publish("billing", 200)

    def publish(self, service, limit):
        rule = Rule(service, limit, DATE)
        self.rules[service] = rule
        self.chat.append(Msg(self.name, rule.message(), "assistant"))

    async def reply(self, msg):
        decision = self.rules["checkout"].allows(msg.metadata)
        return Msg(self.name, "allow" if decision else "hold", "assistant")


class Operator(AgentBase):
    def __init__(self, som, mode):
        super().__init__()
        self.name = "Dana"
        self.som = som
        self.mode = mode
        self.reviews = 0

    async def reply(self, msg):
        som = self.som
        if msg.content == "read":
            self.snapshot = som.rules["checkout"]
            self.version = len(som.chat)
            return Msg(self.name, "ready", "assistant")
        if msg.content == "handoff":
            if self.mode == "recheck_at_handoff":
                self.snapshot = som.rules["checkout"]
            return Msg(self.name, "queued", "assistant")
        rule = self.snapshot
        if self.mode == "ask_on_edit" and self.version != len(som.chat):
            self.reviews += 1
            return await som(msg)
        if self.mode == "current_rule":
            rule = som.rules["checkout"]
        if self.mode == "current_chat":
            for post in reversed(som.chat):
                candidate = Rule.from_message(post.content)
                if candidate and candidate.service == msg.metadata["service"]:
                    rule = candidate
                    break
        # The replay treats this check and the application as one indivisible step.
        return Msg(self.name, "allow" if rule.allows(msg.metadata) else "hold", "assistant")


async def trial(mode, edit, order, cost):
    som = Som()
    worker = Operator(som, mode)
    request = {"service": "checkout", "until": DATE, "cost": cost}
    for event in order.split():
        if event == "edit":
            som.publish(*EDITS[edit])
        else:
            result = await worker(Msg("driver", event, "user", metadata=request))
            if event == "apply":
                decision = result.content
    current_limit = 200
    if order.index("edit") < order.index("apply") and edit != "unrelated":
        current_limit = EDITS[edit][1]
    expected = "allow" if cost <= current_limit else "hold"
    return {"edit": edit, "order": order, "cost": cost, "expected": expected,
            "decision": decision, "owner_rechecks": worker.reviews}


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = {}
    for mode in MODES:
        counts = Counter(cases=0, unauthorized=0, unnecessary_holds=0, owner_rechecks=0)
        failures = []
        for edit, order, cost in itertools.product(EDITS, ORDERS, (100, 101, 200, 201, 300, 301)):
            row = await trial(mode, edit, order, cost)
            counts["cases"] += 1
            counts["owner_rechecks"] += row["owner_rechecks"]
            if row["decision"] != row["expected"]:
                counts["unauthorized" if row["decision"] == "allow" else "unnecessary_holds"] += 1
                failures.append(row)
        report[mode] = {"counts": dict(counts), "counterexamples": failures}
        print(mode, dict(counts))
    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    asyncio.run(main())
