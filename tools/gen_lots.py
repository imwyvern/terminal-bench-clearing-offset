"""Random generator used to mine the 9xx-multi-lots cases (families b and c).

Batches with up to 14 participants and 12 (family b) or 24 (family c) payments, mixing
amounts up to 10^9 with small ones, so several priority 2 payments run long multi-hop
partial-lot phases at the same time. The mined batches were the ones on which
pass-acceleration engines written during trials of 1.4.0 fell back to slow pass-by-pass
work, while the oracle needs well under a second. Their reports were checked by replaying
the literal procedure (tools/verify_pp.py).
"""
import random


def lots_batch(rng: random.Random, fam: str) -> dict:
    n = rng.randint(2, 8 if fam == "a" else 14)
    ids = [f"P{i}" for i in range(n)]
    big = fam in ("b", "c")
    parts = []
    for pid in ids:
        c = rng.choice([0, 5, 10, 40, rng.randint(0, 10**9 if big else 200)])
        r = rng.choice([0, c // 2, c, max(0, c - 7)])
        ceiling = min(10**9, c + rng.choice([0, 7, 30, rng.randint(0, 10**9)]))
        parts.append({"id": pid, "collateral": c, "reserve": r, "ceiling": max(ceiling, c)})
    pays = []
    for k in range(rng.randint(2, 12 if fam != "c" else 24)):
        d, c = rng.sample(ids, 2)
        a = rng.choice([rng.randint(1, 40), rng.randint(1, 10**9 if big else 500)])
        pays.append({"id": f"q{k}", "debtor": d, "creditor": c, "amount": a,
                     "priority": rng.choice([2, 2, 2, 1, 0]), "seq": rng.randint(0, 4)})
    return {"participants": parts, "payments": pays}
