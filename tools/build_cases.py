"""Build tasks/clearing-offset/tests/cases/*.json (offline; not part of the task images).

Every expected report is computed by tools/ref_np.py (numpy brute force over all subsets, no
branch and bound) and must equal the oracle engine in solution/src. Batches with at most 14
payments are also checked against tests/reference.py (pure-Python brute force).

Usage: python3 tools/build_cases.py
"""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / "tasks" / "clearing-offset"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(TASK / "solution" / "src"))
sys.path.insert(0, str(TASK / "tests"))

import ref_np  # noqa: E402
import reference  # noqa: E402
from lumen import engine  # noqa: E402

CASES = TASK / "tests" / "cases"


def B(parts, pays):
    return {
        "participants": [{"id": i, "collateral": c, "reserve": r} for i, c, r in parts],
        "payments": [
            {"id": i, "debtor": d, "creditor": c, "amount": a, "priority": pr, "seq": s}
            for i, d, c, a, pr, s in pays
        ],
    }


def hand_cases():
    return {
        "01-chain": B([("A", 10, 0), ("B", 0, 0), ("C", 0, 0)], [("p1", "A", "B", 4, 0, 1), ("p2", "B", "C", 3, 0, 2), ("p5", "A", "C", 1, 2, 5)]),
        "02-ring": B([("A", 0, 0), ("B", 0, 0), ("C", 0, 0)], [("p1", "A", "B", 10, 0, 1), ("p2", "B", "C", 10, 0, 2), ("p3", "C", "A", 10, 0, 3)]),
        "03-reserve-ring": B([("A", 10, 8), ("B", 0, 0)], [("p1", "A", "B", 5, 0, 1), ("p2", "B", "A", 5, 0, 2)]),
        "04-scan-order": B([("A", 0, 0), ("B", 5, 0), ("C", 0, 0)], [("p1", "A", "C", 5, 0, 1), ("p2", "B", "A", 5, 0, 2), ("p3", "A", "B", 5, 0, 3)]),
        "05-greedy-blocks": B([("A", 6, 0), ("B", 0, 0), ("C", 0, 0)], [("p1", "A", "C", 6, 0, 1), ("p2", "A", "B", 10, 0, 2), ("p3", "B", "A", 4, 0, 3)]),
        "06-priority": B([("A", 6, 0), ("B", 0, 0), ("C", 0, 0)], [("p1", "A", "C", 6, 1, 1), ("p2", "A", "B", 10, 0, 2), ("p3", "B", "A", 4, 0, 3)]),
        "07-multi-edge": B([("A", 0, 0), ("B", 0, 0)], [("p1", "A", "B", 5, 0, 1), ("p2", "A", "B", 5, 0, 2), ("p3", "B", "A", 5, 0, 3)]),
        "08-second-pass": B([("A", 0, 0), ("B", 5, 0), ("C", 0, 0)], [("p1", "A", "C", 5, 0, 1), ("p2", "B", "A", 5, 0, 2)]),
        "09-lex-tie": B([("A", 10, 8), ("B", 0, 0), ("C", 0, 0)], [("p1", "A", "B", 9, 0, 1), ("p2", "B", "A", 1, 0, 2), ("p3", "A", "C", 9, 0, 3), ("p4", "C", "A", 1, 0, 4)]),
        "10-amount-tie": B([("A", 10, 8), ("B", 0, 0), ("C", 0, 0)], [("p1", "A", "B", 9, 0, 1), ("p2", "B", "A", 1, 0, 2), ("p3", "A", "C", 10, 0, 3), ("p4", "C", "A", 2, 0, 4)]),
        "11-count-tie": B([("A", 0, 0), ("B", 4, 4), ("C", 0, 0)], [("p1", "A", "B", 4, 0, 1), ("p2", "B", "A", 8, 0, 2), ("p3", "B", "C", 4, 0, 3), ("p4", "C", "A", 4, 0, 4)]),
        "12-after-cycle": B([("A", 3, 3), ("B", 0, 0), ("C", 0, 0)], [("p1", "A", "B", 3, 0, 1), ("p2", "B", "A", 1, 0, 2), ("p3", "B", "C", 2, 0, 3)]),
        "13-id-tie": B([("A", 5, 0), ("B", 0, 0)], [("b", "A", "B", 5, 0, 1), ("a", "A", "B", 5, 0, 1)]),
        "14-union-bundle": B([("A", 0, 0), ("B", 0, 0), ("C", 0, 0)], [("p1", "A", "B", 4, 0, 1), ("p2", "B", "A", 4, 0, 2), ("p3", "B", "C", 3, 0, 3), ("p4", "C", "B", 3, 0, 4)]),
        "15-not-closed": B([("A", 10, 8), ("B", 0, 0), ("C", 0, 0)], [("p1", "A", "B", 5, 0, 1), ("p2", "C", "A", 5, 0, 2)]),
        "16-three-way-subset": B(
            [("A", 2, 2), ("B", 0, 0), ("C", 0, 0), ("D", 0, 0)],
            [("a1", "A", "B", 5, 1, 1), ("a2", "B", "C", 5, 1, 2), ("a3", "C", "A", 3, 1, 3), ("a4", "C", "D", 2, 1, 4), ("a5", "D", "A", 2, 1, 5), ("a6", "A", "D", 1, 1, 6)],
        ),
        "17-offset-then-offset": B(
            [("A", 0, 0), ("B", 0, 0), ("C", 6, 6), ("D", 0, 0)],
            [("q1", "A", "B", 3, 0, 1), ("q2", "B", "A", 3, 0, 2), ("q3", "C", "D", 2, 0, 3), ("q4", "D", "C", 5, 0, 4), ("q5", "B", "D", 4, 0, 5), ("q6", "D", "B", 4, 0, 6)],
        ),
        "18-low-priority-after": B(
            [("A", 0, 0), ("B", 0, 0), ("C", 0, 0)],
            [("x1", "A", "B", 6, 2, 1), ("x2", "B", "A", 6, 2, 2), ("y1", "B", "C", 1, 0, 3), ("y2", "C", "B", 1, 0, 4), ("x3", "B", "C", 2, 2, 5), ("x4", "C", "B", 2, 2, 6)],
        ),
    }


