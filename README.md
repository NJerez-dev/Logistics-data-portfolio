# Optimización y Análisis de Inventario

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NJerez-dev/Logistics-data-portfolio/blob/main/inventory_analysis.ipynb)

Proyecto de portfolio que analiza datos simulados de ventas e inventario de un
e-commerce para identificar riesgos de quiebre de stock y calcular KPIs de
gestión de inventario (Punto de Reorden y Stock de Seguridad) por producto,
bodega y categoría.

## Tabla de contenidos

- [Objetivo](#objetivo)
- [Stack técnico](#stack-técnico)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Cómo reproducir el análisis](#cómo-reproducir-el-análisis)
- [Análisis realizado](#análisis-realizado)
- [KPIs calculados](#kpis-calculados)
- [Conclusiones clave](#conclusiones-clave)
- [Próximos pasos](#próximos-pasos)
- [Licencia](#licencia)

## Objetivo

Mostrar un flujo end-to-end de análisis de datos logísticos:

1. **Generación** de un dataset sintético realista (50 productos × 3 bodegas × 180 días).
2. **Exploración** de ventas por categoría, bodega y producto.
3. **Detección** de productos en riesgo de quiebre de stock.
4. **Cálculo** de KPIs de reposición (ROP, Stock de Seguridad) con un nivel de servicio del 95%.
5. **Visualización** tipo "semáforo" del estado del inventario.
6. **Reporting** en un libro Excel multi-hoja con gráficos embebidos.

## Stack técnico

| Herramienta   | Uso                                              |
| ------------- | ------------------------------------------------ |
| `pandas`      | Manipulación y agregación de datos               |
| `numpy`       | Generación aleatoria y cálculo numérico          |
| `matplotlib`  | Gráficos base                                    |
| `seaborn`     | Estilos y paletas de visualización               |
| `xlsxwriter`  | Exportación a Excel con gráficos embebidos       |
| Jupyter       | Cuaderno interactivo (`inventory_analysis.ipynb`)|

## Estructura del repositorio

```
.
├── inventory_analysis.ipynb     # Notebook principal con todo el análisis
├── inventory_transactions.csv   # Dataset sintético generado (entrada)
├── inventario_kpis.xlsx         # Reporte final multi-hoja (salida)
├── requirements.txt             # Dependencias del proyecto
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
- 180 días de transacciones diarias con demanda Poisson y stock normal.

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

## Conclusiones clave

1. La categoría **Industrial** concentra el mayor volumen de ingresos.
2. La bodega de **Santiago** es la de mayor demanda.
3. Se detectan múltiples casos de `stock < ROP`, evidenciando riesgo de
   quiebre y oportunidades para ajustar políticas de reposición.
4. La tabla de ROP/SS por categoría-bodega permite priorizar dónde concentrar
   esfuerzos logísticos.

## Próximos pasos

- Incorporar **estacionalidad** en la simulación de demanda.
- Modelar **lead times variables** con distribución log-normal.
- Comparar la política `(s, S)` vs. `(R, Q)` para distintos productos.
- Conectar el pipeline a un dashboard en **Streamlit** o **Power BI**.

## Licencia

Distribuido bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.
