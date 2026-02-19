from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Set

# SKU: Stock Keeping Unit
# ETA: Estimated Time of Arrival


@dataclass(frozen=True)
class OrderLine:
    order_reference: str
    sku: str
    quantity: int


@dataclass(frozen=True)
class Order:
    reference: str
    sku: str
    lines: List[OrderLine]


class Batch:
    def __init__(
        self, reference: str, sku: str, quantity: int, eta: Optional[date] = None
    ):
        self.reference: str = reference
        self.sku: str = sku
        self.quantity: int = quantity
        self.eta: Optional[date] = eta
        self._allocated_lines: Set[OrderLine] = set()

    def __lt__(self, other) -> bool:
        if self.eta is None:
            return True
        if other.eta is None:
            return False
        return self.eta < other.eta

    def allocate(self, order_line: OrderLine):
        if order_line in self._allocated_lines:
            return

        if not self.can_allocate(order_line):
            raise ValueError("Cannot allocate order line to batch")

        self._allocated_lines.add(order_line)
        self.quantity -= order_line.quantity

    def deallocate(self, order_line: OrderLine):
        if order_line not in self._allocated_lines:
            return

        self._allocated_lines.remove(order_line)
        self.quantity += order_line.quantity

    def can_allocate(self, order_line: OrderLine) -> bool:
        return self.sku == order_line.sku and self.quantity >= order_line.quantity


class OutOfStock(Exception):
    pass


def allocate(order_line: OrderLine, batches: List[Batch]) -> str:
    sorted_batches = sorted(batches)

    for batch in sorted_batches:
        if batch.can_allocate(order_line):
            batch.allocate(order_line)
            return batch.reference

    raise OutOfStock(f"Cannot allocate order line {order_line} to any batch")