def mid_batch(rng):
    n = rng.randint(3, 6)
    ids = [chr(65 + i) for i in range(n)]
    parts = []
    for pid in ids:
        c = rng.randint(0, 4)
        parts.append({"id": pid, "collateral": c, "reserve": rng.randint(0, c)})
    pays = []
    for k in range(rng.randint(8, 13)):
        d, c = rng.sample(ids, 2)
        pays.append({"id": rng.choice(["p", "q", "P"]) + f"{k:02d}", "debtor": d, "creditor": c,
                     "amount": rng.randint(1, 7), "priority": rng.choice([0, 0, 0, 1, 2]), "seq": rng.randint(0, 9)})
    return {"participants": parts, "payments": pays}


def big_batch(rng):
    parts, pays, n = [], [], 0
    for ci in range(rng.randint(2, 3)):
        ids = [f"{chr(65 + ci)}{j}" for j in range(rng.randint(6, 8))]
        for pid in ids:
            c = rng.randint(0, 1 if rng.random() < 0.7 else 3)
            parts.append({"id": pid, "collateral": c, "reserve": rng.randint(0, c)})
        prio = rng.randint(0, 2)
        for _ in range(rng.randint(18, 25)):
            d, c = rng.sample(ids, 2)
            pays.append({"id": f"t{n:03d}", "debtor": d, "creditor": c, "amount": rng.randint(1, 9),
                         "priority": prio if rng.random() < 0.9 else rng.randint(0, 2), "seq": rng.randint(0, 40)})
            n += 1
    rng.shuffle(pays)
    return {"participants": parts, "payments": pays}


def write(name, batch, expected, note):
    (CASES / f"{name}.json").write_text(json.dumps({"note": note, "batch": batch, "expected": expected}, indent=1) + "\n", encoding="utf-8")


def main() -> None:
    for old in CASES.glob("*.json"):
        old.unlink()
    CASES.mkdir(parents=True, exist_ok=True)
    stats = []
    for name, batch in hand_cases().items():
        exp = ref_np.settle(batch)
        assert exp == engine.settle(batch) == reference.settle(batch), name
        write(name, batch, exp, "hand batch")
        stats.append((name, len(batch["payments"]), len(exp["settled"])))

    rng = random.Random(20261012)
    mids = 0
    while mids < 10:
        batch = mid_batch(rng)
        exp = ref_np.settle(batch)
        assert exp == engine.settle(batch) == reference.settle(batch), "mid"
        if len(exp["settled"]) < 3:
            continue
        write(f"2{mids}-mid", batch, exp, "random mid-size batch, seed 20261012")
        stats.append((f"2{mids}-mid", len(batch["payments"]), len(exp["settled"])))
        mids += 1

    rng = random.Random(20261013)
    biggest = []
    orig = ref_np.solve_component
    seen = [0]

    def wrap(ps, bal):
        seen[0] = max(seen[0], len(ps))
        return orig(ps, bal)

    ref_np.solve_component = wrap
    bigs = 0
    while bigs < 10:
        batch = big_batch(rng)
        if len(batch["payments"]) > 64 or len(batch["participants"]) > 24:
            continue
        seen[0] = 0
        t0 = time.time()
        mine = engine.settle(batch)
        dt = time.time() - t0
        exp = ref_np.settle(batch)
        if not (20 <= seen[0] <= 26) or dt > 1.5 or len(exp["settled"]) < 8:
            continue
        assert mine == exp, "big mismatch"
        write(f"3{bigs}-gridlock", batch, exp, f"gridlock batch, seed 20261013, largest candidate group {seen[0]}")
        stats.append((f"3{bigs}-gridlock", len(batch["payments"]), len(exp["settled"]), seen[0], round(dt, 3)))
        bigs += 1
    for row in stats:
        print(row)


if __name__ == "__main__":
    main()
