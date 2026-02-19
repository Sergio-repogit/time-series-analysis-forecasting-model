# Time Series Analysis and Forecasting

Este repositorio recoge un flujo completo de análisis de series temporales, desde el análisis exploratorio y estudio de estacionariedad hasta la modelización y clusters y la implementación de funciones auxiliares reutilizables.

El proyecto está orientado a buenas prácticas en análisis temporal usando Python y `statsmodels`.

---

## Estructura del proyecto

### `time_series_eda_and_stationarity`
Análisis exploratorio inicial de la serie temporal.

**Contenido principal:**
- Carga y limpieza del dataset
- Análisis descriptivo
- Visualización de la serie
- Detección de tendencia y estacionalidad
- Descomposición temporal (opcional)
- Primer estudio de estacionariedad

**Objetivo:**  
Entender la estructura de la serie antes de modelar.

---

### `sarima_modeling_and_forecasting`
Modelización y predicción con modelos SARIMA.

**Contenido principal:**
- Transformaciones para estacionarizar la serie
- Análisis ACF y PACF
- Selección de órdenes $(p,d,q)(P,D,Q)_s$
- Entrenamiento del modelo SARIMA, SARIMAX, VAR, LSTM 
- Diagnóstico de residuos
- Forecast y visualización de predicciones

**Objetivo:**  
Construir un modelo predictivo robusto para la serie temporal.

---

### `funciones_auxiliares.py`
Módulo de utilidades reutilizables para el análisis.

**Funciones incluidas:**
- `contar_outliers_iqr` → detección de outliers mediante IQR
- `seleccionar_sede` → filtrado interactivo por estación
- `cambio_temp` → conversión de Fahrenheit a Celsius
- `obtener_q_optimo` → estimación del orden MA usando ACF

**Objetivo:**  
Facilitar la reutilización de código y mantener notebooks limpios.

---

##Flujo de trabajo recomendado

No hay un flujo predeterminado ya que para la modelización ya se ha realizado el ETL pero la explicación se hace en time_series_eda_and_stationarity

---

## Tecnologías utilizadas

- Python
- pandas
- numpy
- matplotlib
- statsmodels

---

## Posibles mejoras futuras

- Automatización de selección de hiperparámetros
- Backtesting con validación temporal
- Extensión a modelos de DL
- Pipeline reproducible end-to-end

---

## Autor

**Sergio Mínguez Cruces**  
Grado en Matemáticas — Computación y Data Science
