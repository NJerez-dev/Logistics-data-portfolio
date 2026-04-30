"""Logistics inventory analysis toolkit.

Public API:
    generate_dataset      Synthetic but realistic sales/inventory data.
    compute_product_kpis  Safety stock and reorder point at the product level.
    compute_warehouse_kpis Same, broken down by warehouse.
    status_for            Traffic-light classification for current stock.
    SERVICE_LEVELS        Mapping from human-readable level to Z-score.
"""
from inventory.config import (
    CATEGORIES,
    DEFAULT_PARAMS,
    SERVICE_LEVELS,
    STATUS_ALERT,
    STATUS_CRITICAL,
    STATUS_HEALTHY,
    WAREHOUSES,
)
from inventory.data_gen import GenerationParams, generate_dataset
from inventory.kpis import (
    compute_product_kpis,
    compute_warehouse_kpis,
    latest_stock_per_product,
    status_for,
)

__all__ = [
    "CATEGORIES",
    "DEFAULT_PARAMS",
    "SERVICE_LEVELS",
    "STATUS_ALERT",
    "STATUS_CRITICAL",
    "STATUS_HEALTHY",
    "WAREHOUSES",
    "GenerationParams",
    "generate_dataset",
    "compute_product_kpis",
    "compute_warehouse_kpis",
    "latest_stock_per_product",
    "status_for",
]

__version__ = "0.2.0"
