# Lumen offset rulebook

This document is the normative settlement procedure for a valid batch. A report is correct exactly when it is the result of this procedure. Array order in `settled` and `unsettled` is not significant.

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

A bundle, for the current priority, is a non-empty set `S` of unsettled payments of that priority that satisfies both conditions below. A bundle may hold any number of payments, may hold several payments between the same ordered pair of participants, and may be the union of several cycles. Payments of another priority are never part of it.

1. Closed. Every participant that is the debtor of a payment in `S` is also the creditor of at least one payment in `S`.
2. Funded. Let `net(p)` be the amount `p` receives from payments in `S` minus the amount `p` pays in `S`. Using balances from before the bundle, `balance[p] + net(p) >= 0` for every participant `p`. `reserve` does not apply to this test. A participant's balance may finish below `reserve` because of an offset.

The score of a bundle is compared in this order. A larger sum of payment amounts wins. If the sums are equal, the bundle with more payments wins. If the counts are also equal, sort the payment ids of each bundle in increasing Unicode code-point order, then compare the two sorted lists from the first element onward; the bundle with the smaller id at the first position where they differ wins. Two different bundles never have the same sorted id list, so there is exactly one winning bundle whenever any bundle exists.

## Procedure

Process priority 0 to completion, then priority 1, then priority 2. Payments of another priority are ignored until their own priority. For the current priority, repeat the following until both steps make no change.

1. Unilateral passes. Take the unsettled payments of this priority in increasing `(seq, id)` order. Walk that list once. When a payment is affordable, settle it immediately and continue later in the same list. Do not return to an earlier payment during that pass. If the pass settled at least one payment, start another pass from the current unsettled list. Stop the unilateral phase when a full pass settles nothing.

2. One offset. If any bundle exists, settle every payment of the single winning bundle at the same time, then go back to step 1. If none exists, this priority is finished.

## Limits

A batch has at most 24 participants and at most 64 payments. `python -m lumen.settle` must finish every valid batch within 5 seconds on one CPU core. The winning bundle is not necessarily a single cycle and a batch can hold far more candidate bundles than can be listed one by one.

## Worked batches

Participants are written as `id collateral/reserve`. Payments are `id debtor->creditor amount priority seq`.

Ring, with no starting cash. `A 0/0`, `B 0/0`, `C 0/0`. Payments `p1 A->B 10` priority 0 seq 1, `p2 B->C 10` priority 0 seq 2, `p3 C->A 10` priority 0 seq 3. Nothing is affordable. The three payments form a closed set with net zero for everyone, so it is a bundle and all three settle. Balances stay 0.

Scan order. `A 0/0`, `B 5/0`, `C 0/0`. Payments `p1 A->C 5` seq 1, `p2 B->A 5` seq 2, `p3 A->B 5` seq 3, all priority 0. The first pass skips `p1`, settles `p2` (A becomes 5), and then settles `p3` in that same pass (A returns to 0 and B returns to 5). The next pass still cannot settle `p1`. No bundle remains: `p1` alone is not closed, because A is its debtor and no remaining payment pays A. Settled: `p2`, `p3`. Balances: A 0, B 5, C 0. Restarting the list after `p2` would settle `p1` and is not this procedure.

Reserve does not bind the offset, and the id list breaks the tie. `A 10/8`, `B 0/0`, `C 0/0`. Payments `p1 A->B 9` seq 1, `p2 B->A 1` seq 2, `p3 A->C 9` seq 3, `p4 C->A 1` seq 4, all priority 0. Unilateral settlement of `p1` would leave A at 1, which is below the reserve 8, so the unilateral phase settles nothing. The bundles are `{p1, p2}` and `{p3, p4}`, each with sum 10 and two payments. `{p1, p2, p3, p4}` is closed but not funded: A would need 18 and receives only 2, so `balance + net` is -6. The reserve is ignored for the two-payment bundles (A ends at 2). The sorted id lists are `[p1, p2]` and `[p3, p4]`, and `p1 < p3`, so `p1` and `p2` settle and `p3` and `p4` stay unsettled. Balances: A 2, B 8, C 0.

More payments win a tie in the sum. `A 0/0`, `B 4/4`, `C 0/0`. Payments `p1 A->B 4`, `p2 B->A 8`, `p3 B->C 4`, `p4 C->A 4`, all priority 0 with seq 1, 2, 3, 4. Unilateral settlement settles nothing (A has 0, and B would fall below its reserve 4). `{p1, p2}` is a bundle with sum 12: B ends at 0, which is allowed. `{p1, p3, p4}` is a bundle with sum 12 and nets of zero. The sums tie, `{p1, p3, p4}` has more payments, so it wins. `{p1, p2, p3, p4}` has B at `4 + 4 - 8 - 4 = -4`, which is not funded. `p1`, `p3`, `p4` settle. Balances: A 0, B 4, C 0. `p2` stays unsettled.

Priority finishes before a later queue. `A 6/0`, `B 0/0`, `C 0/0`. `p1 A->C 6` is priority 1 seq 1. `p2 A->B 10` priority 0 seq 2 and `p3 B->A 4` priority 0 seq 3. Priority 0 has no affordable payment. `{p2, p3}` is a bundle: A nets -6 and has 6. So `p2` and `p3` settle and A is left at 0. Priority 1 then cannot settle `p1`. Settled: `p2`, `p3`. Balances: A 0, B 6, C 0.
