from __future__ import annotations

from pathlib import Path

from .models import CandidateModification


PATCH_LIBRARY: dict[str, str] = {
    "make_cancel_idempotent": '''
from dataclasses import dataclass


@dataclass
class Order:
    order_id: str
    qty: int
    payment_captured: int
    refunded: int = 0
    canceled: bool = False


class Store:
    def __init__(self, inventory: int = 10):
        self.inventory = inventory
        self.orders: dict[str, Order] = {}

    def place_order(self, order_id: str, qty: int, price: int) -> None:
        if qty <= 0:
            raise ValueError("qty must be positive")
        if qty > self.inventory:
            raise ValueError("not enough inventory")
        self.inventory -= qty
        self.orders[order_id] = Order(order_id=order_id, qty=qty, payment_captured=price)

    def cancel_order(self, order_id: str) -> int:
        order = self.orders[order_id]
        if order.canceled:
            return order.refunded
        order.canceled = True
        order.refunded = order.payment_captured
        return order.refunded
''',
    "restore_inventory_on_cancel": '''
from dataclasses import dataclass


@dataclass
class Order:
    order_id: str
    qty: int
    payment_captured: int
    refunded: int = 0
    canceled: bool = False


class Store:
    def __init__(self, inventory: int = 10):
        self.inventory = inventory
        self.orders: dict[str, Order] = {}

    def place_order(self, order_id: str, qty: int, price: int) -> None:
        if qty <= 0:
            raise ValueError("qty must be positive")
        if qty > self.inventory:
            raise ValueError("not enough inventory")
        self.inventory -= qty
        self.orders[order_id] = Order(order_id=order_id, qty=qty, payment_captured=price)

    def cancel_order(self, order_id: str) -> int:
        order = self.orders[order_id]
        if order.canceled:
            return order.refunded
        order.canceled = True
        self.inventory += order.qty
        order.refunded = order.payment_captured
        return order.refunded
''',
    "noop": None,
}


PATCH_DESCRIPTIONS: dict[str, str] = {
    "make_cancel_idempotent": "Add an idempotency guard to cancel_order so repeated cancellation does not double-refund.",
    "restore_inventory_on_cancel": "Restore inventory when an order is canceled while keeping the idempotency guard.",
    "noop": "Make no change.",
}


class CandidateApplier:
    def apply(self, workspace: Path, candidate: CandidateModification) -> None:
        if candidate.name == "noop":
            return
        if candidate.name not in PATCH_LIBRARY:
            raise ValueError(f"Unknown candidate patch: {candidate.name}")
        code = PATCH_LIBRARY[candidate.name]
        if code is None:
            return
        path = workspace / "sut" / "order_system.py"
        path.write_text(code, encoding="utf-8")
