#!/usr/bin/env python3
"""A judged check: a model scores files against a rubric. Exit 0 = pass, 1 = fail, 2 = no verdict.

    python3 tools/judge.py --rubric "Every claim cites a source that supports it" report.md

The judge command reads the prompt on stdin and must print JSON {"pass": bool, "reason": str}.
Default: Claude Haiku with no MCP servers. Override with OR_JUDGE_CMD, ideally a model from a
different family than the agent that did the work.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

DEFAULT = "CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude -p --model haiku --setting-sources project,local --disable-slash-commands --strict-mcp-config --mcp-config '{\"mcpServers\":{}}'"
MAX = 60_000


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rubric", required=True)
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()
    parts = []
    for f in a.files:
        p = Path(f)
        if not p.is_file():
            print(f"judge: missing file {f}")
            return 1
        parts.append(f"--- {f} ---\n{p.read_text(errors='replace')[:MAX]}")
    prompt = (
        "You are a strict reviewer. Decide whether the work below meets the rubric. "
        "Judge only what is in the files.\n\n"
        f"Rubric: {a.rubric}\n\n" + "\n\n".join(parts) +
        '\n\nReply with only one line of JSON: {"pass": true or false, "reason": "one sentence"}'
    )
    r = subprocess.run(["bash", "-c", os.environ.get("OR_JUDGE_CMD", DEFAULT)], input=prompt,
                       capture_output=True, text=True, timeout=300)
    found = re.findall(r"\{[^{}]*\"pass\"[^{}]*\}", r.stdout)
    if not found:
        print(f"judge: no verdict (exit {r.returncode})")
        return 2
    v = json.loads(found[-1])
    print(f"judge: {'pass' if v.get('pass') else 'fail'}: {v.get('reason', '')}")
    return 0 if v.get("pass") is True else 1


if __name__ == "__main__":
    sys.exit(main())
