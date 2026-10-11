# Lumen offset rulebook

This document is the normative settlement procedure for a valid batch. A report is correct exactly when it is the result of this procedure. Array order in `settled` and `unsettled` is not significant.

## Batch

A batch is a JSON object with `participants` and `payments`.

Each participant has `id` (string), `collateral` (integer greater than or equal to 0), `reserve` (integer, `0 <= reserve <= collateral`), and `ceiling` (integer, `ceiling >= collateral`).

Each payment has `id` (string), `debtor` (participant id), `creditor` (a different participant id), `amount` (integer greater than 0), `priority` (integer 0, 1, or 2), and `seq` (integer).

Every integer in a batch (`collateral`, `reserve`, `ceiling`, `amount`) is at most 1000000000. Participant ids are unique. Payment ids are unique. Ids are case-sensitive and are not trimmed. Lower priority numbers are more urgent: 0, then 1, then 2.

The engine is only required to follow this procedure on batches that already meet these constraints.

## Report

`python -m lumen.settle BATCH.json` reads that file and writes one JSON object to standard output, then exits 0. The object has exactly three keys.

- `settled`: array of payment ids that the procedure settles in full.
- `unsettled`: array of every other payment id, including a payment that was only partly paid.
- `balances`: object mapping every participant id to that participant's ending integer balance.

Starting balance of each participant is `collateral`. A payment moves its amount from the debtor to the creditor. Nothing else changes a balance except the offset fee below. All amounts, balances, and fees are integers. Integer division is floor division.

## Unilateral settlement

A payment's `floor` is a number that the debtor's balance must not go below. For priority 0 the floor is `reserve // 2` of the debtor, unless the debtor is strained (see Strain below). For priority 1 and priority 2 the floor is the debtor's full `reserve`. Priorities here are current priorities: aging (below) can lower a payment's priority number while the procedure runs, and the floor, the queues, partial settlement, and bundles all use the current priority.

A payment is affordable when both of these hold, using the balances at the moment it is considered.

- `balance[debtor] - amount >= floor`.
- `balance[creditor] + amount <= ceiling[creditor]`.

A unilateral settlement of an affordable payment moves its whole amount and the payment is settled.

Partial settlement applies to priority 2 only. When a priority 2 payment is not affordable, let `x = min(amount, balance[debtor] - reserve[debtor], ceiling[creditor] - balance[creditor])`. If `x >= 5`, move `x - x % 5` (the largest multiple of 5 not above `x`) now. The payment stays unsettled with the same id and seq, and its `amount` is reduced by what moved. If `x < 5` nothing moves. A priority 0 or priority 1 payment is never split.

Strain. A participant becomes strained the first time it is the debtor of a partial settlement that moves money, and stays strained until the procedure ends. For a strained debtor the priority 0 floor is its full `reserve`, the same as for the other priorities.

The queue of a priority is its unsettled payments. Within one pass the queue is ordered as follows, and the order is computed once at the start of the pass and does not change during the pass.

- Priority 0 and 1: increasing `(seq, id)`.
- Priority 2: larger `amount` first, using the amounts at the start of the pass, then increasing `(seq, id)`.

A unilateral phase for a priority is a sequence of passes. A pass walks the queue once. For each payment in turn it applies full settlement if affordable, otherwise partial settlement if allowed. It continues with the next payment in the same pass and never returns to an earlier payment during that pass. If a pass moved any money, another pass starts from the then-current queue. The phase ends when a full pass moves nothing. The phase "acted" if any pass moved money.

## Bundles

A bundle, for one priority, is a non-empty set `S` of unsettled payments of that priority (using their current amounts) that satisfies all of these. A bundle may hold any number of payments, may hold several payments between the same ordered pair of participants, and may be the union of several cycles. Payments of another priority are never part of it.

1. Closed. Every participant that is the debtor of a payment in `S` is also the creditor of at least one payment in `S`.
2. Funded. For a participant `p`, let `in(p)` be the amount `p` receives from payments in `S`, `out(p)` the amount `p` pays in `S`, and `fee(p) = (out(p) + 19) // 20` (5 percent of `out(p)`, rounded up; zero when `out(p)` is zero). Using balances from before the bundle, `0 <= balance[p] + in(p) - out(p) - fee(p) <= ceiling[p]` for every participant `p`. `reserve` does not apply to this test. A participant's balance may finish below `reserve` because of an offset.

Settling a bundle moves every payment in it at the same time and then subtracts `fee(p)` from each participant `p` once. Fees leave the system; ending balances do not sum to the collateral total.

