from dataclasses import dataclass
from typing import List, Set

# SKU: Stock Keeping Unit


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
    def __init__(self, reference: str, sku: str, quantity: int):
        self.reference: str = reference
        self.sku: str = sku
        self.quantity: int = quantity
        self._allocated_lines: Set[OrderLine] = set()

    def allocate(self, order_line: OrderLine):
        if order_line in self._allocated_lines:
            return

        if not self.can_allocate(order_line):
            raise ValueError("Cannot allocate order line to batch")

        self._allocated_lines.add(order_line)
        self.quantity -= order_line.quantity

    @property
    def available_quantity(self) -> int:
        return self.quantity

    def can_allocate(self, order_line: OrderLine) -> bool:
        return (
            self.sku == order_line.sku
            and self.available_quantity >= order_line.quantity
        )
