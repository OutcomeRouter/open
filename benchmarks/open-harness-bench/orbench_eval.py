"""Inspect AI eval for Open Harness Bench.

Each attempt is one Inspect eval: the task's workdir is copied into an Inspect
sandbox, the agent runs there as a solver (no model calls from Inspect), and the
spec's checks are the scorer. Logs land in ~/.orbench/inspect-logs, so
`inspect view --log-dir ~/.orbench/inspect-logs` shows every attempt.

You can also run it directly:

    inspect eval orbench_eval.py@outcome -T spec=examples/fizzbuzz/spec.toml \
        -T agent=demo-good --model mockllm/model
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import CORRECT, INCORRECT, Score, Target, accuracy, scorer
from inspect_ai.solver import Generate, TaskState, solver
from inspect_ai.util import sandbox

import orbench.core as orc


def _files(workdir: Path) -> dict[str, str]:
    out = {}
    for p in workdir.rglob("*"):
        if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts:
            out[str(p.relative_to(workdir))] = str(p)
    return out


def _spec_of(state: TaskState, spec: orc.Spec | None) -> orc.Spec:
    """A single-task eval passes its spec in; a suite keeps each sample's spec path in metadata."""
    return spec or orc.load_spec(state.metadata["spec"])


@solver
def shell_agent(agent: orc.Agent, spec: orc.Spec | None, tier: str):
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        spec_ = _spec_of(state, spec)
        sb = sandbox()
        await sb.write_file(".orbench/PROMPT.md", orc.prompt_for(spec_))
        import json as _json
        servers = {c["name"]: ({"type": c.get("type", "http"), "url": c["url"]} if "url" in c
                                else {"command": c["command"], "args": list(c.get("args", []))})
                   for c in spec_.companions}
        await sb.write_file(".orbench/mcp.json", _json.dumps({"mcpServers": servers}))
        here = (await sb.exec(["pwd"])).stdout.strip()
        cmd = agent.cmd.format(
            prompt_file=f"{here}/.orbench/PROMPT.md", workdir=here, demo=orc.REPO / "demo_agents", repo=orc.REPO, mcp_config=f"{here}/.orbench/mcp.json"
        )
        if tier == "wait-and-save":
            cmd = f"nice -n 10 bash -c {cmd!r}"
        res = await sb.exec(["bash", "-c", cmd], timeout=int(spec_.timeout_min * 60),
                            env={"ORBENCH_IN_AGENT": "1"})
        state.metadata["agent_exit"] = res.returncode
        state.metadata["agent_output"] = (res.stdout + res.stderr)[-4000:]
        return state

    return solve


@scorer(metrics=[accuracy()])
def spec_checks(spec: orc.Spec | None, deliver_to: str | None):
    async def score(state: TaskState, target: Target) -> Score:
        spec_ = _spec_of(state, spec)
        sb = sandbox()
        for rel in spec_.protect:  # restore protected files and folders so an agent cannot weaken them
            src = spec_.workdir / rel
            files = [src] if src.is_file() else [f for f in src.rglob("*") if f.is_file()] if src.is_dir() else []
            for f in files:
                await sb.write_file(str(f.relative_to(spec_.workdir)), f.read_bytes())
        results = []
        for c in spec_.checks:  # the harness runs every check, withheld ones too
            r = await sb.exec(["bash", "-c", orc.expand(c.cmd, spec_)], timeout=c.timeout_s)
            results.append({
                "name": c.name, "level": c.level, "withheld": c.withheld,
                "passed": r.returncode == 0, "output": (r.stdout + r.stderr)[-1500:],
            })
            if r.returncode != 0:
                break  # a failed check stops the attempt early
        passed = len(results) == len(spec_.checks) and all(x["passed"] for x in results)
        if passed and deliver_to:
            here = (await sb.exec(["pwd"])).stdout.strip()
            shutil.copytree(here, deliver_to, ignore=shutil.ignore_patterns(".orbench", "sandbox-tools", "__pycache__"),
                            dirs_exist_ok=True)
        failed = next((x["name"] for x in results if not x["passed"]), None)
        return Score(
            value=CORRECT if passed else INCORRECT,
            explanation="all checks passed" if passed else f"failed: {failed}",
            metadata={"verdict": "pass" if passed else "fail", "checks": results},
        )

    return score


def build_task(spec: orc.Spec, agent: orc.Agent, tier: str = "standard", deliver_to: str | None = None) -> Task:
    return Task(
        name=f"outcome-{agent.name}",
        dataset=[Sample(id=spec.digest, input=orc.prompt_for(spec), files=_files(spec.workdir),
                        metadata={"task_type": spec.type, "agent": agent.name, "tier": tier})],
        solver=shell_agent(agent, spec, tier),
        scorer=spec_checks(spec, deliver_to),
        sandbox="local",
    )


@task
def suite(tasks: str, agent: str, tier: str = "standard") -> Task:
    """Every spec.toml under `tasks` as one eval: one sample per task, scored by its own checks.

        inspect eval orbench_eval.py@suite -T tasks=tasks/humaneval -T agent=claude-haiku --model mockllm/model
    """
    ag = next((a for a in orc.load_agents() if a.name == agent), None)
    if ag is None:
        raise ValueError(f"no agent named {agent!r} in {orc.HOME / 'agents.toml'}")
    paths = sorted(Path(tasks).resolve().rglob("spec.toml"))
    if not paths:
        raise ValueError(f"no spec.toml under {tasks}")
    samples = []
    for p in paths:
        s = orc.load_spec(str(p))
        samples.append(Sample(id=p.parent.name, input=orc.prompt_for(s), files=_files(s.workdir),
                              metadata={"spec": str(p), "task_type": s.type, "agent": ag.name, "tier": tier}))
    return Task(name=f"suite-{Path(tasks).name}-{ag.name}", dataset=samples,
                solver=shell_agent(ag, None, tier), scorer=spec_checks(None, None), sandbox="local")


@task
def outcome(spec: str, agent: str, tier: str = "standard", deliver_to: str | None = None) -> Task:
    """Run one agent on one task as an Inspect eval."""
    s = orc.load_spec(spec)
    ag = next((a for a in orc.load_agents() if a.name == agent), None)
    if ag is None:
        raise ValueError(f"no agent named {agent!r} in {orc.HOME / 'agents.toml'}")
    return build_task(s, ag, tier, deliver_to)

