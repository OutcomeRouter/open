---------------------------- MODULE Settlement ----------------------------
(* OutcomeRouter settlement, bounded model.
   A contract has a version. A buyer approves one version. Work runs against
   a version. Checks (some withheld) run on the result. Settlement pays the
   price at most once, and only for a passing result of the approved version. *)
EXTENDS Naturals, FiniteSets

CONSTANTS Checks, Withheld, MaxVersion, Price, AuthorShare, Fee, GUARD
ASSUME Withheld \subseteq Checks /\ AuthorShare + Fee <= Price

None == 999

VARIABLES version,      \* current contract version
          approved,     \* version the buyer approved, or None
          workVersion,  \* version the submitted work was done against, or None
          verdict,      \* check -> "pending" | "pass" | "fail"
          paid,         \* number of settlements
          paidVersion,  \* contract version at settlement, or None
          paidApproval, \* approved version at settlement, or None
          payout        \* [work, authors, fee] at settlement

vars == <<version, approved, workVersion, verdict, paid, paidVersion, paidApproval, payout>>

Init == /\ version = 0 /\ approved = None /\ workVersion = None
        /\ verdict = [k \in Checks |-> "pending"]
        /\ paid = 0 /\ paidVersion = None /\ paidApproval = None
        /\ payout = [work |-> 0, authors |-> 0, fee |-> 0]

Edit == /\ version < MaxVersion /\ paid = 0
        /\ version' = version + 1
        /\ approved' = IF GUARD THEN None ELSE approved   \* an edit clears approval
        /\ workVersion' = None
        /\ verdict' = [k \in Checks |-> "pending"]
        /\ UNCHANGED <<paid, paidVersion, paidApproval, payout>>

Approve == /\ approved = None /\ paid = 0
           /\ approved' = version
           /\ UNCHANGED <<version, workVersion, verdict, paid, paidVersion, paidApproval, payout>>

Submit == /\ approved # None /\ workVersion = None /\ paid = 0
          /\ workVersion' = version
          /\ UNCHANGED <<version, approved, verdict, paid, paidVersion, paidApproval, payout>>

RunCheck(k) == /\ workVersion # None /\ verdict[k] = "pending"
               /\ \E v \in {"pass", "fail"} : verdict' = [verdict EXCEPT ![k] = v]
               /\ UNCHANGED <<version, approved, workVersion, paid, paidVersion, paidApproval, payout>>

AllPass == \A k \in Checks : verdict[k] = "pass"

CanSettle == IF GUARD
             THEN approved = version /\ workVersion = version /\ AllPass /\ paid = 0
             ELSE approved # None /\ workVersion # None /\ AllPass

Settle == /\ CanSettle
          /\ paid' = paid + 1
          /\ paidVersion' = version /\ paidApproval' = approved
          /\ payout' = [work |-> Price - AuthorShare - Fee, authors |-> AuthorShare, fee |-> Fee]
          /\ UNCHANGED <<version, approved, workVersion, verdict>>

Next == Edit \/ Approve \/ Submit \/ Settle \/ \E k \in Checks : RunCheck(k)
Spec == Init /\ [][Next]_vars

(* ---- invariants ---- *)
NoPayWithoutPass       == paid > 0 => AllPass                       \* withheld checks included
ApprovalBindsToVersion == paid > 0 => paidApproval = paidVersion    \* no pay on a stale approval
SettleAtMostOnce       == paid <= 1
PayoutConserved        == paid > 0 => payout.work + payout.authors + payout.fee = Price
=============================================================================