The score of a bundle is compared in this order.

1. Larger sum of payment amounts wins.
2. If the sums are equal, the bundle that touches fewer distinct participants (debtors and creditors together) wins.
3. If still equal, the bundle with more payments wins.
4. If still equal, sort the payment ids of each bundle in increasing Unicode code-point order, then compare the two sorted lists from the first element onward; the bundle with the smaller id at the first position where they differ wins. Two different bundles never have the same sorted id list, so there is exactly one winning bundle whenever any bundle exists.

## Procedure

Repeat the following round until a round settles nothing. In a round, take priorities in the order 0, 1, 2 and stop the round at the first priority that acts.

1. Run the unilateral phase for the priority. If it acted, the round ends here.
2. Otherwise look for the winning bundle for that priority among its unsettled payments. If one exists, settle it, subtract the fees, and the round ends here.
3. Otherwise go on to the next priority.
4. Aging, applied once a round has acted at priority `q` (the round ends first), every payment that is still unsettled and whose current priority number is greater than `q` has its age increased by 1. A payment whose age reaches 3 has its priority number reduced by 1 and its age set back to 0. A payment moves at most one priority level per round, and a priority 0 payment never moves further. Every payment starts with age 0. Moving money on a payment (a partial settlement) does not change its age, and an age is not reset by anything other than reaching 3.

The next round starts again at priority 0, whatever priority acted. A round that reaches the end of priority 2 without acting ends the procedure, and no aging happens after it.

## Limits

A batch has at most 24 participants and at most 64 payments. `python -m lumen.settle` must finish every valid batch within 5 seconds on one CPU core, using only the Python 3.12 standard library plus pure Python source in `/app/src`. Third-party packages installed in the working container are not available to the grader. The grader rejects native code: no shared libraries, executables, or other compiled files under `/app/src`, no `ctypes`, `cffi`, `subprocess`, `multiprocessing`, or `importlib` imports, no calls to `exec`, `eval`, `__import__`, `os.system`, `os.popen`, `os.exec*`, `os.spawn*`, `os.fork*`, or `os.posix_spawn*`, and the graded process may not start other processes or threads. Because integers can reach 1000000000 while a partial settlement moves at most the balance that a debtor can spare, a priority 2 phase can consist of tens of millions of passes (see the last worked batch). The result of the procedure is defined by those passes, so a report is correct exactly when it equals what that many passes would produce. A batch is valid and graded even when running the passes one by one would not finish within 5 seconds, so a solution is expected to produce that same result without executing every pass. The winning bundle is not necessarily a single cycle and a batch can hold far more candidate bundles than can be listed one by one.

## Worked batches

Participants are written as `id collateral/reserve/ceiling`. Payments are `id debtor->creditor amount priority seq`.

Ring, with fees. `A 1/0/100`, `B 1/0/100`, `C 1/0/100`. Payments `p1 A->B 10` priority 0 seq 1, `p2 B->C 10` priority 0 seq 2, `p3 C->A 10` priority 0 seq 3. Nothing is affordable (each debtor has 1). The three payments form a closed set. Each participant pays and receives 10, the fee is `(10 + 19) // 20 = 1`, and each ends at `1 + 10 - 10 - 1 = 0`, which is funded. All three settle. Balances are 0, 0, 0. With a starting balance of 0 the fee would make the ring unfunded.

Scan order. `A 0/0/100`, `B 5/0/100`, `C 0/0/100`. Payments `p1 A->C 5` seq 1, `p2 B->A 5` seq 2, `p3 A->B 5` seq 3, all priority 0. The first pass skips `p1`, settles `p2` (A becomes 5), and then settles `p3` in that same pass (A returns to 0 and B returns to 5). The next pass still cannot settle `p1`. No bundle remains: `p1` alone is not closed, because A is its debtor and no remaining payment pays A. Settled: `p2`, `p3`. Balances: A 0, B 5, C 0. Restarting the list after `p2` would settle `p1` and is not this procedure.

Floor and ceiling. `A 10/8/100`, `B 8/0/10`, `C 0/0/100`. `p1 A->C 5` priority 0 seq 1 settles: the priority 0 floor is `8 // 2 = 4` and `10 - 5 = 5 >= 4`. A is at 5 and C is at 5, and the round ends. In the next round priority 0 has nothing left, so priority 1 runs. `p2 A->B 3` priority 1 seq 2 is not affordable: the priority 1 floor is 8 and `5 - 3 = 2 < 8`. `p3 B->C 4` priority 1 seq 3 is affordable for B (floor 0) and C has room, so it settles: B is at 4 and C is at 9. `p4 C->B 9` priority 1 seq 4: C could pay (`9 - 9 = 0 >= 0`), but `4 + 9 = 13 > 10`, the ceiling of B, so it is not affordable. Settled: `p1`, `p3`. Balances: A 5, B 4, C 9.

