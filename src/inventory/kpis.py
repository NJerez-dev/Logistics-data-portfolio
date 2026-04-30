"""Inventory KPI calculations: safety stock, reorder point, traffic light."""
from __future__ import annotations

import numpy as np
import pandas as pd

from inventory.config import STATUS_ALERT, STATUS_CRITICAL, STATUS_HEALTHY


def _kpi_frame(daily: pd.DataFrame, group_cols: list[str], details: pd.DataFrame, z: float) -> pd.DataFrame:
    stats = (
        daily.groupby(group_cols)["units_sold"]
        .agg(["mean", "std"])
        .reset_index()
        .rename(columns={"mean": "avg_demand", "std": "std_demand"})
    )
    out = stats.merge(details, on="product_id")
    out["safety_stock"] = (
        z * out["std_demand"] * np.sqrt(out["supplier_lead_time"])
    ).fillna(0).round().astype(int)
    out["reorder_point"] = (
        out["avg_demand"] * out["supplier_lead_time"] + out["safety_stock"]
    ).round().astype(int)
    return out


def compute_product_kpis(df: pd.DataFrame, z: float = 1.645) -> pd.DataFrame:
    """Aggregate demand to product level (across warehouses) and compute SS / ROP.

    Returns columns: product_id, product_name, category, supplier_lead_time,
    avg_demand, std_demand, safety_stock, reorder_point.
    """
    daily = df.groupby(["product_id", "date"])["units_sold"].sum().reset_index()
    details = df[
        ["product_id", "product_name", "category", "supplier_lead_time"]
    ].drop_duplicates()
    return _kpi_frame(daily, ["product_id"], details, z)


def compute_warehouse_kpis(df: pd.DataFrame, z: float = 1.645) -> pd.DataFrame:
    """SS / ROP at the (product × warehouse) level."""
    daily = (
        df.groupby(["product_id", "warehouse", "date"])["units_sold"]
        .sum()
        .reset_index()
    )
    details = df[
        ["product_id", "product_name", "category", "supplier_lead_time"]
    ].drop_duplicates()
    return _kpi_frame(daily, ["product_id", "warehouse"], details, z)


def latest_stock_per_product(df: pd.DataFrame) -> pd.DataFrame:
    """Return product_id → most recent stock_level (averaged across warehouses)."""
    last_date = df["date"].max()
    return (
        df.loc[df["date"] == last_date]
        .groupby("product_id")["stock_level"]
        .mean()
        .round()
        .astype(int)
        .reset_index()
        .rename(columns={"stock_level": "current_stock"})
    )


def status_for(current_stock: float, reorder_point: float, avg_demand: float, buffer_days: int) -> str:
    """Classify a product's stock as red / yellow / green."""
    if current_stock < reorder_point:
        return STATUS_CRITICAL
    if current_stock < reorder_point + buffer_days * avg_demand:
        return STATUS_ALERT
    return STATUS_HEALTHY
