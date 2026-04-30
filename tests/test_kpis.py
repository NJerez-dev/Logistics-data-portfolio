"""Tests for the KPI calculations."""
from __future__ import annotations

import pandas as pd

from inventory import (
    STATUS_ALERT,
    STATUS_CRITICAL,
    STATUS_HEALTHY,
    compute_product_kpis,
    compute_warehouse_kpis,
    latest_stock_per_product,
    status_for,
)


def test_safety_stock_non_negative(small_dataset):
    kpis = compute_product_kpis(small_dataset, z=1.645)
    assert (kpis["safety_stock"] >= 0).all()


def test_reorder_point_at_least_safety_stock(small_dataset):
    kpis = compute_product_kpis(small_dataset, z=1.645)
    assert (kpis["reorder_point"] >= kpis["safety_stock"]).all()


def test_higher_service_level_implies_higher_safety_stock(small_dataset):
    low = compute_product_kpis(small_dataset, z=1.282)  # 90 %
    high = compute_product_kpis(small_dataset, z=2.326)  # 99 %
    merged = low.merge(high, on="product_id", suffixes=("_low", "_high"))
    # Should hold for every product with non-zero variability.
    increasing = (merged["safety_stock_high"] >= merged["safety_stock_low"]).mean()
    assert increasing >= 0.95


def test_warehouse_kpis_have_one_row_per_pair(small_dataset):
    kpis = compute_warehouse_kpis(small_dataset)
    pairs = small_dataset[["product_id", "warehouse"]].drop_duplicates()
    assert len(kpis) == len(pairs)


def test_kpi_columns_present(small_dataset):
    expected = {
        "product_id",
        "product_name",
        "category",
        "supplier_lead_time",
        "avg_demand",
        "std_demand",
        "safety_stock",
        "reorder_point",
    }
    assert expected.issubset(set(compute_product_kpis(small_dataset).columns))


def test_latest_stock_returns_one_row_per_product(small_dataset):
    latest = latest_stock_per_product(small_dataset)
    assert latest["product_id"].is_unique
    assert set(latest["product_id"]) == set(small_dataset["product_id"])


def test_status_for_thresholds():
    assert status_for(current_stock=10, reorder_point=20, avg_demand=2, buffer_days=7) == STATUS_CRITICAL
    # exactly at ROP → not critical
    assert status_for(current_stock=20, reorder_point=20, avg_demand=2, buffer_days=7) == STATUS_ALERT
    # ROP + buffer*demand boundary
    assert status_for(current_stock=33, reorder_point=20, avg_demand=2, buffer_days=7) == STATUS_ALERT
    assert status_for(current_stock=34, reorder_point=20, avg_demand=2, buffer_days=7) == STATUS_HEALTHY


def test_kpis_handle_constant_demand_without_nan():
    """A product with std=0 must yield SS=0, never NaN."""
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=10),
            "product_id": 1,
            "product_name": "X",
            "category": "Home",
            "warehouse": "Santiago",
            "units_sold": [3] * 10,
            "unit_price": 1000,
            "revenue": [3000] * 10,
            "stock_level": [50] * 10,
            "reorder_point": 20,
            "supplier_lead_time": 5,
        }
    )
    kpis = compute_product_kpis(df, z=1.645)
    assert kpis["safety_stock"].iloc[0] == 0
    assert not kpis["safety_stock"].isna().any()
