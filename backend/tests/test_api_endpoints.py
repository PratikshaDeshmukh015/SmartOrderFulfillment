import pytest
from backend.app.database import SessionLocal
from backend.app.routes import (
    orders, fulfillment, inventory, nodes, shipments, delivery, exceptions, analytics
)

@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()

def test_api_health_endpoint():
    from backend.app.main import health_check
    res = health_check()
    assert res["status"] == "healthy"

def test_list_orders_route(db_session):
    result = orders.list_orders(limit=10, offset=0, db=db_session)
    assert isinstance(result, list)
    assert len(result) > 0
    assert result[0].order_id.startswith("ORD-2026-")

def test_get_order_route(db_session):
    ord_id = "ORD-2026-000001"
    ord_obj = orders.get_order(ord_id, db=db_session)
    assert ord_obj.order_id == ord_id
    assert ord_obj.total_amount > 0

def test_list_inventory_route(db_session):
    result = inventory.list_inventory(db=db_session)
    assert len(result) > 0
    assert "available_quantity" in result[0]

def test_list_nodes_route(db_session):
    result = nodes.list_nodes(active_only=True, db=db_session)
    assert len(result) == 20

def test_optimize_order_route(db_session):
    result = fulfillment.optimize_order("ORD-2026-000001", db=db_session)
    assert result["order_id"] == "ORD-2026-000001"
    assert result["strategy"] is not None
    assert result["weighted_score"] > 0

def test_compare_baseline_route(db_session):
    result = fulfillment.compare_with_baseline("ORD-2026-000001", db=db_session)
    assert "baseline" in result
    assert "optimized" in result
    assert "improvement_summary" in result

def test_analytics_overview_route(db_session):
    res = analytics.get_analytics_overview(db=db_session)
    assert res["total_orders"] == 1000
    assert "on_time_delivery_pct" in res
    assert "split_shipment_pct" in res

def test_exceptions_list_route(db_session):
    res = exceptions.list_exceptions(db=db_session)
    assert len(res) > 0
