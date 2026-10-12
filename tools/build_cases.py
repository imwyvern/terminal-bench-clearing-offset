"""Build tasks/clearing-offset/tests/cases/*.json and the four agent fixtures (offline).

Every expected report is computed by tools/ref_np.py (numpy brute force over all subsets, no
branch and bound) and must equal the oracle engine in solution/src. Batches with at most 13
payments are also checked against tests/reference.py (pure-Python brute force).

Mutant-killer cases: for each single wrong reading of one rule (tools/mutants.py, tools/ref_tie.py)
this script searches small random batches for the smallest one on which the wrong reading gives a
different report and stores it as a case, so every wrong reading fails at least two stored cases.

Usage: python3 tools/build_cases.py   (or --multi-lots to rebuild only the 9xx-multi-lots cases)
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

import mutants  # noqa: E402
from gen_age import age_batch  # noqa: E402
from gen_pp import pp_batch  # noqa: E402
import ref_np  # noqa: E402
import ref_tie  # noqa: E402
import reference  # noqa: E402
from lumen import engine  # noqa: E402

CASES = TASK / "tests" / "cases"
FIXTURES = TASK / "environment" / "fixtures"
MINED = ROOT / "tools" / "mined"
MINED_LOTS = ROOT / "tools" / "mined_lots"


def B(parts, pays):
    return {
        "participants": [{"id": i, "collateral": c, "reserve": r, "ceiling": k} for i, c, r, k in parts],
        "payments": [
            {"id": i, "debtor": d, "creditor": c, "amount": a, "priority": pr, "seq": s}
            for i, d, c, a, pr, s in pays
        ],
    }


def hand_cases():
    return {
        "01-chain": B([("A", 10, 0, 100), ("B", 0, 0, 100), ("C", 0, 0, 100)], [("p1", "A", "B", 4, 0, 1), ("p2", "B", "C", 3, 0, 2), ("p5", "A", "C", 1, 2, 5)]),
        "02-ring": B([("A", 1, 0, 100), ("B", 1, 0, 100), ("C", 1, 0, 100)], [("p1", "A", "B", 10, 0, 1), ("p2", "B", "C", 10, 0, 2), ("p3", "C", "A", 10, 0, 3)]),
        "03-reserve-ring": B([("A", 10, 8, 100), ("B", 1, 0, 100)], [("p1", "A", "B", 5, 1, 1), ("p2", "B", "A", 5, 1, 2)]),
        "04-scan-order": B([("A", 0, 0, 100), ("B", 5, 0, 100), ("C", 0, 0, 100)], [("p1", "A", "C", 5, 0, 1), ("p2", "B", "A", 5, 0, 2), ("p3", "A", "B", 5, 0, 3)]),
        "05-floor-ceiling": B([("A", 10, 8, 100), ("B", 8, 0, 10), ("C", 0, 0, 100)], [("p1", "A", "C", 5, 0, 1), ("p2", "A", "B", 3, 1, 2), ("p3", "B", "C", 4, 1, 3), ("p4", "C", "B", 9, 1, 4)]),
        "06-ceiling-blocks": B([("A", 10, 0, 100), ("B", 8, 0, 10)], [("p1", "A", "B", 5, 0, 1)]),
        "07-partial-order": B([("A", 12, 2, 100), ("B", 0, 0, 100)], [("p1", "A", "B", 14, 2, 1), ("p2", "A", "B", 6, 2, 0)]),
        "08-tie-chain": B([("A", 2, 2, 100), ("B", 8, 8, 100), ("C", 2, 2, 100)], [("p1", "A", "B", 10, 1, 1), ("p2", "A", "C", 6, 1, 2), ("p3", "C", "B", 4, 1, 3), ("p4", "B", "A", 10, 1, 4)]),
        "09-restart": B([("A", 0, 0, 100), ("B", 10, 0, 100), ("C", 0, 0, 100)], [("p0", "C", "A", 10, 0, 5), ("p1", "B", "C", 10, 1, 1)]),
        "10-ring-no-cash": B([("A", 0, 0, 100), ("B", 0, 0, 100), ("C", 0, 0, 100)], [("p1", "A", "B", 10, 0, 1), ("p2", "B", "C", 10, 0, 2), ("p3", "C", "A", 10, 0, 3)]),
        "11-fee-rounds-up": B([("A", 22, 22, 100), ("B", 1, 1, 100)], [("p1", "A", "B", 21, 1, 1), ("p2", "B", "A", 21, 1, 2)]),
        "12-odd-half-floor": B([("A", 20, 9, 100), ("B", 0, 0, 100)], [("p1", "A", "B", 16, 0, 1), ("p2", "A", "B", 1, 0, 2)]),
        "13-partial-lot": B([("A", 17, 2, 100), ("B", 0, 0, 100)], [("p1", "A", "B", 40, 2, 1)]),
        "14-partial-ceiling-room": B([("A", 50, 0, 100), ("B", 20, 0, 33)], [("p1", "A", "B", 40, 2, 1)]),
        "15-pr1-never-split": B([("A", 17, 2, 100), ("B", 0, 0, 100)], [("p1", "A", "B", 40, 1, 1)]),
        "16-bundle-ceiling": B([("A", 10, 10, 11), ("B", 10, 10, 100)], [("p1", "A", "B", 4, 1, 1), ("p2", "B", "A", 12, 1, 2)]),
        "17-union-bundle": B([("A", 3, 3, 100), ("B", 3, 3, 100), ("C", 3, 3, 100)], [("p1", "A", "B", 8, 1, 1), ("p2", "B", "A", 8, 1, 2), ("p3", "B", "C", 6, 1, 3), ("p4", "C", "B", 6, 1, 4)]),
        "18-id-tie": B([("A", 10, 10, 100), ("B", 10, 10, 100)], [("b1", "A", "B", 5, 1, 1), ("a1", "A", "B", 5, 1, 1), ("b2", "B", "A", 5, 1, 2)]),
        "19-bundle-then-pr0": B([("A", 0, 0, 100), ("B", 5, 5, 100), ("C", 5, 5, 100)], [("x1", "B", "C", 10, 1, 1), ("x2", "C", "B", 10, 1, 2), ("z1", "A", "B", 6, 0, 3)]),
        "21-age-relay": B([("A", 0, 0, 100), ("B", 10, 0, 100), ("C", 0, 0, 100), ("D", 0, 0, 100), ("E", 0, 0, 100)], [("r1", "B", "C", 10, 1, 1), ("r2", "C", "D", 10, 0, 9), ("r3", "D", "E", 10, 1, 2), ("w", "E", "A", 12, 2, 3)]),
        "22-strain-floor": B([("A", 20, 10, 100), ("B", 0, 0, 100), ("C", 3, 0, 3)], [("p1", "A", "B", 30, 2, 1), ("s", "C", "B", 3, 2, 2), ("q", "A", "C", 3, 0, 3)]),
        "20-pr2-queue-two-pass": B([("A", 30, 5, 100), ("B", 0, 0, 100), ("C", 0, 0, 100)], [("p1", "A", "B", 9, 2, 1), ("p2", "A", "C", 20, 2, 2), ("p3", "B", "A", 5, 2, 3)]),
    }


MUTANTS = {
    "fee_floor": ("engine", {"fee_floor"}),
    "fee_none": ("engine", {"fee_none"}),
    "no_half": ("engine", {"no_half"}),
    "no_cap_uni": ("engine", {"no_cap_uni"}),
    "no_cap_bundle": ("engine", {"no_cap_bundle"}),
    "no_partial": ("engine", {"no_partial"}),
    "partial_all": ("engine", {"partial_all"}),
    "lot1": ("engine", {"lot1"}),
    "pr2_seq": ("engine", {"pr2_seq"}),
    "seq_prio": ("engine", {"seq_prio"}),
    "tie_count_first": ("tie", None),
    "no_age": ("engine", {"no_age"}),
    "age_all": ("engine", {"age_all"}),
    "age2": ("engine", {"age2"}),
    "no_strain": ("engine", {"no_strain"}),
    "age_reset_move": ("engine", {"age_reset_move"}),
}
AGE_MUTANTS = {"no_age", "age_all", "age2", "no_strain", "age_reset_move"}


def run_mutant(kind, flags, batch):
    if kind == "tie":
        ref_tie.MUT_TIE = True
        try:
            return ref_tie.settle(batch)
        finally:
            ref_tie.MUT_TIE = False
    mutants.M.clear()
    mutants.M.update(flags)
    try:
        return mutants.settle(batch)
    finally:
        mutants.M.clear()


def tiny_batch(rng):
    n = rng.randint(2, 4)
    ids = "ABCD"[:n]
    parts = []
    for pid in ids:
        c = rng.choice([0, 2, 4, 6, 8, 12, 20, 30])
        parts.append({"id": pid, "collateral": c, "reserve": rng.choice([0, c, c // 2, max(0, c - 1)]),
                      "ceiling": c + rng.choice([0, 3, 10, 100])})
    pays = []
    for k in range(rng.randint(2, 5)):
        d, c = rng.sample(list(ids), 2)
        pays.append({"id": f"m{k + 1}", "debtor": d, "creditor": c, "amount": rng.choice([1, 2, 4, 5, 6, 9, 10, 14, 21, 40]),
                     "priority": rng.choice([0, 1, 1, 2]), "seq": k + 1})
    return {"participants": parts, "payments": pays}


def tie_batch(rng):
    n = rng.randint(3, 4)
    ids = "ABCD"[:n]
    parts = []
    for pid in ids:
        c = rng.choice([2, 4, 6, 8])
        parts.append({"id": pid, "collateral": c, "reserve": c, "ceiling": 100})
    pays = []
    for k in range(rng.randint(4, 5)):
        d, c = rng.sample(list(ids), 2)
        pays.append({"id": f"m{k + 1}", "debtor": d, "creditor": c, "amount": rng.choice([2, 4, 6, 8, 10]), "priority": 1, "seq": k + 1})
    return {"participants": parts, "payments": pays}


def mutant_cases():
    out = {}
    for index, (name, (kind, flags)) in enumerate(MUTANTS.items()):
        rng = random.Random(7000 + index)
        found = []
        for _ in range(200000):
            if name == "tie_count_first":
                batch = tie_batch(rng)
            elif name in AGE_MUTANTS:
                batch = age_batch(rng, 4, 7, 3, 4)
            else:
                batch = tiny_batch(rng)
            if run_mutant(kind, flags, batch) != engine.settle(batch):
                found.append((len(batch["payments"]) * 10 + len(batch["participants"]), len(found), batch))
                if len(found) >= 12:
                    break
        assert len(found) >= 2, name
        found.sort(key=lambda item: item[:2])
        for pos in range(2):
            out[f"4{index:01d}{'ab'[pos]}-kill-{name}"] = found[pos][2]
    return out


def mid_batch(rng):
    n = rng.randint(3, 6)
    ids = [chr(65 + i) for i in range(n)]
    parts = []
    for pid in ids:
        c = rng.choice([0, 0, 4, 10, 20, 35])
        parts.append({"id": pid, "collateral": c, "reserve": rng.randint(0, c), "ceiling": c + rng.choice([0, 5, 15, 1000])})
    pays = []
    for k in range(rng.randint(8, 13)):
        d, c = rng.sample(ids, 2)
        pays.append({"id": rng.choice(["p", "q", "P"]) + f"{k:02d}", "debtor": d, "creditor": c,
                     "amount": rng.randint(1, 30), "priority": rng.choice([0, 1, 1, 2, 2]), "seq": rng.randint(0, 9)})
    return {"participants": parts, "payments": pays}


def big_batch(rng):
    parts, pays, n = [], [], 0
    for ci in range(rng.randint(2, 3)):
        ids = [f"{chr(65 + ci)}{j}" for j in range(rng.randint(5, 8))]
        for pid in ids:
            c = rng.choice([0, 0, 5, 10, 20, 40, 80])
            parts.append({"id": pid, "collateral": c, "reserve": rng.randint(0, c), "ceiling": c + rng.choice([0, 10, 25, 60, 10000])})
        prio = rng.randint(0, 2)
        for _ in range(rng.randint(16, 24)):
            d, c = rng.sample(ids, 2)
            pays.append({"id": f"t{n:03d}", "debtor": d, "creditor": c, "amount": rng.randint(3, 40),
                         "priority": prio if rng.random() < 0.85 else rng.randint(0, 2), "seq": rng.randint(0, 40)})
            n += 1
    rng.shuffle(pays)
    return {"participants": parts, "payments": pays}


def write(name, batch, expected, note):
    (CASES / f"{name}.json").write_text(json.dumps({"note": note, "batch": batch, "expected": expected}, indent=1) + "\n", encoding="utf-8")


def check(name, batch):
    mine = engine.settle(batch)
    exp = ref_np.settle(batch)
    assert mine == exp, name
    if len(batch["payments"]) <= 13:
        assert reference.settle(batch) == exp, name
    return exp


def naive_is_slow(batch, seconds=6):
    """True when the pass-by-pass simulation (tools/mutants.py with no wrong reading) needs more than `seconds`."""
    import signal

    class Slow(Exception):
        pass

    def stop(*_):
        raise Slow

    old = signal.signal(signal.SIGALRM, stop)
    signal.alarm(seconds)
    try:
        mutants.M.clear()
        mutants.settle(batch)
        return False
    except Slow:
        return True
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)


def main() -> None:
    for old in CASES.glob("*.json"):
        old.unlink()
    CASES.mkdir(parents=True, exist_ok=True)
    hands = hand_cases()
    stats = []
    for name, batch in hands.items():
        exp = check(name, batch)
        write(name, batch, exp, "hand batch")
        stats.append((name, len(batch["payments"]), len(exp["settled"])))
    for name in ("01-chain", "02-ring", "03-reserve-ring", "04-scan-order"):
        (FIXTURES / f"{name}.json").write_text(json.dumps(hands[name], indent=2) + "\n", encoding="utf-8")
        (FIXTURES / f"{name}.expected.json").write_text(json.dumps(engine.settle(hands[name]), indent=2) + "\n", encoding="utf-8")

    for name, batch in mutant_cases().items():
        exp = check(name, batch)
        write(name, batch, exp, "smallest batch found on which one wrong reading of one rule differs")
        stats.append((name, len(batch["payments"]), len(exp["settled"])))

    rng = random.Random(20261014)
    mids = 0
    while mids < 12:
        aging = mids % 2 == 1
        batch = age_batch(rng, 9, 13, 4, 7) if aging else mid_batch(rng)
        exp = check("mid", batch)
        if len(exp["settled"]) < 3:
            continue
        if aging and run_mutant("engine", {"no_age"}, batch) == exp:
            continue
        write(f"5{mids:02d}-mid", batch, exp, "random mid-size batch, seed 20261014")
        stats.append((f"5{mids:02d}-mid", len(batch["payments"]), len(exp["settled"])))
        mids += 1

    rng = random.Random(20261016)
    aged = 0
    while aged < 8:
        batch = age_batch(rng, 14, 20, 5, 8)
        exp = check("age-large", batch)
        if len(exp["settled"]) < 6 or run_mutant("engine", {"no_age"}, batch) == exp or run_mutant("engine", {"age_all"}, batch) == exp:
            continue
        write(f"55{aged}-age-large", batch, exp, "larger batch where the aging rule decides the outcome, seed 20261016")
        stats.append((f"55{aged}-age-large", len(batch["payments"]), len(exp["settled"])))
        aged += 1

    rng = random.Random(20261015)
    seen = [0]
    orig = ref_np.settle
    bigs = 0
    while bigs < 10:
        batch = big_batch(rng)
        if len(batch["payments"]) > 64 or len(batch["participants"]) > 24:
            continue
        t0 = time.time()
        mine = engine.settle(batch)
        dt = time.time() - t0
        if dt > 1.5 or len(mine["settled"]) < 10:
            continue
        exp = ref_np.settle(batch)
        assert mine == exp, "big mismatch"
        write(f"6{bigs:02d}-gridlock", batch, exp, "gridlock batch, seed 20261015")
        stats.append((f"6{bigs:02d}-gridlock", len(batch["payments"]), len(mine["settled"]), round(dt, 3)))
        bigs += 1
    rng = random.Random(20261017)
    heavy = 0
    tries = 0
    while heavy < 12:
        tries += 1
        batch = pp_batch(rng, amt_hi=10**9)
        for pay in batch["payments"]:
            if pay["amount"] > 100:
                pay["amount"] = rng.randint(3 * 10**8, 10**9)
        if sum(1 for pay in batch["payments"] if pay["priority"] == 2 and pay["amount"] > 10**8) < 2:
            continue
        if not naive_is_slow(batch):
            continue
        t0 = time.time()
        mine = engine.settle(batch)
        dt = time.time() - t0
        assert dt < 1.0, dt
        write(f"8{heavy:02d}-long-lots", batch, mine, "huge partial-lot ping-pong; checked offline by tools/verify_pp.py against pass-by-pass simulation")
        stats.append((f"8{heavy:02d}-long-lots", len(batch["payments"]), len(mine["settled"]), round(dt, 3)))
        heavy += 1
    for path in sorted(MINED.glob("*.json")):
        batch = json.loads(path.read_text(encoding="utf-8"))["batch"]
        t0 = time.time()
        mine = engine.settle(batch)
        dt = time.time() - t0
        assert dt < 2.0, (path.name, dt)
        write(f"7{path.stem}-hard", batch, mine, "mined hard batch, checked offline against tools/ref_milp.py")
        stats.append((f"7{path.stem}-hard", len(batch["payments"]), len(mine["settled"]), round(dt, 3)))
    stats += multi_lots()
    for row in stats:
        print(row)


def multi_lots():
    """9xx-multi-lots: mined batches (tools/gen_lots.py) with several long multi-hop partial-lot phases."""
    stats = []
    for old in CASES.glob("9*-multi-lots.json"):
        old.unlink()
    for n, path in enumerate(sorted(MINED_LOTS.glob("*.json"))):
        batch = json.loads(path.read_text(encoding="utf-8"))
        t0 = time.time()
        mine = engine.settle(json.loads(json.dumps(batch)))
        dt = time.time() - t0
        assert dt < 1.0, (path.name, dt)
        write(f"9{n:02d}-multi-lots", batch, mine, f"mined multi-hop partial-lot batch ({path.stem}); checked offline by tools/verify_pp.py against pass-by-pass simulation")
        stats.append((f"9{n:02d}-multi-lots", len(batch["payments"]), len(mine["settled"]), round(dt, 3)))
    return stats


if __name__ == "__main__":
    if sys.argv[1:] == ["--multi-lots"]:
        for row in multi_lots():
            print(row)
    else:
        main()
