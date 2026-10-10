"""Offline cross-check: whole procedure with a numpy brute-force bundle solver (no branch and bound)."""
from __future__ import annotations
import numpy as np


def solve_component(ps, bal):
    """ps sorted by id. Brute force over all 2**k subsets, MSB = smallest id."""
    k = len(ps)
    people = sorted({p["debtor"] for p in ps} | {p["creditor"] for p in ps})
    ix = {x: i for i, x in enumerate(people)}
    n = len(people)
    h1 = k // 2
    h2 = k - h1
    def half(items):
        m = len(items)
        size = 1 << m
        sub = np.arange(size, dtype=np.int64)
        net = np.zeros((n, size), dtype=np.int64)
        tot = np.zeros(size, dtype=np.int64)
        cnt = np.zeros(size, dtype=np.int64)
        outm = np.zeros(size, dtype=np.int64)
        inm = np.zeros(size, dtype=np.int64)
        for j, p in enumerate(items):
            bit = (sub >> (m - 1 - j)) & 1  # MSB first = smallest id first
            net[ix[p["debtor"]]] -= bit * p["amount"]
            net[ix[p["creditor"]]] += bit * p["amount"]
            tot += bit * p["amount"]
            cnt += bit
            outm |= bit << ix[p["debtor"]]
            inm |= bit << ix[p["creditor"]]
        return net, tot, cnt, outm, inm
    nl, tl, cl, ol, il = half(ps[:h1])
    nr, tr, cr, orr, ir = half(ps[h1:])
    base = np.array([bal[x] for x in people], dtype=np.int64)
    best = (0, 0, 0)  # total, count, mask
    for L in range(1 << h1):
        ok = np.ones(1 << h2, dtype=bool)
        for q in range(n):
            ok &= (base[q] + nl[q, L] + nr[q]) >= 0
        ok &= ((ol[L] | orr) & ~(il[L] | ir)) == 0
        total = tl[L] + tr
        cnt = cl[L] + cr
        ok &= total > 0
        if not ok.any():
            continue
        score = np.where(ok, total * 1000 + cnt, -1)
        top = score.max()
        idx = np.nonzero(score == top)[0]
        R = int(idx.max())  # largest right mask = lexicographically smallest among ties
        cand = (int(top) // 1000, int(top) % 1000, (L << h2) | R)
        if (cand[0], cand[1]) > (best[0], best[1]) or ((cand[0], cand[1]) == (best[0], best[1]) and cand[2] > best[2]):
            best = cand
    if best[0] == 0:
        return []
    mask = best[2]
    return [ps[j] for j in range(k) if (mask >> (k - 1 - j)) & 1]


def settle(batch):
    bal = {p["id"]: p["collateral"] for p in batch["participants"]}
    res = {p["id"]: p["reserve"] for p in batch["participants"]}
    todo = {p["id"]: p for p in batch["payments"]}
    done = set()
    def move(pays):
        for p in pays:
            bal[p["debtor"]] -= p["amount"]; bal[p["creditor"]] += p["amount"]
            done.add(p["id"]); del todo[p["id"]]
    for prio in (0, 1, 2):
        while True:
            changed = False
            while True:
                hit = False
                for p in sorted((q for q in todo.values() if q["priority"] == prio), key=lambda q: (q["seq"], q["id"])):
                    if bal[p["debtor"]] - p["amount"] >= res[p["debtor"]]:
                        move([p]); hit = True; changed = True
                if not hit:
                    break
            pool = sorted((q for q in todo.values() if q["priority"] == prio), key=lambda q: q["id"])
            while True:
                cred = {p["creditor"] for p in pool}
                nxt = [p for p in pool if p["debtor"] in cred]
                if len(nxt) == len(pool):
                    break
                pool = nxt
            comps = {}
            for p in pool:
                a, b = comps.setdefault(p["debtor"], {p["debtor"]}), comps.setdefault(p["creditor"], {p["creditor"]})
                if a is not b:
                    m = a | b
                    for x in m:
                        comps[x] = m
            uniq = []
            for s in comps.values():
                if not any(s is t for t in uniq):
                    uniq.append(s)
            win = []
            for s in uniq:
                ps = [p for p in pool if p["debtor"] in s]
                win += solve_component(ps, bal)
            if win:
                move(win); changed = True
            if not changed:
                break
    by = {p["id"]: p for p in batch["payments"]}
    order = lambda ids: sorted(ids, key=lambda i: (by[i]["priority"], by[i]["seq"], i))
    return {"settled": order(done), "unsettled": order(set(by) - done), "balances": dict(sorted(bal.items()))}
