# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["agentscope==1.0.16", "mcp==1.23.1", "sqlalchemy[asyncio]>=2,<3", "tqdm>=4,<5"]
# ///
"""Enumerate late clarification replies and replay counterexamples through AgentScope."""
import argparse
import asyncio
import itertools
import json
from dataclasses import dataclass
from pathlib import Path

from agentscope.agent import AgentBase
from agentscope.message import Msg


@dataclass(frozen=True)
class Reply:
    tenant: str
    revision: int
    signer: str
    limit: int


# A and B operate different tenants with the same service and revision numbers.
OWNERS = {"A": "Som", "B": "Mar"}
REPLIES = {
    "old": Reply("A", 1, "Som", 200),
    "new": Reply("A", 2, "Som", 100),
    "other": Reply("B", 1, "Mar", 300),
    "duplicate_old": Reply("A", 1, "Som", 200),
    "wrong_owner": Reply("A", 1, "Mar", 300),
}
MODES = ("scoped_revision", "omit_revision", "omit_scope", "omit_owner_check")


class Record:
    def __init__(self, mode):
        self.mode = mode
        self.revisions = {"A": 1, "B": 1}
        self.answers = {}
        self.pending = set()
        self.receipts = {}

    def key(self, tenant, revision):
        if self.mode == "omit_revision":
            return tenant
        if self.mode == "omit_scope":
            return revision
        return tenant, revision

    def ask(self, tenant):
        key = self.key(tenant, self.revisions[tenant])
        if key in self.pending or key in self.answers:
            return False
        self.pending.add(key)
        return True

    def deliver(self, event):
        if event == "amend":
            self.revisions["A"] += 1
            self.ask("A")
            return
        answer = REPLIES[event]
        if self.mode != "omit_owner_check" and answer.signer != OWNERS[answer.tenant]:
            return
        key = self.key(answer.tenant, answer.revision)
        self.answers[key] = answer
        self.pending.discard(key)

    def decide(self, tenant, cost):
        answer = self.answers.get(self.key(tenant, self.revisions[tenant]))
        if answer is None:
            return "wait"
        return "allow" if cost <= answer.limit else "hold"

    def apply(self, tenant, operation, cost):
        key = tenant, operation
        if key in self.receipts:
            if self.receipts[key] != cost:
                return "conflict"
            return "already_applied"
        if self.decide(tenant, cost) == "allow":
            self.receipts[key] = cost
            return "applied"
        return "not_applied"


def expected(prefix, tenant, cost):
    # Oracle uses the event history, independent of the implementation's cache keys.
    if tenant == "B":
        known, cap = "other" in prefix, 300
    elif "amend" in prefix:
        known, cap = "new" in prefix, 100
    else:
        known, cap = bool({"old", "duplicate_old"}.intersection(prefix)), 200
    return ("allow" if cost <= cap else "hold") if known else "wait"


def schedules():
    for order in itertools.permutations(("amend", *REPLIES)):
        if order.index("amend") < order.index("new") and order.index("old") < order.index("duplicate_old"):
            yield order


class Inbox(AgentBase):
    def __init__(self, mode):
        super().__init__()
        self.name = "record"
        self.record = Record(mode)

    async def reply(self, msg):
        self.record.deliver(msg.content)
        decision = self.record.decide(msg.metadata["tenant"], msg.metadata["cost"])
        return Msg(self.name, decision, "assistant")


async def replay(mode, witness):
    inbox = Inbox(mode)
    for event in witness["prefix"]:
        result = await inbox(Msg("delivery", event, "user", metadata={
            "tenant": witness["tenant"], "cost": witness["cost"]}))
    assert result.content == witness["actual"]


def check_delivery(mode):
    wrong = 0
    shortest = None
    count = 0
    for order in schedules():
        count += 1
        record = Record(mode)
        record.ask("A")
        record.ask("B")
        bad = False
        for n, event in enumerate(order, 1):
            record.deliver(event)
            prefix = order[:n]
            for tenant, cost in itertools.product(OWNERS, (80, 150, 250)):
                want = expected(prefix, tenant, cost)
                actual = record.decide(tenant, cost)
                if want != actual:
                    bad = True
                    if shortest is None or n < len(shortest["prefix"]):
                        shortest = dict(prefix=list(prefix), tenant=tenant, cost=cost, expected=want, actual=actual)
        wrong += bad
    return {"schedules": count, "schedules_with_wrong_decisions": wrong, "shortest_witness": shortest}


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    results = {}
    for mode in MODES:
        result = check_delivery(mode)
        if result["shortest_witness"]:
            await replay(mode, result["shortest_witness"])
        else:
            await replay(mode, dict(prefix=["amend", "new", "old", "duplicate_old"], tenant="A", cost=150, actual="hold"))
        assert (result["schedules_with_wrong_decisions"] == 0) == (mode == "scoped_revision")
        results[mode] = result

    record = Record("scoped_revision")
    assert record.ask("A") and not record.ask("A") and record.ask("B")
    record.deliver("amend")
    record.deliver("old")
    assert ("A", 2) in record.pending and ("B", 1) in record.pending
    assert record.apply("A", "first", 80) == "not_applied"
    record.deliver("new")
    assert record.apply("A", "first", 80) == "applied"
    assert record.apply("A", "first", 80) == "already_applied"
    assert record.apply("A", "first", 99) == "conflict"
    record.deliver("other")
    assert record.apply("B", "first", 80) == "applied"
    assert len(record.receipts) == 2
    print(json.dumps(results, indent=2))
    if args.out:
        args.out.write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    asyncio.run(main())
