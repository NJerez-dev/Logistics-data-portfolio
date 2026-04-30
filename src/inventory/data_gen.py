"""Synthetic inventory + sales data generator.

Improvements over the prior simple Poisson approach:

- **ABC curve**: baseline demand follows a Pareto distribution, so ~20 % of
  SKUs drive most of the revenue (matches real retail).
- **Weekly seasonality**: demand peaks midweek, dips on weekends.
- **Annual seasonality**: peaks in late November (Black Friday / holidays),
  dips in February.
- **Per-product trend**: each (product, warehouse) gets a small linear drift
  so some products are growing and others declining.
- **Promotional spikes**: random days with a demand uplift.
- **Coherent stock evolution**: ``stock_t = max(0, stock_{t-1} - sold_t + arrivals_t)``
  — stockouts and replenishments are simulated end-to-end.
- **Log-normal lead times**: each replenishment order takes a different
  number of days to arrive, drawn from a log-normal centered on the
  product's nominal lead time.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from inventory.config import CATEGORIES, WAREHOUSES


@dataclass
class GenerationParams:
    n_products: int = 50
    n_days: int = 365
    warehouses: tuple[str, ...] = WAREHOUSES
    start_date: str = "2024-01-01"
    seed: int = 42
    promo_probability: float = 0.02
    promo_uplift: float = 2.5
    pareto_shape: float = 1.16  # 80/20 rule
    weekly_amplitude: float = 0.15
    annual_amplitude: float = 0.20
    annual_peak_doy: int = 330  # late November
    initial_stock_days: int = 30
    order_qty_days: int = 30
    lead_time_sigma: float = 0.30  # log-normal sigma
    categories: tuple[str, ...] = field(default_factory=lambda: CATEGORIES)


def _build_catalog(rng: np.random.Generator, params: GenerationParams) -> pd.DataFrame:
    n = params.n_products
    baseline = rng.pareto(params.pareto_shape, n) + 0.3
    baseline = baseline / baseline.mean() * 4.0  # mean ~ 4 units / day / warehouse

    return pd.DataFrame(
        {
            "product_id": np.arange(1, n + 1),
            "product_name": [f"Product_{i}" for i in range(1, n + 1)],
            "category": rng.choice(params.categories, n),
            "unit_price": rng.integers(5_000, 50_000, n),
            "baseline_demand": baseline,
            "supplier_lead_time": rng.integers(3, 15, n),
        }
    )


def _seasonality(dates: pd.DatetimeIndex, params: GenerationParams) -> np.ndarray:
    dow = dates.dayofweek.to_numpy()
    weekly = 1.0 + params.weekly_amplitude * np.cos(2 * np.pi * (dow - 2) / 7)

    doy = dates.dayofyear.to_numpy()
    annual = 1.0 + params.annual_amplitude * np.cos(
        2 * np.pi * (doy - params.annual_peak_doy) / 365
    )
    return weekly * annual


def _simulate_pair(
    rng: np.random.Generator,
    product: pd.Series,
    warehouse: str,
    dates: pd.DatetimeIndex,
    seasonal: np.ndarray,
    params: GenerationParams,
) -> pd.DataFrame:
    n = len(dates)
    baseline = product["baseline_demand"]

    # Per-pair linear trend: between -0.05% and +0.15% per day.
    slope = rng.uniform(-0.0005, 0.0015)
    trend = 1.0 + slope * np.arange(n)

    promo = rng.random(n) < params.promo_probability
    promo_factor = np.where(promo, params.promo_uplift, 1.0)

    lambdas = np.maximum(baseline * seasonal * trend * promo_factor, 0.05)

    # Replenishment policy: when stock < ROP, place order for Q units that
    # arrives after a sampled lead time.
    rop = max(int(baseline * product["supplier_lead_time"] * 1.3), 5)
    Q = max(int(baseline * params.order_qty_days), 10)
    initial_stock = int(baseline * params.initial_stock_days)
    mu_lt = np.log(max(product["supplier_lead_time"], 1))

    units_sold = np.zeros(n, dtype=int)
    stock_after = np.zeros(n, dtype=int)
    pending: list[tuple[int, int]] = []  # (arrival_day, qty)
    stock = initial_stock

    for t in range(n):
        # 1) Receive any orders that arrive today.
        arrivals_today = sum(q for d, q in pending if d == t)
        stock += arrivals_today
        pending = [(d, q) for d, q in pending if d > t]

        # 2) Realize today's demand, capped by available stock.
        demand = rng.poisson(lambdas[t])
        sold = min(demand, stock)
        units_sold[t] = sold
        stock -= sold
        stock_after[t] = stock

        # 3) Place a replenishment order if below ROP and nothing pending.
        if stock < rop and not pending:
            lt = max(1, int(round(rng.lognormal(mu_lt, params.lead_time_sigma))))
            pending.append((t + lt, Q))

    return pd.DataFrame(
        {
            "date": dates,
            "product_id": int(product["product_id"]),
            "product_name": product["product_name"],
            "category": product["category"],
            "warehouse": warehouse,
            "units_sold": units_sold,
            "unit_price": int(product["unit_price"]),
            "revenue": units_sold * int(product["unit_price"]),
            "stock_level": stock_after,
            "reorder_point": rop,
            "supplier_lead_time": int(product["supplier_lead_time"]),
        }
    )


def generate_dataset(params: GenerationParams | None = None) -> pd.DataFrame:
    """Generate a realistic synthetic sales/inventory dataset.

    Parameters
    ----------
    params : GenerationParams, optional
        Generation parameters. If ``None``, defaults are used (50 products,
        365 days, three warehouses, seed 42).

    Returns
    -------
    pd.DataFrame
        One row per (date, product, warehouse) with units sold, revenue and
        end-of-day stock level.
    """
    if params is None:
        params = GenerationParams()
    rng = np.random.default_rng(params.seed)

    catalog = _build_catalog(rng, params)
    dates = pd.date_range(start=params.start_date, periods=params.n_days)
    seasonal = _seasonality(dates, params)

    chunks: list[pd.DataFrame] = []
    for warehouse in params.warehouses:
        for _, product in catalog.iterrows():
            chunks.append(_simulate_pair(rng, product, warehouse, dates, seasonal, params))

    return pd.concat(chunks, ignore_index=True)
