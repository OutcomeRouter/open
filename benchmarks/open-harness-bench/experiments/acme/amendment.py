# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["agentscope==1.0.16", "mcp==1.23.1", "sqlalchemy[asyncio]>=2,<3", "tqdm>=4,<5"]
# ///
"""Test a replacement the fixed chat parser cannot read, then replace it again."""
import argparse
import asyncio
import json
from pathlib import Path

from agentscope.agent import AgentBase
from agentscope.message import Msg
from replay import Rule
from revision import DATE, Som


class Reader(AgentBase):
    def __init__(self, name, owner, posts, corrections, mode):
        super().__init__()
        self.name = name
        self.owner = owner
        self.posts = posts
        self.corrections = corrections
        self.mode = mode
        self.asked = 0

    async def reply(self, msg):
        revision = len(self.posts)
        rule = Rule.from_message(self.posts[-1].content)
        if self.mode == "structured":
            rule = self.owner.rules["checkout"]
        elif self.mode == "search_older" and rule is None:
            rule = next(r for p in reversed(self.posts) if (r := Rule.from_message(p.content)))
        elif self.mode == "clarify_revision" and rule is None:
            rule = self.corrections.get(revision)
        if rule is None:
            self.asked += 1
            if self.mode == "clarify_revision":
                # The owner confirms an interpretation of this exact revision.
                answer = await self.owner(Msg(self.name, "Confirm the current limit", "user",
                                              metadata={"clarify": True}))
                rule = Rule.from_message(answer.content)
                self.corrections[revision] = rule
            else:
                return await self.owner(msg)
        return Msg(self.name, "allow" if rule.allows(msg.metadata) else "hold", "assistant")


class PolicyOwner(Som):
    async def reply(self, msg):
        if msg.metadata.get("clarify"):
            return Msg(self.name, self.rules["checkout"].message(), "assistant")
        return await super().reply(msg)


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = {}
    for mode in ("search_older", "ask_per_request", "clarify_revision", "structured"):
        owner = PolicyOwner()
        posts = [owner.chat[0]]
        corrections = {}
        events = []
        for limit, wording, expected in (
            (100, "For checkout, halve the two-hundred-dollar cap. Friday still stands.",
             ("allow", "hold", "hold", "hold")),
            (300, "Raise the checkout cap to three hundred through Friday.",
             ("allow", "allow", "allow", "hold")),
        ):
            owner.publish("checkout", limit)
            posts.append(Msg(owner.name, wording, "assistant"))
            for cost, target in zip((80, 150, 250, 350), expected, strict=True):
                worker = Reader(f"operator-{len(events)}", owner, posts, corrections, mode)
                result = await worker(Msg("driver", f"Capacity for ${cost}?", "user",
                                          metadata={"service": "checkout", "until": DATE, "cost": cost}))
                events.append({"limit": limit, "cost": cost, "decision": result.content,
                               "expected": target, "asked": worker.asked})
        report[mode] = {"wrong": sum(e["decision"] != e["expected"] for e in events),
                        "owner_rechecks": sum(e["asked"] for e in events), "events": events}
        print(mode, report[mode]["wrong"], "wrong,", report[mode]["owner_rechecks"], "rechecks")
    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    asyncio.run(main())
