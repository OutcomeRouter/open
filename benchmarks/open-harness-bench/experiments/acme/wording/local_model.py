# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["mlx-lm==0.32.2", "mlx==0.32.4", "transformers==5.24.0"]
# ///
"""Generate a report with the pinned quantized model on Apple silicon."""
import argparse
import json
from functools import lru_cache
from pathlib import Path

from huggingface_hub import snapshot_download
from mlx_lm import generate, load
from study import DESCRIPTIONS, SYSTEM, parse_call, run_study, summary, tools_for

MODEL = "mlx-community/Qwen3-1.7B-4bit"
REV = "3b1b1768f8f8cf8351c712464f906e86c2b8269e"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    model, tok = load(snapshot_download(MODEL, revision=REV, allow_patterns=["*.safetensors", "*.json", "*.jinja", "*.txt"]))
    outputs = []

    @lru_cache(maxsize=None)
    def choose(arm, order, text):
        prompt = tok.apply_chat_template([{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
                    tools=tools_for(arm, order), tokenize=False, add_generation_prompt=True, enable_thinking=False)
        raw = generate(model, tok, prompt=prompt, max_tokens=96, verbose=False)
        choice = parse_call(raw)
        outputs.append({"arm": arm, "order": order, "request": text, "output": raw, "choice": choice})
        return choice

    rows = run_study(choose)
    report = {"model": MODEL, "revision": REV, "greedy": True,
              "description_tokens": {k: len(tok.encode(v, add_special_tokens=False)) for k,v in DESCRIPTIONS.items()},
              "runs": rows, "responses": outputs}
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    summary(rows)


if __name__ == "__main__":
    main()
