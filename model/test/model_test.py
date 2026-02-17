import pytest

from model.model import Batch, OrderLine


def make_batch_and_order_line(
    batch_quantity: int,
    line_quantity: int,
    batch_sku: str = "TEST-SKU",
    line_sku: str = "TEST-SKU",
) -> tuple[Batch, OrderLine]:
    batch = Batch(reference="batch-001", sku=batch_sku, quantity=batch_quantity)
    order_line = OrderLine(
        order_reference="order-001", sku=line_sku, quantity=line_quantity
    )

    return batch, order_line


def test_allocate_order_line_to_batch_reduces_available_quantity():
    batch, order_line = make_batch_and_order_line(20, 2)

    batch.allocate(order_line)

    assert batch.available_quantity == 18


def test_allocate_order_line_to_batch_with_insufficient_quantity_raises_exception():
    batch, order_line = make_batch_and_order_line(2, 20)

    with pytest.raises(ValueError):
        batch.allocate(order_line)


def test_allocate_order_line_to_batch_with_mismatched_sku_raises_exception():
    batch, order_line = make_batch_and_order_line(
        20, 2, batch_sku="TEST-SKU", line_sku="OTHER-SKU"
    )

    with pytest.raises(ValueError):
        batch.allocate(order_line)


def test_allocate_different_order_lines_to_batch_reduces_available_quantity():
    batch = Batch(reference="batch-001", sku="TEST-SKU", quantity=20)
    order_line1 = OrderLine(order_reference="order-001", sku="TEST-SKU", quantity=2)
    order_line2 = OrderLine(order_reference="order-002", sku="TEST-SKU", quantity=3)
    order_line3 = OrderLine(order_reference="order-002", sku="TEST-SKU", quantity=5)

    batch.allocate(order_line1)
    batch.allocate(order_line2)
    batch.allocate(order_line3)

    assert batch.available_quantity == 10


def test_allocate_same_order_line_to_batch_multiple_times_does_not_reduce_available_quantity():
    batch, order_line = make_batch_and_order_line(20, 2)

    batch.allocate(order_line)
    batch.allocate(order_line)

    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    batch, order_line = make_batch_and_order_line(20, 2)

    assert batch.can_allocate(order_line) is True


def test_cannot_allocate_if_available_smaller_than_required():
    batch, order_line = make_batch_and_order_line(2, 20)

    assert batch.can_allocate(order_line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, order_line = make_batch_and_order_line(2, 2)

    assert batch.can_allocate(order_line) is True


def test_cannot_allocate_if_skus_do_not_match():
    batch, order_line = make_batch_and_order_line(
        20, 2, batch_sku="TEST-SKU", line_sku="OTHER-SKU"
    )

    assert batch.can_allocate(order_line) is False
