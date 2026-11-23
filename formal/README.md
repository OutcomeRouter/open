# Settlement model

`Settlement.tla` is a bounded TLA+ model of how OutcomeRouter settles a task. It is a model of the design, not a proof about the running service.

Invariants checked with the guard on (`SettlementGuard.cfg`):

- `NoPayWithoutPass`: no payment unless every check passed, withheld checks included.
- `ApprovalBindsToVersion`: no payment on an approval of an older contract version.
- `SettleAtMostOnce`: at most one settlement.

`SettlementNoGuard.cfg` turns the guard off; TLC then finds a counterexample: approve v1, edit to v2, settle on the v1 approval. Not modelled: disputes, priority races, budgets and per-attempt pay. Results: [`results.txt`](results.txt).

Run it (Java 11+ and [tla2tools.jar](https://github.com/tlaplus/tlaplus/releases)):

```sh
java -cp tla2tools.jar tlc2.TLC -deadlock -config SettlementGuard.cfg Settlement.tla
java -cp tla2tools.jar tlc2.TLC -deadlock -config SettlementNoGuard.cfg Settlement.tla
```
