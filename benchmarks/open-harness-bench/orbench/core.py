"""Core types for Open Harness Bench: task specs, checks, agents and prompts.

A task is a folder with a spec.toml, starting files and checks. Every check runs on every
result, withheld ones included. This package has no routing, pricing or accounts."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

HOME = Path(os.environ.get("ORBENCH_HOME", Path.home() / ".orbench"))
REPO = Path(__file__).resolve().parent.parent
LEVELS = ["proved", "verified", "tested", "judged", "human"]
TIERS = ["wait-and-save", "standard", "priority"]

DEFAULT_CONFIG = f'''# Benchmark agents. Each agent is a shell command run inside a fresh copy
# of the task's workdir. Template variables:
#   {{prompt_file}}  the task prompt (visible checks only)
#   {{workdir}}      the sandbox directory (also the working directory)
#   {{demo}}         the demo agents folder in the repo
# price_usd is your estimate of what one attempt costs, pass or fail.

[[agents]]
name = "demo-good"
cmd = "python3 {{demo}}/good.py {{prompt_file}}"
price_usd = 0.40

[[agents]]
name = "demo-flaky"
cmd = "python3 {{demo}}/flaky.py {{prompt_file}}"
price_usd = 0.15

[[agents]]
name = "demo-lazy"
cmd = "python3 {{demo}}/lazy.py {{prompt_file}}"
price_usd = 0.05

# Real agents: uncomment and set a price (what one attempt costs you, pass or fail).
# Claude Code gets only the spec's companion MCP servers (never OutcomeRouter itself), and
# none of your own CLAUDE.md, memory, skills or user settings.
#
# [[agents]]
# name = "claude-code"
# cmd = "CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude -p \\"$(cat {{prompt_file}})\\" --permission-mode acceptEdits --allowedTools Read,Edit,Write,Glob,Grep,Bash --setting-sources project,local --disable-slash-commands --strict-mcp-config --mcp-config {{mcp_config}}"
# price_usd = 1.50
#
# [[agents]]
# name = "codex"
# cmd = "codex exec --full-auto \\"$(cat {{prompt_file}})\\""
# price_usd = 1.20
#
# [[agents]]
# name = "aider"
# cmd = "aider --yes --no-git --message-file {{prompt_file}}"
# price_usd = 0.60
'''


# ---------------------------------------------------------------- model


@dataclass



@dataclass
class Check:
    name: str
    cmd: str
    level: str = "tested"
    withheld: bool = False
    timeout_s: int = 300
    milestone: str = ""  # run after this milestone; empty means at the end


@dataclass
class Spec:
    path: Path
    task: str
    workdir: Path
    type: str = "general"
    checks: list[Check] = field(default_factory=list)
    deadline_min: float = 60
    max_attempts: int = 3
    timeout_min: float = 30
    milestones: list[dict] = field(default_factory=list)  # [{name, task}], run in order
    sandbox: str = "local"  # "docker" runs checks in a container with no network
    image: str = "python:3.12-slim"
    protect: list[str] = field(default_factory=list)  # files restored from workdir before checks
    companions: list[dict] = field(default_factory=list)  # [{name, url}] or [{name, command}] MCP servers
    max_spend_usd: float = 0.0  # stop-loss: no new attempt once agent spend would pass this (0 = no cap)
    target_pass_chance: float = 0.9  # Standard picks the cheapest plan that reaches this chance of passing
    allow_secrets: bool = False  # the folder holds credentials on purpose (agents will see them)
    data_consent: bool = False  # the buyer allows this task's graded records to train models
    billing: str = "pay-on-pass"  # or "metered": agent spend passed through at cost plus METERED_FEE, pass or fail

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.path.read_bytes()).hexdigest()[:12]


@dataclass
class Agent:
    name: str
    cmd: str
    price_usd: float
    image: str = ""  # if set, the agent itself runs in this container image
    kind: str = "process"  # "process" runs cmd; "human" is a person (with their own agents) working from the queue
    pay: str = "per-attempt"  # or "on-pass": paid price_usd only when the attempt passes, nothing for a failure
    contact: str = ""  # how to reach a person who takes tasks; passed to OR_NOTIFY_CMD
    timeout_minutes: float = 0  # this agent's own time limit per attempt (humans need longer); 0 = the spec's
    data_consent: bool = False  # this agent (or person) allows its graded work records to train models
    members: list = field(default_factory=list)  # a team: [{name, kind: "agent"|"person", share}], one record together


def load_spec(path: str) -> Spec:
    p = Path(path).resolve()
    d = tomllib.loads(p.read_text())
    checks = [Check(**c) for c in d.get("checks", [])]
    for c in checks:
        if c.level not in LEVELS:
            sys.exit(f"check {c.name!r}: level must be one of {LEVELS}")
    if not checks:
        sys.exit("a spec needs at least one check: that is what defines a pass")
    milestones = d.get("milestones", [])
    names = {m["name"] for m in milestones}
    for c in checks:
        if c.milestone and c.milestone not in names:
            sys.exit(f"check {c.name!r} names unknown milestone {c.milestone!r}")
    for comp in d.get("companions", []):
        blob = json.dumps(comp).lower()
        if "name" not in comp or not ("url" in comp or "command" in comp):
            sys.exit("each companion needs a name and a url or a command")
        if "outcomerouter" in blob or "or_mcp" in blob:
            sys.exit(f"companion {comp['name']!r} points back at OutcomeRouter; agents may not start their own runs")
    if d.get("sandbox", "local") not in ("local", "docker"):
        sys.exit("sandbox must be local or docker")
    workdir = (p.parent / d.get("workdir", ".")).resolve()
    if not workdir.is_dir():
        sys.exit(f"workdir {workdir} does not exist")
    if not str(d.get("task", "")).strip():
        sys.exit("a spec needs a task")
    for c in checks:
        if not c.cmd.strip():
            sys.exit(f"check {c.name!r} has an empty cmd")
        if not 1 <= c.timeout_s <= 6 * 3600:
            sys.exit(f"check {c.name!r}: timeout_s must be between 1 and 21600")
    for rel in d.get("protect", []):
        if not (workdir / rel).resolve().is_relative_to(workdir):
            sys.exit(f"protect path {rel!r} leaves the workdir")
    for key, lo, hi in (("max_attempts", 1, 20), ("deadline_minutes", 1, 7 * 24 * 60),
                        ("attempt_timeout_minutes", 0.01, 24 * 60)):
        if key in d and not lo <= float(d[key]) <= hi:
            sys.exit(f"{key} must be between {lo} and {hi}")
    if d.get("billing", "pay-on-pass") not in ("pay-on-pass", "metered"):
        sys.exit("billing must be pay-on-pass or metered")
    if not 0.5 <= float(d.get("target_pass_chance", 0.9)) < 1:
        sys.exit("target_pass_chance must be at least 0.5 and below 1")
    if float(d.get("max_spend_usd", 0)) < 0:
        sys.exit("max_spend_usd must be 0 (no cap) or more")
    return Spec(
        path=p,
        task=d["task"].strip(),
        workdir=workdir,
        type=d.get("type", "general"),
        checks=checks,
        deadline_min=float(d.get("deadline_minutes", 60)),
        max_attempts=int(d.get("max_attempts", 3)),
        timeout_min=float(d.get("attempt_timeout_minutes", 30)),
        milestones=milestones,
        sandbox=d.get("sandbox", "local"),
        image=d.get("image", "python:3.12-slim"),
        protect=list(d.get("protect", [])),
        companions=list(d.get("companions", [])),
        max_spend_usd=float(d.get("max_spend_usd", 0)),
        target_pass_chance=float(d.get("target_pass_chance", 0.9)),
        allow_secrets=bool(d.get("allow_secrets", False)),
        data_consent=bool(d.get("data_consent", False)),
        billing=d.get("billing", "pay-on-pass"),
    )


def load_agents() -> list[Agent]:
    cfg = HOME / "agents.toml"
    if not cfg.exists():  # first run: write the demo agents
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text(DEFAULT_CONFIG)
    agents = [Agent(**a) for a in tomllib.loads(cfg.read_text()).get("agents", [])]
    for a in agents:
        if a.members:
            if any(m.get("kind") not in ("agent", "person") or "name" not in m for m in a.members):
                sys.exit(f"team {a.name!r}: each member needs a name and kind = agent or person")
            total = sum(float(m.get("share", 0)) for m in a.members)
            if abs(total - 1) > 1e-6:
                sys.exit(f"team {a.name!r}: member shares must add up to 1 (they add up to {total:g})")
    names = [a.name for a in agents]
    if len(set(names)) != len(names):
        sys.exit("agents.toml: agent names must be unique")
    for a in agents:
        if a.kind not in ("process", "human") or a.pay not in ("per-attempt", "on-pass"):
            sys.exit(f"agent {a.name!r}: kind must be process or human, pay must be per-attempt or on-pass")
        if a.kind == "human":
            hours = (a.timeout_minutes or 60) / 60
            if a.price_usd / hours < PEOPLE_MIN_HOURLY:
                sys.exit(f"agent {a.name!r}: a person's price must be at least ${PEOPLE_MIN_HOURLY:.0f} per hour of "
                         f"their time limit (${PEOPLE_MIN_HOURLY * hours:.2f} for {hours:g} h)")
        if a.kind == "process" and not a.cmd:
            sys.exit(f"agent {a.name!r}: a process agent needs a cmd")
        if not a.price_usd > 0:
            sys.exit(f"agent {a.name!r}: price_usd must be more than 0 (what one attempt costs, pass or fail)")
    if not agents:
        sys.exit("agents.toml lists no agents")
    return agents


# ---------------------------------------------------------------- ledger



def stages(spec: Spec) -> list[tuple[str, list[Check]]]:
    """Milestones in order, each with its checks; unassigned checks run at the end."""
    if not spec.milestones:
        return [("", spec.checks)]
    out = [(m["name"], [c for c in spec.checks if c.milestone == m["name"]]) for m in spec.milestones]
    tail = [c for c in spec.checks if not c.milestone]
    out[-1] = (out[-1][0], out[-1][1] + tail)
    return out


def prompt_for(spec: Spec, stage: str = "") -> str:
    checks = dict(stages(spec)).get(stage, spec.checks) if stage else spec.checks
    visible = [c for c in checks if not c.withheld]
    hidden = len(checks) - len(visible)
    lines = [spec.task]
    if stage:
        m = next(m for m in spec.milestones if m["name"] == stage)
        n = [x["name"] for x in spec.milestones].index(stage) + 1
        lines += ["", f"Milestone {n} of {len(spec.milestones)}: {stage}", m.get("task", "").strip(),
                  "Do only this milestone now. Earlier milestones are already done in this directory."]
    lines += ["", "Your result passes only if these checks pass (run in this directory):"]
    lines += [f"- [{c.level}] {c.name}: `{c.cmd}`" for c in visible]
    if hidden:
        lines += ["", f"There are also {hidden} withheld check(s) you cannot see. Solve the task properly."]
    if spec.companions:
        lines += ["", "You can call these companion agents (MCP servers) for context: "
                  + ", ".join(c["name"] for c in spec.companions) + "."]
    lines += ["", "Work only inside the current directory. Do not edit the checks."]
    return "\n".join(lines) + "\n"



def expand(cmd: str, spec: Spec, spec_dir: str | None = None) -> str:
    """Fill {spec_dir}: the folder holding spec.toml, where withheld check files live outside the workdir."""
    return cmd.replace("{spec_dir}", spec_dir or str(spec.path.parent))


