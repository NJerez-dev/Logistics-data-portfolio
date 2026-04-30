"""Project-wide constants and defaults."""
from __future__ import annotations

CATEGORIES: tuple[str, ...] = ("Electronics", "Home", "Industrial", "Food")
WAREHOUSES: tuple[str, ...] = ("Santiago", "Valparaiso", "Concepcion")

# Z-score for one-tailed normal at a given service level.
SERVICE_LEVELS: dict[str, float] = {
    "90%": 1.282,
    "95%": 1.645,
    "97.5%": 1.960,
    "99%": 2.326,
}

# Traffic-light labels (kept here so app + notebook agree).
STATUS_CRITICAL = "🔴 Crítico"
STATUS_ALERT = "🟡 Alerta"
STATUS_HEALTHY = "🟢 Saludable"

DEFAULT_PARAMS = {
    "n_products": 50,
    "n_days": 365,
    "warehouses": WAREHOUSES,
    "seed": 42,
}
