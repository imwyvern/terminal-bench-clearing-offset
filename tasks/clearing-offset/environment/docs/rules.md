# Lumen offset rulebook

This document is the normative settlement procedure for a valid batch. A report is correct exactly when it is the result of this procedure. Array order in `settled` and `unsettled` is not significant. Do not treat a larger settled total as better: the procedure is not an optimization.

## Batch

A batch is a JSON object with `participants` and `payments`.

Each participant has `id` (string), `collateral` (integer greater than or equal to 0), and `reserve` (integer, `0 <= reserve <= collateral`).

Each payment has `id` (string), `debtor` (participant id), `creditor` (a different participant id), `amount` (integer greater than 0), `priority` (integer 0, 1, or 2), and `seq` (integer).

Participant ids are unique. Payment ids are unique. Ids are case-sensitive and are not trimmed. Lower priority numbers are more urgent: 0, then 1, then 2.

The engine is only required to follow this procedure on batches that already meet these constraints.

## Report

`python -m lumen.settle BATCH.json` reads that file and writes one JSON object to standard output, then exits 0. The object has exactly three keys.

- `settled`: array of payment ids that the procedure settles.
- `unsettled`: array of every other payment id.
- `balances`: object mapping every participant id to that participant's ending integer balance.

Starting balance of each participant is `collateral`. Settling a payment subtracts `amount` from the debtor and adds `amount` to the creditor. An offset settles its payments at the same time by applying the sum of those changes. Nothing else changes a balance. The sum of ending balances equals the sum of collateral.

## Definitions

A payment is affordable for a unilateral settlement when `balance[debtor] - amount >= reserve[debtor]` using the balances at the moment it is considered.

A cycle uses unsettled payments of one priority only. Between an ordered pair of participants, the cycle uses the single unsettled payment of that priority with the smallest `seq`, then the smallest `id`. Pairs with no such payment are absent.

A 2-cycle on participants `u` and `v` (`u` sorts before `v`) exists when both directed edges exist. Its canonical tuple is `(u, v)`.

A 3-cycle on three participants exists for a direction when all three directed edges exist. Let `s` be the earliest id of the three, and let `x` and `y` be the other two with `x` sorting before `y`. The two directions are the tuples `(s, x, y)` and `(s, y, x)`. Keep each direction that has all three edges. They are different candidates.

A cycle is feasible when, for every participant, `balance + net >= 0`, using balances from before the cycle and the simultaneous net of its payments. `reserve` does not apply to this test. A participant's balance may finish below `reserve` because of an offset.

The score of a feasible cycle is compared in this order: larger sum of payment amounts wins; if those sums are equal, the shorter tuple wins; if length is also equal, the lexicographically smaller canonical tuple wins. String order is Unicode code-point order.

## Procedure

Process priority 0 to completion, then priority 1, then priority 2. Payments of another priority are ignored until their own priority. For the current priority, repeat the following until both steps make no change.

1. Unilateral passes. Take the unsettled payments of this priority in increasing `(seq, id)` order. Walk that list once. When a payment is affordable, settle it immediately and continue later in the same list. Do not return to an earlier payment during that pass. If the pass settled at least one payment, start another pass from the current unsettled list. Stop the unilateral phase when a full pass settles nothing.

2. One offset. If any feasible cycle exists, settle every payment on the single winning cycle at the same time, then go back to step 1. If none exists, this priority is finished.

## Worked batches

Participants are written as `id collateral/reserve`. Payments are `id debtor->creditor amount priority seq`.

Ring, with no starting cash. `A 0/0`, `B 0/0`, `C 0/0`. Payments `p1 A->B 10` priority 0 seq 1, `p2 B->C 10` priority 0 seq 2, `p3 C->A 10` priority 0 seq 3. Nothing is affordable. The 3-cycle nets to zero, so it is feasible and all three payments settle. Balances stay 0.

Scan order. `A 0/0`, `B 5/0`, `C 0/0`. Payments `p1 A->C 5` seq 1, `p2 B->A 5` seq 2, `p3 A->B 5` seq 3, all priority 0. The first pass skips `p1`, settles `p2` (A becomes 5), and then settles `p3` in that same pass (A returns to 0 and B returns to 5). The next pass still cannot settle `p1`. No cycle remains. Settled: `p2`, `p3`. Balances: A 0, B 5, C 0. Restarting the list after `p2` would settle `p1` and is not this procedure.

Reserve does not bind the offset, and the tuple breaks the tie. `A 10/8`, `B 0/0`, `C 0/0`. Payments `p1 A->B 9` seq 1, `p2 B->A 1` seq 2, `p3 A->C 9` seq 3, `p4 C->A 1` seq 4, all priority 0. Unilateral settlement of `p1` would leave A at 1, which is below the reserve 8, so the unilateral phase settles nothing. Both 2-cycles have amount 10 and are feasible because the reserve is ignored (`A` ends at 2). Tuple `(A, B)` beats `(A, C)`, so `p1` and `p2` settle and `p3` and `p4` stay unsettled. Balances: A 2, B 8, C 0.

Priority finishes before a later queue. Same participants as the scan is not required. `A 6/0`, `B 0/0`, `C 0/0`. `p1 A->C 6` is priority 1 seq 1. `p2 A->B 10` priority 0 seq 2 and `p3 B->A 4` priority 0 seq 3. Priority 0 has no affordable payment. The offset nets A by -6 and is feasible, so `p2` and `p3` settle and A is left at 0. Priority 1 then cannot settle `p1`. Settled: `p2`, `p3`. Balances: A 0, B 6, C 0.
