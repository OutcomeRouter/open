# Open Harness Bench

How do you tell whether a coding agent solved a task or just learned the examples? Give two workers the same FizzBuzz task. Both pass the examples in the prompt. Only one handles the larger inputs that the scorer tests afterward.

This public [OutcomeRouter](https://outcomerouter.ai) benchmark includes the task, both workers, the scorer, and 539 more tasks. The two demo workers are scripts, so anyone can reproduce the difference without a model account.

## What did the selection step contribute?

Across **90 synthetic tasks**, choosing the first proposal that passed the visible examples produced **46 passes**. Giving the selector one extra test produced **89 passes** on the same final checks. Repeating a published example with the same number of candidate checks kept the score at 46. The fresh test recovered 43 tasks. One ledger task still failed because its extra test asked about an empty ledger, a case both proposals already handled.

Each task had two scripted proposals in a fixed, shuffled order. One implemented the generated reference. The other memorized the three examples. Both arms saw the same proposals. Only the second arm could use one separately seeded input and its known answer before choosing. The final check used 400 generated inputs per task. This experiment isolates selection when a correct proposal is available and a trusted source can supply an expected answer. It does not estimate performance on production work or measure model reasoning.

```sh
# From benchmarks/open-harness-bench, Python 3.11+; no dependencies or API keys.
python3 tools/selection_ablation.py --out /tmp/selection-ablation.json
diff results/selection-ablation.json /tmp/selection-ablation.json
```

Inspect [every paired outcome](results/selection-ablation.json), the [one missed case](tasks/synthetic-ledger/ledger-d5-15), or the [experiment code](tools/selection_ablation.py).

## Run the comparison

Use Python 3.11 or newer, Bash, and Git on macOS or Linux.

```sh
git clone https://github.com/OutcomeRouter/open.git
cd open/benchmarks/open-harness-bench
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
export ORBENCH_HOME="$(mktemp -d)"
for agent in demo-good demo-lazy; do
  inspect eval orbench_eval.py@outcome -T spec=examples/fizzbuzz/spec.toml \
    -T agent="$agent" --model mockllm/model --log-dir "$ORBENCH_HOME/logs"
done
python tools/compare.py "$ORBENCH_HOME"/logs/*demo-lazy*.eval "$ORBENCH_HOME"/logs/*demo-good*.eval
inspect view --log-dir "$ORBENCH_HOME/logs"
```

| Worker | Visible checks | Withheld check on larger inputs | Verdict |
| --- | --- | --- | --- |
| demo-good | Pass | Pass | Pass |
| demo-lazy | Pass | Fail | Fail |

Open either sample in Inspect to see the check names, output, and verdict. Follow the same result through the [task definition](examples/fizzbuzz/spec.toml), [workers](demo_agents), and [scorer](orbench_eval.py). To run the regression tests, use `python -m unittest discover -s tests -v`.

## What a pass means

The solver runs a configured shell command in a fresh copy of the starting files. The worker prompt includes the visible checks. Before scoring, the harness restores the original files named in `protect`. The scorer runs checks in order and stops at the first failure. A pass requires every check to succeed.

The local runner executes with the user's permissions. Use trusted workers and task commands. Withheld checks are omitted from the prompt but remain readable in this public checkout. A spec digest identifies the contents of `spec.toml`. Record the Git commit as well to identify the versions of the fixtures and scorer.

## Compare agent setups

The first run creates `$ORBENCH_HOME/agents.toml` with demo commands and examples for adding a coding agent. Change the worker while keeping the task set, checks, and attempt budget fixed. After adding a coding worker named `my-worker`, this command runs two attempts per task. Use the same `--epochs` in both arms. The default is one attempt per task.

```sh
inspect eval orbench_eval.py@suite -T tasks=tasks/humaneval -T agent=my-worker \
  --epochs 2 --model mockllm/model --log-dir "$ORBENCH_HOME/suite-logs"
```

Report passed attempts and total attempts together. For cost per passing result, divide **total measured spend across all attempts** by the number of passes. With zero passes, report the spend and zero passes. The local scorer records verdicts and check output. Record timeouts and unscored attempts separately and include their spend. Collect actual spend from the worker or provider. A configured price is an estimate.

### Compare a single worker with a team

A stronger judge, more model calls, and better handoffs can each change the result. To test handoffs, give the same workers the same task and call budget. Change only how they share findings. Keep the scorer outside the team. For a learning router, freeze the routing rule before the evaluation split and include failed attempts in the cost.

RSI Bench fixes the underlying model and evaluates a frozen graph on hidden problems. Its teams can change roles, prompts, and routing together. Its verifier accounts for calls. Replit’s optimization study varied team size and found that some teams lost performance as they grew. [RSI Bench task](https://rsi-benchmark.com/tasks/agent-swarm-optimization) · [Replit experiment](https://frontier.replit.com/throwing-headcount-at-the-problem/)

Record each worker’s setup in its `agents.toml` entry. The labels identify the setup you claim to have run. Keep the command, actual call trace, and billed usage with your results.

```toml
[agents.layers]
model = "your-model-revision"
coordination = "shared-board"
reviewer = "same-model"
budget = "four calls per task"
```

The report shows which tasks changed verdict in each direction. It rejects mismatched task sets, epochs, fixture contents, runner versions, and per-attempt time limits. The fixture hash covers the spec, starting files, and files under `checks/`. External tools, API revisions, and actual usage need separate records. The local runner cannot enforce an external agent’s model-call budget.

## When do overlapping requests interrupt the owner?

In the [Acme AgentScope experiment](experiments/acme/replay.py), fresh agents request checkout capacity before a Friday sale. Som approves a service, a dollar limit per change, and an expiry. A Saturday extension needs a new decision. An extension with no cost estimate gets a request for its price.

Run `uv run --python 3.12 experiments/acme/replay.py` here. Each condition gets the same [requests](experiments/acme/requests.json). Agents use a fixed parser for Som’s chat message and an equivalent structured rule. In the burst schedule, private context produced eight questions. Shared chat and a shared rule each produced seven. Waiting for a pending answer with the same service, cost, and end date reduced that to five. The [recorded replay](results/acme-swarm.json) shows who asked, who waited, and which exceptions reached Som.

This is a local, single-process simulation using AgentScope agents and messages, with scripted decisions and no paid model calls. It measures interruptions under two schedules. Language understanding, cloud latency, and actual infrastructure spend require separate tests. [AgentScope paper](https://arxiv.org/abs/2407.17789)

### What if Som edits the limit while work is queued?

Run `uv run --python 3.12 experiments/acme/revision.py` to move Som’s edit before or after each step as Dana reads, hands off, and applies a request. A check at handoff still misses a limit change that arrives before application. Using the old limit can also hold up work after Som raises it. In this replay, reading the latest applicable chat message and reading the current structured rule produced the same decisions without asking Som again. Both assume the final check and action happen together. The fixture uses a fixed chat grammar and a single process. [Results and failing schedules](results/acme-revisions.json)

Track recovery by testing fresh workers on the same boundary cases immediately after an amendment and after each live request. The [convergence replay](experiments/acme/convergence.py) reports the first checkpoint where every probe is correct without an owner question and stays so through the remaining checkpoints. Each probe uses a disposable copy of the learned answers. A null recovery time means the strategy never met that criterion during the observation window. [Checkpoint results](results/acme-convergence.json)

What happens when the fixed parser misses a replacement? Run `uv run --python 3.12 experiments/acme/amendment.py`. Searching backward can resurrect an obsolete grant. Asking Som to confirm the meaning of a revision lets later workers reuse that answer until the next revision. The structured comparison assumes Som supplied the fields when publishing. [Amendment replay](results/acme-amendment.json)

The [late-answer experiment](experiments/acme/late_answers.py) tests reordered and repeated replies across two tenants. Run it with `uv run --python 3.12 experiments/acme/late_answers.py` to reproduce the [counterexamples](results/acme-late-answers.json). The [TLA+ model](../../formal/Clarification.tla) checks scope, revision at commit, and at-most-once application within its bounds. Run `python3 experiments/acme/crash_retry.py` to kill a SQLite writer before and after it commits a local outbox entry and retry under a changed limit.

### Does a tool description change how quickly workers recover?

A local Qwen3-1.7B model chooses one tool at a time after an owner changes a spending limit. One tool asks about the current request. Another, `resolve`, asks for a decision that future workers can reuse. The [experiment](experiments/acme/wording/study.py) compares four descriptions of `resolve`. Follow-up tests vary the descriptions of two competing tools, add a third tool ordering, and give workers the confirmed limit directly. Each wording runs on two amendments with three tool orderings. Recovery starts at the first checkpoint where the limit is confirmed and fresh workers answer all four probes correctly through the last checkpoint. The probes cover costs below, at, and above the limit and a missing price.

None of the 126 live requests across 42 runs elicited the reusable decision. With the original wording the model asked the owner nine times across 18 live requests. Changing both competing descriptions cut that to zero, but produced six unsupported approval proposals. That variant made the expected choice on eight of 24 final probes. In a separate control that supplied the confirmed limit, it scored nine of 24. These are repeated conditions on one model and two fictional amendments. No proposal changed infrastructure.

Inspect the [raw model calls and results](results/acme-wording.json). Run `python3 experiments/acme/wording/study.py results/acme-wording.json` to rescore the saved calls. To generate them again on Apple silicon, use `uv run --python 3.12 experiments/acme/wording/local_model.py --out /tmp/acme-wording.json`. Owner replies are scripted. This measures first tool choices and revision reuse on a three-request stream.

### Does the policy language change the result?

Som’s grant covers checkout capacity through Friday, up to $200 per change. Run `uv run --python 3.12 experiments/acme/compare_policies.py --timing` to compare [CEL, Rego, and Cedar](experiments/acme/policies) with a Python reference. Every evaluator allowed the same six boundary cases and referred the other 42 for owner review. Each reproduced the same decisions and interruptions under both schedules. [Results by evaluator](results/acme-policies.json)

The adapters receive typed inputs. They check an existing grant for one action in one tenant. The replay supplies owner identity and handles pending requests outside the policy engine. Timings include local Python conversion and evaluation through cel-python, regopy, or cedarpy. They exclude network calls and policy loading.

## Task corpus

| Collection | Tasks | Source |
| --- | ---: | --- |
| [HumanEval](tasks/humaneval) | 164 | HumanEval via Inspect Evals |
| [MBPP](tasks/mbpp) | 200 | Sample from MBPP via Inspect Evals |
| [ClassEval](tasks/class_eval) | 85 | Tasks retained from a sample of 100 |
| Synthetic | 90 | 30 each from the ledger, records, and text generators |

Run `python3 tools/audit_corpus.py` to check the corpus locally. The audit runs the starting files for every task. It also regenerates reference solutions for all 90 synthetic tasks. The imported tasks have no local reference in this checkout.

The [importer](tools/import_inspect.py) checks that the starting files fail and the reference solution passes. The [generator](tools/gen_tasks.py) builds synthetic tasks from a seed. Public tasks can occur in training data. Use fresh held-out tasks to test whether a result carries over to your workload.

Code uses Apache-2.0. See [NOTICE](NOTICE) for dataset licenses.
