---- MODULE Clarification ----
EXTENDS Naturals

CONSTANTS Tenants, Ops, MaxRevision, CheckScope, CheckRevision, CheckOnce
VARIABLES revision, issued, receipts, effects
vars == <<revision, issued, receipts, effects>>

Messages == [tenant: Tenants, op: Ops, rev: 1..MaxRevision]
ReceiptSet == [tenant: Tenants, op: Ops, atRevision: 1..MaxRevision, used: Messages]

Init ==
  /\ revision = [t \in Tenants |-> 1]
  /\ issued = {}
  /\ receipts = {}
  /\ effects = [t \in Tenants |-> [o \in Ops |-> 0]]

Bump(t) ==
  /\ revision[t] < MaxRevision
  /\ revision' = [revision EXCEPT ![t] = @ + 1]
  /\ UNCHANGED <<issued, receipts, effects>>

(* Issued evidence may be delivered or reused arbitrarily late. *)
Issue(t, o) ==
  /\ issued' = issued \cup {[tenant |-> t, op |-> o, rev |-> revision[t]]}
  /\ UNCHANGED <<revision, receipts, effects>>

Commit(t, o, m) ==
  /\ m.op = o
  /\ (CheckScope => m.tenant = t)
  /\ (CheckRevision => m.rev = revision[t])
  /\ (CheckOnce => effects[t][o] = 0)
  /\ effects' = [effects EXCEPT ![t][o] = @ + 1]
  /\ receipts' = receipts \cup {
       [tenant |-> t, op |-> o, atRevision |-> revision[t], used |-> m]}
  /\ UNCHANGED <<revision, issued>>

Next == \E t \in Tenants :
          \/ Bump(t)
          \/ \E o \in Ops : Issue(t, o) \/ (\E m \in issued : Commit(t, o, m))

Spec == Init /\ [][Next]_vars

TypeOK ==
  /\ revision \in [Tenants -> 1..MaxRevision]
  /\ issued \subseteq Messages
  /\ receipts \subseteq ReceiptSet
  /\ effects \in [Tenants -> [Ops -> Nat]]

ScopeAtCommit == \A r \in receipts : r.used.tenant = r.tenant
RevisionAtCommit == \A r \in receipts : r.used.rev = r.atRevision
AtMostOnce == \A t \in Tenants, o \in Ops : effects[t][o] <= 1
====