Ceiling blocks a payment. `A 10/0/100`, `B 8/0/10`. `p1 A->B 5` priority 0: A can afford it, but `8 + 5 = 13 > 10`, so it is not affordable and never settles (a lone payment is not a bundle). Balances stay A 10, B 8.

Partial settlement and queue order. `A 12/2/100`, `B 0/0/100`. Payments `p1 A->B 14` priority 2 seq 1 and `p2 A->B 6` priority 2 seq 0. The queue is `p1` then `p2` (larger amount first). `p1` is not affordable (`12 - 14 < 2`), `x = min(14, 12 - 2, 100) = 10`, so 10 moves: A is at 2 and `p1` stays unsettled with amount 4. `p2` is not affordable (`2 - 6 < 2`), `x = 0`, nothing moves. The next pass moves nothing. Balances: A 2, B 10. Both payments are unsettled. If `p2` had gone first it would have settled in full.

The tie chain. `A 2/2/100`, `B 8/8/100`, `C 2/2/100`. Payments `p1 A->B 10`, `p2 A->C 6`, `p3 C->B 4`, `p4 B->A 10`, all priority 1 with seq 1, 2, 3, 4. Nothing is affordable. Two bundles have the best sum 20: `{p1, p4}` touches two participants (A, B) and `{p2, p3, p4}` touches three (A, B, C). Fewer participants wins, even though the second bundle has more payments. `{p1, p4}` settles with fees of 1 for A and 1 for B (A ends at `2 + 10 - 10 - 1 = 1`, B at `8 + 10 - 10 - 1 = 7`). Balances: A 1, B 7, C 2. `p2` and `p3` stay unsettled and nothing more can settle.

Aging. `A 0/0/100`, `B 10/0/100`, `C 0/0/100`, `D 0/0/100`, `E 0/0/100`. Payments `r1 B->C 10` priority 1 seq 1, `r2 C->D 10` priority 0 seq 9, `r3 D->E 10` priority 1 seq 2, and `w E->A 10` priority 2 seq 3. Round 1: priority 0 cannot act and has no bundle, priority 1 settles `r1`. `w` has priority number 2, which is greater than 1, so its age becomes 1. Round 2: priority 0 settles `r2`, `w` ages to 2. Round 3: priority 0 has nothing, priority 1 settles `r3`, and `w` ages to 3, so its priority number becomes 1 and its age 0. Round 4 finds `w` payable at priority 1. Settled: all four payments. Balances: A 10, B 0, C 0, D 0, E 0.

Strain. `A 20/10/100`, `B 0/0/100`, `C 3/0/3`. `p1 A->B 30` priority 2 seq 1 cannot be paid in full, so `x = min(30, 20 - 10, 100) = 10` moves and A becomes strained with balance 10. From then on a priority 0 payment of A needs `balance - amount >= 10`, not `>= 5`.

Priorities are not finished once and for all. `A 0/0/100`, `B 10/0/100`, `C 0/0/100`. `p0 C->A 10` is priority 0 seq 5 and `p1 B->C 10` is priority 1 seq 1. Round 1: priority 0 cannot act (C has nothing) and has no bundle, so priority 1 acts and `p1` settles (C has 10). Round 2 starts at priority 0 and `p0` is now affordable. Settled: `p0`, `p1`. Balances: A 10, B 0, C 0.

Many passes. `A 10/0/100000`, `B 10/0/100000`. `p1 A->B 30` priority 2 seq 1 and `p2 B->A 30` priority 2 seq 2. Pass 1: `p1` (tie on amount, seq 1 first) moves 10, so A is at 0 and B at 20 and `p1` has 20 left; `p2` moves 20, so B is at 0, A is at 20, and `p2` has 10 left. Pass 2 orders the queue by the amounts at its start (`p1` 20, `p2` 10): `p1` is affordable in full and settles, then `p2` settles. Both payments settle in 2 passes and the balances return to A 10, B 10. With `30` replaced by `n` the same exchange takes about `n / 20` passes (51 for `n = 1000`, 5001 for `n = 100000`), and for `n = 1000000000` about 50 million passes, with the same ending balances.
