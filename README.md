# Optimización y Análisis de Inventario

[![CI](https://github.com/NJerez-dev/Logistics-data-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/NJerez-dev/Logistics-data-portfolio/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NJerez-dev/Logistics-data-portfolio/blob/main/inventory_analysis.ipynb)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://logistics-data-portfolio-k9zdgvvcqnzzguigqdppa5.streamlit.app/)

Proyecto de portfolio que analiza datos simulados de ventas e inventario de un
e-commerce para identificar riesgos de quiebre de stock y calcular KPIs de
gestión de inventario (Punto de Reorden y Stock de Seguridad) por producto,
bodega y categoría.

> 🔗 **Demo en vivo:** <https://logistics-data-portfolio-k9zdgvvcqnzzguigqdppa5.streamlit.app/>

## Tabla de contenidos

- [Objetivo](#objetivo)
- [Dashboard interactivo](#dashboard-interactivo)
- [El paquete `inventory`](#el-paquete-inventory)
- [Generador de datos realista](#generador-de-datos-realista)
- [Stack técnico](#stack-técnico)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Cómo reproducir el análisis](#cómo-reproducir-el-análisis)
- [Análisis realizado](#análisis-realizado)
- [KPIs calculados](#kpis-calculados)
- [Tests y CI](#tests-y-ci)
- [Conclusiones clave](#conclusiones-clave)
- [Próximos pasos](#próximos-pasos)
- [Licencia](#licencia)

## Objetivo

Mostrar un flujo end-to-end de análisis de datos logísticos:

1. **Generación** de un dataset sintético realista (50 productos × 3 bodegas × 365 días, con estacionalidad anual y semanal, curva ABC, lead times log-normales y stock evolucionado de forma coherente).
2. **Exploración** de ventas por categoría, bodega y producto.
3. **Detección** de productos en riesgo de quiebre de stock.
4. **Cálculo** de KPIs de reposición (ROP, Stock de Seguridad) con un nivel de servicio del 95 %.
5. **Visualización** tipo "semáforo" del estado del inventario.
6. **Reporting** en un libro Excel multi-hoja y en un **dashboard interactivo de Streamlit**.
7. **Calidad de código**: paquete instalable con `pyproject.toml`, suite de `pytest` y CI con GitHub Actions.

## Dashboard interactivo

🌐 **Pruébalo aquí:** <https://logistics-data-portfolio-k9zdgvvcqnzzguigqdppa5.streamlit.app/>

El proyecto incluye un dashboard en **Streamlit** que permite explorar los KPIs
en vivo: filtrar por bodega y categoría, ajustar el nivel de servicio (90 % a
99 %) y el buffer del semáforo, y descargar la tabla resultante de ROP/SS en CSV.

### Correr el dashboard localmente

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Abre tu navegador en [http://localhost:8501](http://localhost:8501).

### Despliegue en Streamlit Community Cloud

1. Haz fork de este repositorio en tu cuenta de GitHub.
2. Ve a [streamlit.io/cloud](https://streamlit.io/cloud) e inicia sesión con GitHub.
3. Pulsa **New app**, selecciona el repo y elige `streamlit_app.py` como
   archivo principal.
4. La app quedará pública en una URL del estilo
   `https://<tu-usuario>-logistics-data-portfolio.streamlit.app`.

> Una vez desplegada, reemplaza la URL en el badge de Streamlit al inicio del
> README para que apunte directamente a tu instancia.

### Vista general

| Sección                         | Qué muestra                                                       |
| ------------------------------- | ----------------------------------------------------------------- |
| **KPI cards**                   | Ingresos, unidades vendidas, conteo de productos críticos/alerta. |
| **📊 Resumen de ventas**        | Ingresos por categoría, por bodega y top 10 productos.            |
| **🚦 Estado de inventario**     | Semáforo por producto (rojo/amarillo/verde) + ROP overlay.        |
| **📋 KPIs por producto/bodega** | Tabla detallada filtrable + descarga en CSV.                      |

## El paquete `inventory`

La lógica de negocio vive en `src/inventory/` como paquete Python instalable
y testeado, no en celdas de notebook copiadas.

```python
from inventory import (
    generate_dataset,
    compute_product_kpis,
    compute_warehouse_kpis,
    status_for,
    SERVICE_LEVELS,
)

df = generate_dataset()                       # dataset sintético realista
kpis = compute_product_kpis(df, z=1.645)      # SS y ROP por producto
status_for(stock=10, rop=20, avg_demand=2, buffer_days=7)
# → '🔴 Crítico'
```

Se instala en modo editable con:

```bash
pip install -e ".[dev]"
```

| Módulo                  | Responsabilidad                                          |
| ----------------------- | -------------------------------------------------------- |
| `inventory.config`      | Constantes (Z-scores, categorías, bodegas, etiquetas).   |
| `inventory.data_gen`    | Generador sintético con estacionalidad y stock coherente.|
| `inventory.kpis`        | `compute_product_kpis`, `compute_warehouse_kpis`, etc.   |

El notebook y el dashboard de Streamlit consumen esta misma API, por lo que
los cálculos están garantizados consistentes entre ambos.

## Generador de datos realista

El módulo `inventory.data_gen` reemplaza la simulación trivial original
(Poisson uniforme + stock independiente) por algo que se parece a retail real:

| Característica           | Detalle                                                                  |
| ------------------------ | ------------------------------------------------------------------------ |
| **Curva ABC**            | Demanda baseline ~ Pareto: ~20 % de los SKUs concentran la mayor parte de los ingresos. |
| **Estacionalidad anual** | Pico en noviembre-diciembre (Black Friday + holidays), valle en febrero. |
| **Estacionalidad semanal** | Pico de lunes a jueves, caída los fines de semana.                     |
| **Tendencia por SKU**    | Cada combinación producto-bodega tiene una pendiente lineal aleatoria.   |
| **Promociones**          | ~2 % de los días tienen un uplift de demanda × 2,5.                      |
| **Stock coherente**      | `stock_t = max(0, stock_{t−1} − sold_t + arrivals_t)` — los quiebres son **emergentes**, no un artefacto de muestreo. |
| **Lead times log-normales** | Cada orden de reposición tarda un tiempo distinto en llegar.          |
| **Política (s, Q)**      | Cuando `stock < ROP`, se dispara una orden de tamaño `Q`.                |

Todos estos parámetros se exponen en `GenerationParams` para experimentación.

## Stack técnico

| Herramienta   | Uso                                              |
| ------------- | ------------------------------------------------ |
| `pandas`      | Manipulación y agregación de datos               |
| `numpy`       | Generación aleatoria y cálculo numérico          |
| `matplotlib`  | Gráficos base                                    |
| `seaborn`     | Estilos y paletas de visualización               |
| `xlsxwriter`  | Exportación a Excel con gráficos embebidos       |
| `streamlit`   | Dashboard interactivo (`streamlit_app.py`)       |
| `plotly`      | Gráficos interactivos del dashboard              |
| Jupyter       | Cuaderno interactivo (`inventory_analysis.ipynb`)|

## Estructura del repositorio

```
.
├── src/inventory/               # Paquete instalable
│   ├── __init__.py
│   ├── config.py                # Constantes (Z, categorías, etiquetas)
│   ├── data_gen.py              # Generador sintético realista
│   └── kpis.py                  # Cálculo de SS / ROP / semáforo
├── tests/                       # Suite de pytest
│   ├── test_data_gen.py
│   └── test_kpis.py
├── .github/workflows/ci.yml     # Lint + tests en GitHub Actions
├── inventory_analysis.ipynb     # Notebook principal con todo el análisis
├── streamlit_app.py             # Dashboard interactivo
├── .streamlit/config.toml       # Tema y configuración del dashboard
├── inventory_transactions.csv   # Dataset sintético generado (entrada)
├── inventario_kpis.xlsx         # Reporte final multi-hoja (salida)
├── pyproject.toml               # Empaquetado + configuración de ruff/pytest
├── requirements.txt             # Dependencias para el dashboard / notebook
├── LICENSE                      # Licencia MIT
└── README.md                    # Este archivo
```

## Cómo reproducir el análisis

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/NJerez-dev/Logistics-data-portfolio.git
   cd Logistics-data-portfolio
   ```

2. **Crear un entorno virtual e instalar dependencias**
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # En Windows: .venv\Scripts\activate
   pip install -e ".[dev,app]"    # paquete + dependencias de tests y dashboard
   # o, si solo quieres correr el notebook / dashboard:
   pip install -r requirements.txt
   ```

3. **Abrir el notebook**
   ```bash
   jupyter notebook inventory_analysis.ipynb
   ```
   o ejecutarlo directamente en
   [Google Colab](https://colab.research.google.com/github/NJerez-dev/Logistics-data-portfolio/blob/main/inventory_analysis.ipynb).

4. **Ejecutar todas las celdas** (`Cell → Run All`). El notebook regenerará
   `inventory_transactions.csv`, calculará los KPIs y producirá
   `inventario_kpis.xlsx`.

## Análisis realizado

### 1. Generación de datos
- 50 productos en 4 categorías (`Electronics`, `Home`, `Industrial`, `Food`).
- 3 bodegas (`Santiago`, `Valparaiso`, `Concepcion`).
- 365 días con demanda Poisson modulada por estacionalidad anual y semanal,
  curva ABC, promociones y stock evolucionado vía política (s, Q).
- Ver [Generador de datos realista](#generador-de-datos-realista) para más detalle.

### 2. Análisis de ventas
- Ingresos totales y unidades vendidas.
- Ranking por **categoría** y por **bodega**.
- Top 10 productos por ingresos.

### 3. Análisis de inventario
- Nivel medio de stock por producto.
- Identificación de productos donde `stock_level < reorder_point`.

### 4. Visualización tipo semáforo
Cada producto se clasifica según su stock actual:

| Color    | Condición                                           |
| -------- | --------------------------------------------------- |
| Rojo     | `stock < reorder_point` (riesgo crítico)            |
| Amarillo | `stock < reorder_point + 7·demanda_diaria_promedio` |
| Verde    | Stock saludable por encima del umbral               |

## KPIs calculados

Para cada combinación **producto × bodega**, con un nivel de servicio del 95%
(`Z = 1.645`):

```
Safety Stock (SS) = Z · σ_demanda · √(lead_time)

Reorder Point (ROP) = demanda_promedio_diaria · lead_time + SS
```

Los KPIs se agregan también a nivel de **categoría × bodega** para apoyar
decisiones tácticas de reabastecimiento.

## Tests y CI

Suite con `pytest` que cubre:

- **Generador**: schema, ausencia de nulos, `units_sold ≥ 0`, `stock_level ≥ 0`,
  determinismo bajo el mismo seed, presencia de la curva ABC y de la
  estacionalidad anual.
- **KPIs**: `safety_stock ≥ 0`, monotonía respecto al nivel de servicio y al
  lead time, fronteras del semáforo, estabilidad ante varianza nula.

Ejecútalos localmente:

```bash
pip install -e ".[dev]"
ruff check src tests
pytest -v
```

GitHub Actions (`.github/workflows/ci.yml`) corre lint + tests automáticamente
en cada push / PR sobre Python 3.10, 3.11 y 3.12.

## Conclusiones clave

1. La categoría **Industrial** concentra el mayor volumen de ingresos.
2. La bodega de **Santiago** es la de mayor demanda.
3. Se detectan múltiples casos de `stock < ROP`, evidenciando riesgo de
   quiebre y oportunidades para ajustar políticas de reposición.
4. La tabla de ROP/SS por categoría-bodega permite priorizar dónde concentrar
   esfuerzos logísticos.

## Próximos pasos

- **Forecasting** de demanda comparando baseline (media móvil) vs. Prophet vs. LightGBM.
- **Simulación Monte Carlo** del fill rate real bajo distintas políticas.
- **Comparación de políticas** `(s, S)` vs. `(R, Q)` vs. base-stock.
- **Clasificación ABC/XYZ** para segmentar la lógica de reposición.
- **Anomaly detection** en las series de ventas.

## Licencia

Distribuido bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.
