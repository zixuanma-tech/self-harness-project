from __future__ import annotations

import shutil
from pathlib import Path

INITIAL_ORDER_SYSTEM = '''
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
        order.canceled = True
        order.refunded += order.payment_captured
        return order.refunded
'''


class WorkspaceManager:
    def __init__(self, runtime_root: Path):
        self.runtime_root = runtime_root
        self.runtime_root.mkdir(parents=True, exist_ok=True)

    def create_initial_workspace(self) -> Path:
        workspace = self.runtime_root / "mainline_round_0"
        if workspace.exists():
            shutil.rmtree(workspace)
        (workspace / "sut").mkdir(parents=True, exist_ok=True)
        (workspace / "sut" / "order_system.py").write_text(INITIAL_ORDER_SYSTEM, encoding="utf-8")
        return workspace

    def clone_workspace(self, source: Path, name: str) -> Path:
        target = self.runtime_root / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)
        return target
