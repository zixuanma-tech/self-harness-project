from __future__ import annotations

from pathlib import Path

BASE_HARD_TESTS = '''
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sut"))

from order_system import Store


def test_hard_no_double_refund():
    store = Store(inventory=5)
    store.place_order("o1", qty=1, price=100)
    store.cancel_order("o1")
    store.cancel_order("o1")
    order = store.orders["o1"]
    assert order.refunded == 100, "duplicate_refund"


def test_hard_inventory_never_negative():
    store = Store(inventory=2)
    store.place_order("o1", qty=1, price=100)
    assert store.inventory >= 0, "inventory_negative"
'''

BASE_SOFT_TESTS = '''
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sut"))

from order_system import Store


def test_soft_cancel_restores_inventory():
    store = Store(inventory=5)
    store.place_order("o1", qty=1, price=100)
    before_cancel = store.inventory
    store.cancel_order("o1")
    assert store.inventory == before_cancel + 1, "inventory_not_restored"
'''


def _generated_validator_source(name: str) -> str:
    if name == "soft_inventory_restore_qty_two":
        return '''
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sut"))

from order_system import Store


def test_soft_generated_inventory_restore_qty_two():
    store = Store(inventory=5)
    store.place_order("o2", qty=2, price=100)
    before_cancel = store.inventory
    store.cancel_order("o2")
    assert store.inventory == before_cancel + 2, "inventory_not_restored_qty_two"
'''
    if name == "hard_idempotent_cancel_guard":
        return '''
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sut"))

from order_system import Store


def test_hard_generated_cancel_is_idempotent():
    store = Store(inventory=4)
    store.place_order("o3", qty=1, price=50)
    first = store.cancel_order("o3")
    second = store.cancel_order("o3")
    assert first == second == 50, "duplicate_refund"
'''
    raise ValueError(f"Unknown generated validator: {name}")


class ValidatorMaterializer:
    def __init__(self, generated_validators: set[str]):
        self.generated_validators = generated_validators

    def materialize_into(self, workspace: Path) -> None:
        tests_dir = workspace / "tests"
        generated_dir = workspace / "generated_tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        generated_dir.mkdir(parents=True, exist_ok=True)

        (tests_dir / "test_hard_validators.py").write_text(BASE_HARD_TESTS, encoding="utf-8")
        (tests_dir / "test_soft_validators.py").write_text(BASE_SOFT_TESTS, encoding="utf-8")

        # Clear stale generated validators and re-materialize from source-of-truth state.
        for existing in generated_dir.glob("test_*.py"):
            existing.unlink()

        for name in sorted(self.generated_validators):
            path = generated_dir / f"test_{name}.py"
            path.write_text(_generated_validator_source(name), encoding="utf-8")
