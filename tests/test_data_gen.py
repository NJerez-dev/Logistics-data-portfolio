"""Tests for the synthetic dataset generator."""
from __future__ import annotations

import pandas as pd

from inventory import GenerationParams, generate_dataset

EXPECTED_COLUMNS = {
    "date",
    "product_id",
    "product_name",
    "category",
    "warehouse",
    "units_sold",
    "unit_price",
    "revenue",
    "stock_level",
    "reorder_point",
    "supplier_lead_time",
}


def test_schema(small_dataset):
    assert set(small_dataset.columns) == EXPECTED_COLUMNS


def test_no_nulls(small_dataset):
    assert small_dataset.isna().sum().sum() == 0


def test_non_negative_invariants(small_dataset):
    for col in ("units_sold", "stock_level", "revenue"):
        assert (small_dataset[col] >= 0).all(), f"{col} has negative values"


def test_revenue_matches_price_and_units(small_dataset):
    expected = small_dataset["units_sold"] * small_dataset["unit_price"]
    assert (small_dataset["revenue"] == expected).all()


def test_dimensions_match_params():
    params = GenerationParams(n_products=5, n_days=30, seed=7)
    df = generate_dataset(params)
    expected_rows = params.n_products * len(params.warehouses) * params.n_days
    assert len(df) == expected_rows
    assert df["product_id"].nunique() == params.n_products
    assert set(df["warehouse"].unique()) == set(params.warehouses)


def test_deterministic_under_same_seed():
    a = generate_dataset(GenerationParams(n_products=8, n_days=30, seed=99))
    b = generate_dataset(GenerationParams(n_products=8, n_days=30, seed=99))
    pd.testing.assert_frame_equal(a, b)


def test_different_seeds_produce_different_data():
    a = generate_dataset(GenerationParams(n_products=8, n_days=30, seed=1))
    b = generate_dataset(GenerationParams(n_products=8, n_days=30, seed=2))
    assert not a["units_sold"].equals(b["units_sold"])


def test_abc_curve_top_quintile_dominates():
    """The Pareto baseline should make ~20 % of products carry most revenue."""
    df = generate_dataset(GenerationParams(n_products=50, n_days=180, seed=42))
    by_product = df.groupby("product_id")["revenue"].sum().sort_values(ascending=False)
    top_quintile = int(len(by_product) * 0.2)
    share = by_product.iloc[:top_quintile].sum() / by_product.sum()
    assert share > 0.40, f"Top 20% only carries {share:.2%} of revenue"


def test_seasonality_present():
    """A full year of data should show a higher mean in Nov-Dec than in Feb."""
    df = generate_dataset(GenerationParams(n_products=20, n_days=365, seed=42))
    df = df.assign(month=pd.to_datetime(df["date"]).dt.month)
    nov_dec = df.loc[df["month"].isin([11, 12]), "units_sold"].mean()
    feb = df.loc[df["month"] == 2, "units_sold"].mean()
    assert nov_dec > feb, f"No seasonal lift detected (Nov-Dec={nov_dec:.2f}, Feb={feb:.2f})"
