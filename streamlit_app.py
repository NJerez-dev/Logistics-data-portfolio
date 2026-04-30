"""Streamlit dashboard for the Logistics Inventory Portfolio.

Run locally:
    streamlit run streamlit_app.py

Deploy: push to GitHub and connect the repo on https://streamlit.io/cloud
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = Path(__file__).parent / "inventory_transactions.csv"

SERVICE_LEVELS: dict[str, float] = {
    "90%": 1.282,
    "95%": 1.645,
    "97.5%": 1.960,
    "99%": 2.326,
}

STATUS_CRITICAL = "🔴 Crítico"
STATUS_ALERT = "🟡 Alerta"
STATUS_HEALTHY = "🟢 Saludable"
STATUS_COLORS = {
    STATUS_CRITICAL: "#e74c3c",
    STATUS_ALERT: "#f1c40f",
    STATUS_HEALTHY: "#2ecc71",
}

st.set_page_config(
    page_title="Inventory KPIs Dashboard",
    page_icon="📦",
    layout="wide",
)


# --------------------------------------------------------------------------- #
# Data loading & KPI computation                                              #
# --------------------------------------------------------------------------- #
@st.cache_data
def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    return df


@st.cache_data
def compute_product_kpis(df: pd.DataFrame, z: float) -> pd.DataFrame:
    """Aggregate demand to product level and compute SS/ROP."""
    daily = (
        df.groupby(["product_id", "date"])["units_sold"].sum().reset_index()
    )
    stats = (
        daily.groupby("product_id")["units_sold"]
        .agg(["mean", "std"])
        .reset_index()
        .rename(columns={"mean": "avg_demand", "std": "std_demand"})
    )
    details = df[
        ["product_id", "product_name", "category", "supplier_lead_time"]
    ].drop_duplicates()
    out = stats.merge(details, on="product_id")
    out["safety_stock"] = (
        z * out["std_demand"] * np.sqrt(out["supplier_lead_time"])
    ).fillna(0).round().astype(int)
    out["reorder_point"] = (
        out["avg_demand"] * out["supplier_lead_time"] + out["safety_stock"]
    ).round().astype(int)
    return out


@st.cache_data
def compute_warehouse_kpis(df: pd.DataFrame, z: float) -> pd.DataFrame:
    """Compute SS/ROP at the product × warehouse level."""
    daily = (
        df.groupby(["product_id", "warehouse", "date"])["units_sold"]
        .sum()
        .reset_index()
    )
    stats = (
        daily.groupby(["product_id", "warehouse"])["units_sold"]
        .agg(["mean", "std"])
        .reset_index()
        .rename(columns={"mean": "avg_demand", "std": "std_demand"})
    )
    details = df[
        ["product_id", "product_name", "category", "supplier_lead_time"]
    ].drop_duplicates()
    out = stats.merge(details, on="product_id")
    out["safety_stock"] = (
        z * out["std_demand"] * np.sqrt(out["supplier_lead_time"])
    ).fillna(0).round().astype(int)
    out["reorder_point"] = (
        out["avg_demand"] * out["supplier_lead_time"] + out["safety_stock"]
    ).round().astype(int)
    return out


@st.cache_data
def latest_stock_per_product(df: pd.DataFrame) -> pd.DataFrame:
    latest = (
        df.sort_values("date")
        .groupby("product_id")
        .tail(1)[["product_id", "stock_level"]]
        .rename(columns={"stock_level": "current_stock"})
    )
    return latest


def status_for(current: float, rop: int, avg_demand: float, buffer_days: int) -> str:
    if current < rop:
        return STATUS_CRITICAL
    if current < rop + buffer_days * avg_demand:
        return STATUS_ALERT
    return STATUS_HEALTHY


# --------------------------------------------------------------------------- #
# Sidebar                                                                     #
# --------------------------------------------------------------------------- #
df = load_data()

with st.sidebar:
    st.title("📦 Filtros")

    warehouses = st.multiselect(
        "Bodegas",
        sorted(df["warehouse"].unique()),
        default=sorted(df["warehouse"].unique()),
    )
    categories = st.multiselect(
        "Categorías",
        sorted(df["category"].unique()),
        default=sorted(df["category"].unique()),
    )

    st.divider()
    st.header("Política de inventario")

    service_level = st.selectbox(
        "Nivel de servicio",
        options=list(SERVICE_LEVELS.keys()),
        index=1,
        help="Probabilidad de no caer en quiebre de stock durante el lead time.",
    )
    z = SERVICE_LEVELS[service_level]

    buffer_days = st.slider(
        "Buffer 'verde' (días de demanda)",
        min_value=1,
        max_value=30,
        value=7,
        help="Stock = ROP + buffer·demanda_diaria → zona verde.",
    )

    st.divider()
    st.caption(
        "Datos sintéticos generados con `np.random.seed(42)`. "
        "Ver el [notebook](inventory_analysis.ipynb) para detalle de la metodología."
    )


# --------------------------------------------------------------------------- #
# Filter & compute                                                            #
# --------------------------------------------------------------------------- #
df_f = df[df["warehouse"].isin(warehouses) & df["category"].isin(categories)]

st.title("📦 Inventory KPIs Dashboard")
st.caption(
    "Análisis interactivo de ventas, riesgo de quiebre de stock y políticas "
    "de reposición. Mueve los filtros del panel izquierdo para recalcular "
    "los KPIs en vivo."
)

if df_f.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

product_kpis = compute_product_kpis(df_f, z)
stock = latest_stock_per_product(df_f)
prod = product_kpis.merge(stock, on="product_id")
prod["status"] = prod.apply(
    lambda r: status_for(
        r["current_stock"], r["reorder_point"], r["avg_demand"], buffer_days
    ),
    axis=1,
)

# --------------------------------------------------------------------------- #
# Top KPI cards                                                               #
# --------------------------------------------------------------------------- #
total_rev = df_f["revenue"].sum()
total_units = int(df_f["units_sold"].sum())
n_critical = int((prod["status"] == STATUS_CRITICAL).sum())
n_alert = int((prod["status"] == STATUS_ALERT).sum())
n_healthy = int((prod["status"] == STATUS_HEALTHY).sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ingresos totales", f"${total_rev:,.0f}")
c2.metric("Unidades vendidas", f"{total_units:,}")
c3.metric(
    f"{STATUS_CRITICAL}",
    n_critical,
    help="Productos con stock por debajo del ROP",
)
c4.metric(f"{STATUS_ALERT}", n_alert)

# --------------------------------------------------------------------------- #
# Tabs                                                                        #
# --------------------------------------------------------------------------- #
tab_sales, tab_traffic, tab_table = st.tabs(
    ["📊 Resumen de ventas", "🚦 Estado de inventario", "📋 KPIs por producto/bodega"]
)

with tab_sales:
    col_a, col_b = st.columns(2)

    rev_cat = (
        df_f.groupby("category")["revenue"]
        .sum()
        .sort_values()
        .reset_index()
    )
    fig = px.bar(
        rev_cat,
        x="revenue",
        y="category",
        orientation="h",
        title="Ingresos por categoría",
        labels={"revenue": "Ingresos", "category": "Categoría"},
    )
    col_a.plotly_chart(fig, width="stretch")

    rev_wh = (
        df_f.groupby("warehouse")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    fig = px.bar(
        rev_wh,
        x="warehouse",
        y="revenue",
        title="Ingresos por bodega",
        labels={"revenue": "Ingresos", "warehouse": "Bodega"},
    )
    col_b.plotly_chart(fig, width="stretch")

    top10 = (
        df_f.groupby("product_name")["revenue"]
        .sum()
        .nlargest(10)
        .sort_values()
        .reset_index()
    )
    fig = px.bar(
        top10,
        x="revenue",
        y="product_name",
        orientation="h",
        title="Top 10 productos por ingresos",
        labels={"revenue": "Ingresos", "product_name": "Producto"},
    )
    st.plotly_chart(fig, width="stretch")

with tab_traffic:
    st.subheader("Estado de inventario por producto")
    st.caption(
        "Cada barra es el stock actual; la línea negra marca el ROP. "
        "Los productos están ordenados por nivel de riesgo."
    )

    status_order = {STATUS_CRITICAL: 1, STATUS_ALERT: 2, STATUS_HEALTHY: 3}
    sorted_prods = prod.assign(
        _order=prod["status"].map(status_order)
    ).sort_values(["_order", "current_stock"])

    fig = px.bar(
        sorted_prods,
        x="product_name",
        y="current_stock",
        color="status",
        color_discrete_map=STATUS_COLORS,
        hover_data={
            "reorder_point": True,
            "safety_stock": True,
            "category": True,
            "_order": False,
        },
        labels={
            "current_stock": "Stock actual",
            "product_name": "Producto",
            "status": "Estado",
        },
        title="",
    )
    fig.add_scatter(
        x=sorted_prods["product_name"],
        y=sorted_prods["reorder_point"],
        mode="markers",
        name="Punto de reorden",
        marker=dict(color="black", symbol="line-ew", size=12, line=dict(width=3)),
    )
    fig.update_layout(xaxis_tickangle=-60, height=500)
    st.plotly_chart(fig, width="stretch")

    st.subheader("Distribución del estado del catálogo")
    pie = px.pie(
        names=[STATUS_CRITICAL, STATUS_ALERT, STATUS_HEALTHY],
        values=[n_critical, n_alert, n_healthy],
        color=[STATUS_CRITICAL, STATUS_ALERT, STATUS_HEALTHY],
        color_discrete_map=STATUS_COLORS,
        hole=0.5,
    )
    st.plotly_chart(pie, width="stretch")

with tab_table:
    wh_kpis = compute_warehouse_kpis(df_f, z)
    st.dataframe(
        wh_kpis[
            [
                "product_id",
                "product_name",
                "warehouse",
                "category",
                "avg_demand",
                "std_demand",
                "supplier_lead_time",
                "safety_stock",
                "reorder_point",
            ]
        ].sort_values(["product_id", "warehouse"]),
        width="stretch",
        hide_index=True,
    )
    st.download_button(
        "⬇️ Descargar como CSV",
        wh_kpis.to_csv(index=False).encode("utf-8"),
        file_name=f"kpis_servicio_{service_level}.csv",
        mime="text/csv",
    )
