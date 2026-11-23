#!/usr/bin/env python3
"""Independent-verifier check: send the output to a verifier and accept its verdict.

Two ways to reach a verifier, one verdict format {"pass": bool, "evidence": str}:

  A2A (verifiers that are agents, e.g. an audit firm's agent). Pass its agent card URL
  (or a2a:<endpoint>). We send A2A SendMessage with a data part {check, files} and read
  the verdict from the reply (a data part, or JSON in a text part, of the message or of
  the task's artifacts):
      python3 tools/verify.py https://auditor.example/.well-known/agent-card.json --check "..." out.csv

  HTTP (simple deterministic services, e.g. a buyer's reconciliation endpoint). Any other
  URL gets a JSON POST {check, files}:
      python3 tools/verify.py https://ci.example/verify --check "..." out.csv

Exit 0 = pass, 1 = fail, 2 = no verdict (unreachable, malformed or unclear reply), which fails
the check. OR_VERIFIER_TOKEN, if set, is sent as a bearer token.
"""
import argparse
import json
import os
import re
import sys
import urllib.request
import uuid
from pathlib import Path

MAX = 200_000


def post(url: str, body: dict, extra: dict | None = None) -> dict:
    h = {"Content-Type": "application/json", **(extra or {})}
    if os.environ.get("OR_VERIFIER_TOKEN"):
        h["Authorization"] = f"Bearer {os.environ['OR_VERIFIER_TOKEN']}"
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def verdict_in(obj) -> dict | None:
    """Find {"pass": bool, ...} in an A2A part, artifact or plain JSON."""
    if isinstance(obj, dict):
        if isinstance(obj.get("pass"), bool):
            return obj
        if isinstance(obj.get("data"), dict) and isinstance(obj["data"].get("pass"), bool):
            return obj["data"]
        if isinstance(obj.get("text"), str):
            for m in re.findall(r"\{[^{}]*\"pass\"[^{}]*\}", obj["text"]):
                try:
                    v = json.loads(m)
                    if isinstance(v.get("pass"), bool):
                        return v
                except json.JSONDecodeError:
                    pass
        for k in ("message", "task", "parts", "artifacts", "status", "result"):
            if k in obj:
                v = verdict_in(obj[k])
                if v:
                    return v
    if isinstance(obj, list):
        for x in reversed(obj):
            v = verdict_in(x)
            if v:
                return v
    return None


def a2a_endpoint(target: str) -> str:
    if target.startswith("a2a:"):
        return target[4:]
    with urllib.request.urlopen(target, timeout=60) as r:
        card = json.loads(r.read())
    for i in card.get("supportedInterfaces", []):
        if i.get("protocolBinding") == "JSONRPC":
            return i["url"]
    if card.get("url"):
        return card["url"]
    raise ValueError("agent card has no JSON-RPC endpoint")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="A2A agent card URL, a2a:<endpoint>, or an HTTP endpoint")
    ap.add_argument("--check", default="")
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()
    files = {f: Path(f).read_text(errors="replace")[:MAX] for f in a.files if Path(f).is_file()}
    payload = {"check": a.check, "files": files}
    use_a2a = a.target.startswith("a2a:") or a.target.rstrip("/").endswith((".well-known/agent-card.json",
                                                                            ".well-known/agent.json"))
    try:
        if use_a2a:
            msg = {"role": "ROLE_USER", "messageId": str(uuid.uuid4()), "parts": [
                {"text": "Verify this output against the check. Reply with JSON {\"pass\": bool, \"evidence\": str}."},
                {"data": payload}]}
            reply = post(a2a_endpoint(a.target), {"jsonrpc": "2.0", "id": 1, "method": "SendMessage",
                                                   "params": {"message": msg}}, {"A2A-Version": "1.0"})
            if "error" in reply:
                print(f"verifier: A2A error {reply['error'].get('code')}: {reply['error'].get('message')}")
                return 2
            v = verdict_in(reply.get("result"))
        else:
            v = verdict_in(post(a.target, payload))
    except Exception as e:
        print(f"verifier: no verdict ({type(e).__name__})")
        return 2
    if not v:
        print("verifier: no clear verdict in the reply")
        return 2
    print(f"verifier ({'A2A' if use_a2a else 'HTTP'}): {'pass' if v['pass'] else 'fail'}: {v.get('evidence', '')}")
    return 0 if v["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
