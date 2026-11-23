# Open Harness Bench

An open benchmark from [OutcomeRouter](https://outcomerouter.ai).

Tasks, checks and an [Inspect](https://inspect.aisi.org.uk/) eval for agent work that is paid only when it passes. It is the evaluation harness behind OutcomeRouter: the same task format, the same checks and the same rule that every check runs on every result, withheld ones included. Routing, pricing and accounts are not part of this repository.

Early: one recorded run so far (below). We will publish more as the [free beta](https://outcomerouter.ai/glossary/#free-beta) runs.

## Why

An agent's result depends on its whole harness: the task text, the starting files, the tools, the sandbox and the checks. Benchmarks rarely define those layers one by one, and almost never seal them, so two scores that look comparable often were not run the same way. Open Harness Bench defines each layer separately and pins it:

| Layer | What it fixes |
| --- | --- |
| Task | the task text and starting files, in a spec pinned by its digest |
| Checks | the commands that decide a pass, kept outside the worker's folder; withheld checks still count |
| Sandbox | a fresh copy of the starting files; protected files restored before any check runs |
| Worker | the agent command and its setup, recorded with every result |
| Verdict | pass only if every check passes, with each check's output kept |

Today the eval runs in Inspect's local sandbox. Sealing each layer in a hermetic container with no network is next; specs can already ask for `sandbox = "docker"`.

## Quick start

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
# one task, one agent
.venv/bin/inspect eval orbench_eval.py@outcome -T spec=examples/fizzbuzz/spec.toml -T agent=demo-good --model mockllm/model
# a whole folder of tasks as one eval
.venv/bin/inspect eval orbench_eval.py@suite -T tasks=tasks/humaneval -T agent=demo-good --model mockllm/model
.venv/bin/inspect view
```

Agents are shell commands in `~/.orbench/agents.toml`, written on first run with three demo agents and commented examples for Claude Code, Codex and Aider. Inspect does not call a model itself (`mockllm/model`): the agent runs as the solver inside the sandbox, and the task's checks are the scorer.

## Terms

The same words as the [OutcomeRouter glossary](https://outcomerouter.ai/glossary/).

| Term | Here | Inspect |
| --- | --- | --- |
| [Spec](https://outcomerouter.ai/glossary/#spec) | `spec.toml`: the task text, starting files and checks | Sample |
| [Check](https://outcomerouter.ai/glossary/#check-strength) | a command that exits 0 on pass, with a level: proved, verified, tested, judged or human | Scorer |
| [Withheld check](https://outcomerouter.ai/glossary/#withheld-check) | `withheld = true`: the agent never sees it; it still counts | |
| [Milestone check](https://outcomerouter.ai/glossary/#milestone-check) | a check that stops an attempt early when it fails | |
| [Worker](https://outcomerouter.ai/glossary/#worker) | an agent command, a person, or a team with shares | Solver |
| [Sandbox](https://outcomerouter.ai/glossary/#sandbox) | a fresh copy of the starting files; protected files are restored before checks run | Sandbox |
| [Attempt](https://outcomerouter.ai/glossary/#attempt) | one worker's try at one task | one sample run |
| [Verdict](https://outcomerouter.ai/glossary/#verdict) | pass only if every check passes; per-check results and output are kept | Score (`metadata.verdict`) |
| [Track record](https://outcomerouter.ai/glossary/#track-record) | verdicts collected across tasks | eval logs |
| Seed | a real task with a check (here: public benchmark tasks) | |
| Variant | a task made by changing a seed or a generator recipe | |
| Family | all variants made the same way (`tasks/synthetic-<family>`) | |

## Tasks

539 tasks, each validated before it was kept.

| Folder | Tasks | Source | How it was refined |
| --- | --- | --- | --- |
| `tasks/humaneval` | 164 | HumanEval via Inspect Evals | kept only if the starting files fail and the reference solution passes |
| `tasks/mbpp` | 200 | MBPP via Inspect Evals, random sample | same validation |
| `tasks/class_eval` | 85 | ClassEval via Inspect Evals, random sample | same validation; 15 of 100 sampled failed it and were dropped |
| `tasks/synthetic-*` | 90 | `tools/gen_tasks.py` (ledger, records, text) | 30 per family; rules composed to a known number of steps; checked against a reference on 400 random inputs |

Each imported task keeps the eval's own tests as a withheld check outside the agent's folder, and adds a visible check from the docstring examples where they are well formed. Rebuild or extend:

```sh
.venv/bin/pip install inspect-evals
.venv/bin/python tools/import_inspect.py mbpp --sample 200 --seed 1 --out tasks/mbpp
.venv/bin/python tools/gen_tasks.py --family ledger --n 30 --seed 1 --out tasks/synthetic-ledger
```

Public tasks may be in models' training data, so treat scores on them as priors, not proof. Fresh tasks from real work are what the record is built on.

## Results so far

One run, 14 tasks (MBPP and ClassEval), one attempt each:

| Agent | Pass rate | Cost per passing result |
| --- | --- | --- |
| claude-sonnet | 100% (14/14) | $0.60 |
| claude-haiku | 93% (13/14) | $0.22 |

Small sample. Under review for data quality.

## Other checks

- `tools/verify.py`: an [independent verifier](https://outcomerouter.ai/glossary/#independent-verifier) over A2A or HTTP, returning `{"pass": bool, "evidence": str}`.
- `tools/judge.py`: a judged check, a model scoring files against a rubric. Use a model from a different family than the worker.

## License

Code: Apache-2.0. Tasks derived from public datasets keep their licenses; see [NOTICE](NOTICE).
