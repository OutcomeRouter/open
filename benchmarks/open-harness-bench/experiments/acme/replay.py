# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["agentscope==1.0.16", "mcp==1.23.1", "sqlalchemy[asyncio]>=2,<3", "tqdm>=4,<5"]
# ///
"""Run from any directory with uv run --python 3.12 path/to/replay.py."""
import argparse
import asyncio
import json
import re
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from agentscope.agent import AgentBase
from agentscope.message import Msg

HERE = Path(__file__).resolve().parent
MODES = ("private", "shared_chat", "shared_rule", "shared_rule_and_pending")


@dataclass(frozen=True)
class Rule:
    service: str
    limit: int
    through: str

    def allows(self, request):
        return (request["service"] == self.service and request["cost"] is not None
                and 0 <= request["cost"] <= self.limit
                and request["until"] is not None
                and date.fromisoformat(request["until"]) <= date.fromisoformat(self.through))

    def message(self):
        return f"I approve extra capacity for {self.service} up to ${self.limit} per change through {self.through}."

    @classmethod
    def from_message(cls, text):
        match = re.fullmatch(r"I approve extra capacity for (\w+) up to \$(\d+) per change through ([\d-]+)\.", text)
        if match:
            return cls(match[1], int(match[2]), match[3])
        return None


class Owner(AgentBase):
    def __init__(self):
        super().__init__()
        self.name = "Som"
        self.requests = []
        self.rule = Rule("checkout", 200, "2026-11-27")

    async def reply(self, msg):
        self.requests.append(msg.name)
        await asyncio.sleep(0)  # deliver the owner's reply after this wave's requests arrive
        if msg.metadata["cost"] is None:
            return Msg(self.name, "Check what the extension would cost first.", "assistant",
                       metadata={"decision": "request_cost", "rule": None})
        approved = self.rule.allows(msg.metadata)
        return Msg(self.name, self.rule.message() if approved else "Hold this change for review.",
                   "assistant", metadata={"decision": "allow" if approved else "hold",
                                          "rule": asdict(self.rule) if approved else None})


class Record:
    def __init__(self, owner, mode):
        self.owner = owner
        self.mode = mode
        self.answers = []
        self.pending = {}

    async def decide(self, request):
        for answer in reversed(self.answers):
            if self.mode == "private":
                continue
            if self.mode == "shared_chat":
                rule = Rule.from_message(answer.content)
            else:
                fields = answer.metadata["rule"]
                rule = Rule(**fields) if fields else None
            if rule and rule.allows(request.metadata):
                return "allow", "reused"

        fields = request.metadata
        # All requests in this fixture have the same tenant and action.
        key = (fields["service"], fields["cost"], fields["until"])
        share_pending = self.mode == "shared_rule_and_pending"
        if share_pending and key in self.pending:
            answer = await self.pending[key]
            return answer.metadata["decision"], "joined pending request"

        task = asyncio.create_task(self.owner(request))
        if share_pending:
            self.pending[key] = task
        try:
            answer = await task
            self.answers.append(answer)
            return answer.metadata["decision"], "asked Som"
        finally:
            if share_pending:
                self.pending.pop(key, None)


class Worker(AgentBase):
    def __init__(self, name, record):
        super().__init__()
        self.name = name
        self.record = record

    async def reply(self, msg):
        request = Msg(self.name, msg.content, "user", metadata=msg.metadata)
        decision, source = await self.record.decide(request)
        return Msg(self.name, decision, "assistant", metadata={"source": source})


async def run(rows, mode, concurrent):
    owner = Owner()
    record = Record(owner, mode)
    events = []

    async def act(row):
        worker = Worker(row["who"], record)
        request = Msg("driver", row["text"], "user",
                      metadata={k: row[k] for k in ("service", "cost", "until")})
        result = await worker(request)
        return {"who": worker.name, "wave": row["wave"], "request": row["text"],
                "decision": result.content, "source": result.metadata["source"], "expected": row["expected"]}

    for wave in sorted({r["wave"] for r in rows}):
        jobs = [act(r) for r in rows if r["wave"] == wave]
        events.extend(await asyncio.gather(*jobs) if concurrent else [await job for job in jobs])
    correct = sum(e["decision"] == e["expected"] for e in events)
    return {"mode": mode, "schedule": "burst" if concurrent else "serial",
            "interruptions": len(owner.requests), "correct": correct,
            "unauthorized": sum(e["decision"] == "allow" and e["expected"] != "allow" for e in events),
            "events": events}


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    rows = json.loads((HERE / "requests.json").read_text())
    runs = [await run(rows, mode, burst) for burst in (False, True) for mode in MODES]
    for r in runs:
        print(f"{r['schedule']:7} {r['mode']:25} {r['interruptions']} owner requests, "
              f"{r['correct']}/{len(rows)} correct, {r['unauthorized']} unauthorized")
    if args.out:
        args.out.write_text(json.dumps(runs, indent=2) + "\n")
    if any(r["correct"] != len(rows) for r in runs):
        raise SystemExit("Decision differed from the fixture's expected outcome")


if __name__ == "__main__":
    asyncio.run(main())
