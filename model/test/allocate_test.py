import pytest
from datetime import date, timedelta

from model.model import Batch, OrderLine, OutOfStock, allocate


today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)
sku = "TEST-SKU"


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", sku, 100, eta=None)
    shipment_batch = Batch("shipment-batch", sku, 100, eta=tomorrow)
    line = OrderLine("order-1", sku, 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.quantity == 90
    assert shipment_batch.quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch("fast-batch", sku, 100, eta=today)
    medium = Batch("normal-batch", sku, 100, eta=tomorrow)
    latest = Batch("slow-batch", sku, 100, eta=later)
    line = OrderLine("order-1", sku, 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.quantity == 90
    assert medium.quantity == 100
    assert latest.quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch", sku, 100, eta=None)
    shipment_batch = Batch("shipment-batch", sku, 100, eta=tomorrow)
    line = OrderLine("order-1", sku, 10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch-1", sku, 10, eta=today)
    allocate(OrderLine("order-1", sku, 10), [batch])

    with pytest.raises(OutOfStock, match=sku):
        allocate(OrderLine("order-2", sku, 1), [batch])
