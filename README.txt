# Proyecto: Optimización y Análisis de Inventario

## Descripción del Proyecto
Este proyecto se centra en el análisis de datos de ventas e inventario para un negocio de e-commerce simulado. El objetivo principal es proporcionar información detallada sobre el rendimiento de las ventas, identificar posibles problemas de inventario (como quiebres de stock) y calcular KPIs clave de gestión de inventario, como el Punto de Reorden (ROP) y el Stock de Seguridad (SS) a varios niveles (producto, bodega, categoría).

## Contenidos del Repositorio
El repositorio contiene los siguientes archivos clave:
*   `inventory_transactions.csv`: El conjunto de datos crudo generado mediante simulación, que contiene movimientos diarios de ventas e inventario para varios productos en diferentes bodegas.
*   `inventario_kpis.xlsx`: Un informe de Excel que resume los indicadores clave de rendimiento (KPIs) para la gestión de inventario. Este archivo incluye tablas detalladas y visualizaciones incrustadas del estado de ventas e inventario.
*   Archivos de imágenes PNG (por ejemplo, `revenue_by_category.png`, `inventory_status_by_product.png`, `reorder_point_safety_stock_by_category_warehouse.png`, etc.): Gráficos individuales generados durante el análisis, también incrustados en el informe de Excel.
*   `[nombre-del-notebook].ipynb`: El archivo Jupyter Notebook que contiene todo el código para la generación de datos, análisis, visualización y exportación.
*   `README.md`: Este archivo, que proporciona una visión general del proyecto.

## Análisis Realizado
1.  **Generación y Carga de Datos**: Se crearon datos simulados de ventas e inventario para 50 productos en 3 bodegas durante 180 días. Los datos se cargaron y se inspeccionaron para verificar su calidad.
2.  **Análisis de Ventas**:
    *   Cálculo de ingresos totales y unidades vendidas.
    *   Análisis de la distribución de ingresos por categoría de producto y bodega.
    *   Identificación de los productos con mejor rendimiento por ingresos.
3.  **Análisis de Inventario**:
    *   Cálculo de los niveles promedio de stock por producto.
    *   Identificación de productos con riesgo de quiebre de stock al comparar el stock actual con los puntos de reorden.
4.  **Cálculo de KPIs de Inventario**:
    *   Cálculo de estadísticas de demanda diaria (media y desviación estándar) por producto y bodega.
    *   Cálculo del Stock de Seguridad (SS) y el Punto de Reorden (ROP) para cada combinación producto-bodega, utilizando un nivel de servicio del 95% (Z=1.645).
    *   Agregación de ROP y SS por categoría y bodega.
5.  **Visualización**:
    *   Se generaron varios gráficos para visualizar tendencias de ventas, rendimiento por categoría y estado del inventario.
    *   Se creó una visualización tipo "Semáforo" para mostrar los niveles de stock actuales en relación con los puntos de reorden calculados, indicando el riesgo de inventario.
    *   Se crearon visualizaciones para ROP y SS a niveles agregados y para productos específicos.
6.  **Generación de Reportes**: Todas las tablas y gráficos generados se exportaron a un archivo Excel multi-hoja (`inventario_kpis.xlsx`).

## Conclusiones Clave
1.  La categoría 'Industrial' genera el mayor volumen de ingresos.
2.  La bodega de 'Santiago' concentra la mayor demanda.
3.  Se detectaron múltiples casos donde los niveles de stock caen por debajo del punto de reorden, lo que indica riesgos potenciales de quiebre de stock.
4.  Esto sugiere oportunidades para mejorar las políticas de reabastecimiento mediante una gestión de KPIs basada en datos.

## Cómo Reproducir el Análisis
1.  Asegúrate de tener Python instalado junto con las librerías `pandas`, `numpy`, `matplotlib`, `seaborn` y `xlsxwriter`.
2.  Abre el Jupyter Notebook Análisis_Inventario.ipynb`.
3.  Ejecuta todas las celdas del notebook secuencialmente. Esto realizará las siguientes acciones:
    *   Generará el conjunto de datos sintéticos.
    *   Realizará todos los análisis de ventas e inventario.
    *   Generará y guardará todos los gráficos como archivos PNG.
    *   Exportará todos los dataframes relevantes e incrustará los gráficos generados en el archivo `inventario_kpis.xlsx`.