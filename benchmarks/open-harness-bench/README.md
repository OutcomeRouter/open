# Open Harness Bench

How do you tell whether a coding agent solved a task or just learned the examples? Give two workers the same FizzBuzz task. Both pass the examples in the prompt. Only one handles the larger inputs that the scorer tests afterward.

This public [OutcomeRouter](https://outcomerouter.ai) benchmark includes the task, both workers, the scorer, and 539 more tasks. The two demo workers are scripts, so anyone can reproduce the difference without a model account.

## What did the selection step contribute?

Across **90 synthetic tasks**, choosing the first proposal that passed the visible examples produced **46 passes**. Giving the selector one extra test produced **89 passes** on the same final checks. The extra test recovered 43 tasks. One ledger task still failed because its extra test asked about an empty ledger, a case both proposals already handled.

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

The first run creates `$ORBENCH_HOME/agents.toml` with demo commands and examples for adding a coding agent. Change the worker while keeping the task set, checks, and attempt budget fixed. To run a folder of tasks, use `orbench_eval.py@suite` and pass `-T tasks=tasks/humaneval` in place of the single spec argument.

Report passed attempts and total attempts together. For cost per passing result, divide **total measured spend across all attempts** by the number of passes. With zero passes, report the spend and zero passes. The local scorer records verdicts and check output. Collect actual spend from the worker or provider separately. A configured price is an estimate.

### Compare a single worker with a team

A stronger judge, more model calls, and better handoffs can each change the result. To test handoffs, give the same workers the same task and call budget. Change only how they share findings. Keep the scorer outside the team. For a learning router, freeze the routing rule before the evaluation split and include failed attempts in the cost.

The RSI Bench swarm task illustrates this design. It fixes the underlying model and evaluates a frozen graph on hidden problems. The verifier accounts for calls. Replit’s optimization study varied team size and found that some teams lost performance as they grew. [RSI Bench task](https://rsi-benchmark.com/tasks/agent-swarm-optimization) · [Replit experiment](https://frontier.replit.com/throwing-headcount-at-the-problem/)

Record each worker’s setup in its `agents.toml` entry. The labels identify the setup you claim to have run. Keep the command, actual call trace, and billed usage with your results.

```toml
[agents.layers]
model = "your-model-revision"
coordination = "shared-board"
reviewer = "same-model"
budget = "four calls per task"
```

Compare the logs from the walkthrough with the incomplete worker on the left:

```sh
python tools/compare.py "$ORBENCH_HOME"/logs/*demo-lazy*.eval "$ORBENCH_HOME"/logs/*demo-good*.eval
```

The report shows which tasks changed verdict in each direction. It rejects mismatched task sets, epochs, fixture contents, runner versions, and per-attempt time limits. The fixture hash covers the spec, starting files, and files under `checks/`. External tools, API revisions, and actual usage need separate records. The local runner cannot enforce an external agent’s model-call budget.

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
