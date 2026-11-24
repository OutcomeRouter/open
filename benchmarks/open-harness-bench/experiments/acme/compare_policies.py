# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["agentscope==1.0.16", "mcp==1.23.1", "sqlalchemy[asyncio]>=2,<3", "tqdm>=4,<5", "cel-python==0.5.0", "regopy==1.5.2", "cedarpy==4.12.2"]
# ///
"""Compare evaluators of Som's capacity grant. Missing evidence goes to the owner."""
import argparse
import asyncio
import itertools
import json
import platform
import statistics
import time
from datetime import date
from pathlib import Path

import celpy
from cedarpy import Decision, PolicySet, is_authorized
from celpy.adapter import json_to_cel
from regopy import Interpreter

from replay import HERE, MODES, Rule, run

POLICIES = HERE / "policies"
GRANT = Rule("checkout", 200, "2026-11-27")


def inputs(rule, request):
    # One typed request format: missing optional evidence is absent, dates are whole days.
    data = {"service": request["service"]}
    if request.get("cost") is not None:
        if type(request["cost"]) is not int:
            raise ValueError("cost must be a whole number of dollars")
        data["cost"] = request["cost"]
    if request.get("until") is not None:
        data["until"] = date.fromisoformat(request["until"]).toordinal()
    grant = {"service": rule.service, "limit": rule.limit, "through": date.fromisoformat(rule.through).toordinal()}
    return {"request": data, "grant": grant}


def evaluators():
    env = celpy.Environment()
    cel = env.program(env.compile((POLICIES / "capacity.cel").read_text()))
    rego = Interpreter()
    rego.add_module("capacity", (POLICIES / "capacity.rego").read_text())
    cedar = PolicySet.from_str((POLICIES / "capacity.cedar").read_text())

    def python_eval(data):
        r, g = data["request"], data["grant"]
        return (r["service"] == g["service"] and "cost" in r and 0 <= r["cost"] <= g["limit"]
                and "until" in r and r["until"] <= g["through"])

    def cel_eval(data):
        return bool(cel.evaluate({key: json_to_cel(value) for key, value in data.items()}))

    def rego_eval(data):
        rego.set_input(data)
        result = rego.query("answer = data.acme.allow")
        if not result.ok():
            raise RuntimeError(str(result))
        return json.loads(str(result))["bindings"]["answer"] is True

    def cedar_eval(data):
        r, g = data["request"], data["grant"]
        context = {k: v for k, v in r.items() if k != "service"}
        context.update(limit=g["limit"], through=g["through"],
                       approvedService={"__entity": {"type": "Service", "id": g["service"]}})
        result = is_authorized({"principal": 'Worker::"requester"', "action": 'Action::"addCapacity"',
                                "resource": {"type": "Service", "id": r["service"]}, "context": context}, cedar, [])
        if result.diagnostics.errors:
            raise RuntimeError(str(result.diagnostics.errors))
        return result.decision == Decision.Allow

    return {"Python": python_eval, "CEL (cel-python)": cel_eval,
            "Rego (regopy)": rego_eval, "Cedar (cedarpy)": cedar_eval}


def boundary_cases():
    # The expected set is enumerated independently of the four policies.
    for service, cost, until in itertools.product(
        ("checkout", "billing"), (None, -1, 0, 199, 200, 201),
        (None, "2026-11-26", "2026-11-27", "2026-11-28")
    ):
        request = {"service": service, "cost": cost, "until": until}
        expected = service == "checkout" and cost in (0, 199, 200) and until in ("2026-11-26", "2026-11-27")
        yield request, expected


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--timing", action="store_true", help="show local warm adapter timings")
    args = parser.parse_args()
    rows = json.loads((HERE / "requests.json").read_text())
    cases = list(boundary_cases())
    baseline = [await run(rows, mode, burst) for burst in (False, True) for mode in MODES]
    report = {}
    for name, evaluate in evaluators().items():
        def allows(rule, request):
            return evaluate(inputs(rule, request))

        accepted = 0
        for request, expected in cases:
            actual = allows(GRANT, request)
            if actual != expected:
                raise AssertionError((name, request, expected, actual))
            accepted += actual
        runs = [await run(rows, mode, burst, allows) for burst in (False, True) for mode in MODES]
        if runs != baseline or any(r["correct"] != len(rows) for r in runs):
            raise AssertionError(f"{name} diverged in the AgentScope replay")
        report[name] = {"boundary_cases": len(cases), "auto_allow": accepted,
                        "refer_to_owner": len(cases) - accepted, "replays_matched": len(runs),
                        "burst_interruptions": {r["mode"]: r["interruptions"] for r in runs if r["schedule"] == "burst"}}
        print(name, json.dumps(report[name]))
        if args.timing:
            durations = []
            for _ in range(7):
                start = time.perf_counter_ns()
                for request, _ in cases:
                    allows(GRANT, request)
                durations.append((time.perf_counter_ns() - start) / (len(cases) * 1000))
            print(f"  {statistics.median(durations):.1f} us/decision, warm adapter, {platform.machine()}")
    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    asyncio.run(main())
