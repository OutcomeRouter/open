"""Content identifiers used to match attempts in a paired comparison."""
import hashlib
from pathlib import Path


def fingerprint(parts):
    digest = hashlib.sha256()
    for label, data in parts:
        for value in (label.encode(), data):
            digest.update(len(value).to_bytes(8, "big"))
            digest.update(value)
    return digest.hexdigest()


def tree(root: Path):
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if path.is_file() and not {".git", "__pycache__"}.intersection(rel.parts):
            yield rel.as_posix(), path.read_bytes()


def task_identity(spec):
    parts = [("spec.toml", spec.path.read_bytes())]
    for label, root in (("work", spec.workdir), ("checks", spec.path.parent / "checks")):
        parts.extend((f"{label}/{name}", data) for name, data in tree(root))
    return fingerprint(parts)


def experiment_metadata(spec, agent, tier):
    from importlib.metadata import version

    root = Path(__file__).resolve().parents[1]
    runner = ("orbench_eval.py", "orbench/core.py", "orbench/provenance.py")
    return {
        "task_type": spec.type,
        "agent": agent.name,
        "tier": tier,
        "fixture_sha256": task_identity(spec),
        "runner_sha256": fingerprint((name, (root / name).read_bytes()) for name in runner),
        "inspect_version": version("inspect-ai"),
        "sandbox": spec.sandbox,
        "timeout_minutes": spec.timeout_min,
        "command_sha256": fingerprint([("template", agent.cmd.encode())]),
        "worker_layers": dict(agent.layers),
    }
