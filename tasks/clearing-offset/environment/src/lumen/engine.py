"""Unilateral funding scan used by the current Lumen build."""

from __future__ import annotations


def settle(batch: dict) -> dict:
    balance = {participant["id"]: participant["collateral"] for participant in batch["participants"]}
    reserve = {participant["id"]: participant["reserve"] for participant in batch["participants"]}
    remaining = {payment["id"]: dict(payment) for payment in batch["payments"]}
    settled: list[str] = []

    for priority in (0, 1, 2):
        while True:
            choice = None
            waiting = sorted(
                (payment for payment in remaining.values() if payment["priority"] == priority),
                key=lambda payment: (payment["seq"], payment["id"]),
            )
            for payment in waiting:
                debtor = payment["debtor"]
                if balance[debtor] - payment["amount"] >= reserve[debtor]:
                    choice = payment
                    break
            if choice is None:
                break
            balance[choice["debtor"]] -= choice["amount"]
            balance[choice["creditor"]] += choice["amount"]
            settled.append(choice["id"])
            del remaining[choice["id"]]

    by_id = {payment["id"]: payment for payment in batch["payments"]}
    settled_ids = set(settled)

    def sort_ids(ids: set[str]) -> list[str]:
        return sorted(ids, key=lambda pid: (by_id[pid]["priority"], by_id[pid]["seq"], pid))

    return {
        "settled": sort_ids(settled_ids),
        "unsettled": sort_ids(set(by_id) - settled_ids),
        "balances": {pid: balance[pid] for pid in sorted(balance)},
    }
