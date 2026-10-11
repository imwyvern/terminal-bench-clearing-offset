"""Offline check of the long-lots cases: replay each one pass by pass (no acceleration) and compare.

The replay is tools/mutants.py with no wrong reading switched on, which is the literal pass-by-pass
procedure. It can take minutes per case. Usage: python3 tools/verify_pp.py [case-file ...]
"""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import mutants  # noqa: E402

CASES = ROOT / "tasks" / "clearing-offset" / "tests" / "cases"


def check(path):
    case = json.loads(Path(path).read_text(encoding="utf-8"))
    t0 = time.time()
    mutants.M.clear()
    got = mutants.settle(case["batch"])
    return Path(path).name, got == case["expected"], round(time.time() - t0, 1)


if __name__ == "__main__":
    files = sys.argv[1:] or sorted(str(p) for p in CASES.glob("8*-long-lots.json"))
    with Pool(6) as pool:
        for name, ok, secs in pool.imap_unordered(check, files):
            print(name, "agree" if ok else "DIFFERENT", secs, "s", flush=True)
