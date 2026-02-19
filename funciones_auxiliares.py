
import pandas as pd
from statsmodels.tsa.stattools import acf, pacf
import numpy as np

def contar_outliers_iqr(df):
    """
    Métrica usada en cada columna numérica para ver si es outliers: Q1 - 1.5*IQR y Q3 + 1.5*IQR.
    
    Devuelve un df con el número de outliers por columna.
    """
    outliers_count = {}
    
    for col in df.select_dtypes(include=['number']).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Conteo de outliers
        outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
        outliers_count[col] = outliers
    
    return pd.Series(outliers_count)


def seleccionar_sede(df,palabra = "so"):

    """
    Selecciona los datos de la sede para el estudio 

    Parámetros 

    Palabra: str, Codigo de la estacion que se quiere ver, se inicializa por si no se sabe los codigo
    
    Devuelve
    
    df cuyas observaciones coincidan con el code seleccionado.
    """
    lista = set(df["code"])
    lista.discard("IT0463A")   # No lanza error si no existe

    while palabra not in lista:
        print(lista)
        palabra = input("Selecciones el código de la base que quiera revisar los datos")
        
    print("La base elegida es:", palabra)
    return df[df['code'] == palabra]
    

def cambio_temp(df,columna):
    """  
    Cambia de farengeit a celsius  
    Parámetros

    df: Data frame
    columna: str, Nombre de la columna sobre la que hacer el cambio de unidades

    Devuelve 

    df:  Data frame, cuya columna se ha convertido de farengeit a celsius.
    """
    df[columna]=(df[columna]-32)*5/9
    print(f"La variable {columna} se ha convertido existosamente")
    return df

def obtener_q_optimo(serie, nlags=20, alpha=0.05):
    """
    Calcula el valor óptimo de q (número de rezagos para MA) 
    a partir de la ACF de una serie temporal.

    Parámetros
    
    serie : Serie temporal estacionaria.
    nlags : int, Número máximo de rezagos a considerar.
    alpha : float, Nivel de significancia para el intervalo de confianza.

    Devuelve 

    q_optimo : int, Último lag significativo (valor de q sugerido).
    """

    # Calculamos ACF y límites de confianza
    acf_vals, confint = acf(serie, nlags=nlags, alpha=alpha)

    # Extraemos límites superior e inferior
    lower, upper = confint[:, 0], confint[:, 1]

    # Detectamos los lags significativos
    significativos = [i for i in range(1, nlags+1) if (acf_vals[i] < lower[i]) or (acf_vals[i] > upper[i])]

    # Si no hay lags significativos, devolvemos 0
    if not significativos:
        print(f"El valor estimado de q (MA) es: {0} ya que no se ha llegado a lags significativos en {nlags} lags")
        return 0

    # El q óptimo es el último lag significativo
    q_optimo = significativos[-1]

    print(f"El valor estimado de q (MA) es: {q_optimo}")

    return q_optimo

def obtener_p_optimo(serie, nlags=20, alpha=0.05):
    """
    Calcula el valor óptimo de p (orden AR) usando la PACF.
    
    Parámetros

    serie : Serie temporal estacionaria.
    nlags : int, número máximo de rezagos a considerar (por defecto 20 valores).
    alpha : float, nivel de significancia (por defecto 0.05 para 95% de confianza).
    
    Retorna
   
    p_optimo : int, último lag significativo fuera del intervalo de confianza.
    """

    # Calculamos ACF y límites de confianza
    pacf_vals, confint = pacf(serie, nlags=nlags, alpha=alpha)

    # Extraemos límites superior e inferior
    lower, upper = confint[:, 0], confint[:, 1]

    # Detectamos los lags significativos
    significativos = [i for i in range(1, nlags+1) if (pacf_vals[i] < lower[i]) or (pacf_vals[i] > upper[i])]

    
    # Si no hay lags significativos, devolvemos 0
    if not significativos:
        print(f"El valor estimado de p (AR) es: {0} ya que no se ha llegado a lags significativos en {nlags} lags")
        return 0

    # El q óptimo es el último lag significativo 
    p_optimo = significativos[-1]

    print(f"El valor estimado de p (AR) es: {p_optimo}")
    
    return p_optimo


def comentarios(df):

    """    
    Devuelve un diccionario con los comentarios para cada gráfica (normal, descomposición y descomposición tras resampleo tanto semanal como mensual) de la sede correspondiente.
    """
    codigo = df["code"].iloc[0]
    if codigo == 'ASFF01':
        comentario = {"serie":
    """    La serie temporal indica los niveles de las partículas en suspensión detectadas en ASFF01 a lo largo de dos años.
                      
    En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 5 y 25 µg/m³, pero hay cimas que rebasan los 60 µg/m³. Tales eventos son particularmente significativos puesto que superan ampliamente el umbral de 35 µg/m³,
    que se considera un riesgo para la salud, llegando a valores asociados con graves efectos en poblaciones vulnerables.

    Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³). 
    Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de contaminación más severas por ejemplo,
    principios de 2022 y de 2023.

    Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",
    "descomposicion":
        """        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo depende de
        patrones climáticos estacionales(como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 50 µg/m³, mucho más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa. 
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.
        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad.
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 10 y 25), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando mayoritariamente por debajo de 35, valor a partir se considera un riesgo para la salud.

        - Tendencia (Trend)
        Se observa una tendencia positiva, pero pese a observarse cambios en la gráfica, el valor numérico no cambia practicamente nada si se fija en los valores que toma el eje desde 14 a 15.5 y demostrando la mejoría en la estabilidad.

        - Estacionalidad (Seasonal)
        Se aprecia claramente el patrón anual, esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados..

        - Residuos (Residual/Irregular)
        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a  la diaria.""",

                                "mensual": """        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 10 y 20), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo en 25 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres)

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        }
                
    elif codigo == 'ANCCAMS04':
        comentario = {"serie":
        """        La serie temporal indica los niveles de las partículas en suspensión detectadas en ANCCAMS04 a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 5 y 25 µg/m³, pero hay cimas que rebasan los 35 µg/m³ la cual que se considera segun la OMS un riesgo para la salud,
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³).
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de contaminación más severas
        por ejemplo, finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",
                            "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo depende de
        patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 35 µg/m³, mucho más allá de los parámetros recomendados. 
        La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa. Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.
        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad.
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":
        """        Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 5 y 25), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando por debajo de 35, valor a partir se considera un riesgo para la salud.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual, esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados..

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a  la diaria.""",

                                "mensual": """        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 7.5 y 17.5), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo 17.5 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        }
                
    elif codigo == 'IT1827A':
        comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en IT1827A a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 5 y 40 µg/m³, pero hay cimas que rebasan los 60 µg/m³ la cual se considera segun la OMS un riesgo para la salud,
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de exposición habital de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³).
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de 
        contaminación más severas por ejemplo, finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",
        "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo 
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 60 µg/m³, mucho más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa.
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie, pero si una acentuación en ese segundo ciclo.

        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad.
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 5 y 45), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando en su mayoría por debajo de 35, valor a partir se considera un riesgo para la salud según la OMS.

        - Tendencia (Trend)

        Observando los valores del eje Y practicamente  numéricamente se mantiene estable.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual, esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a  la diaria.""",

                                "mensual": """        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 5 y 25), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo 25 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        }
    elif codigo == 'IT0461A':
        comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en IT0461AA a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 5 y 30 µg/m³, pero hay cimas que rebasan los 40 µg/m³ la cual se considera segun la OMS un riesgo para la salud,
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de exposición habital de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³).
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de 
        contaminación más severas por ejemplo, finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",
        "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 50 µg/m³, mucho más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa.
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie, pero si una acentuación en ese segundo ciclo.

        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad.
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 5 y 30), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando en su mayoría por debajo de 35, valor a partir se considera un riesgo para la salud según la OMS.

        - Tendencia (Trend)

        Observando los valores del eje Y practicamente  numéricamente se mantiene estable.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual, esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a  la diaria.""",

                                "mensual": """        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 5 y 20), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo 20 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        }
    elif codigo == 'ANCCAMS00':
        comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en ANCCAMS00 a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 5 y 30 µg/m³, pero hay cimas que rebasan los 40 µg/m³ la cual se considera segun la OMS un riesgo para la salud,
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de exposición habital de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³).
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de 
        contaminación más severas por ejemplo, finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",

        "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 40 µg/m³, mucho más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa. Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie, pero si una acentuación en ese segundo ciclo.

        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad.
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        "Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 5 y 25), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando por debajo de 35, máximo en 25, valor a partir se considera un riesgo para la salud según la OMS.

        - Tendencia (Trend)

        Observando los valores del eje Y practicamente  numéricamente se mantiene estable.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual, esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a  la diaria.""",

                                "mensual": """        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 7.5 y 17.5), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo 17.5 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        }

    elif codigo == 'ANCCAMS02':
        comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en ANCCAMS02 a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 5 y 30 µg/m³, pero hay cimas que rebasan los 40 µg/m³ la cual se considera segun la OMS un riesgo para la salud,
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de exposición habital de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³).
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de
        contaminación más severas por ejemplo, finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",

        "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 40 µg/m³, mucho más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa.
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie, pero si una acentuación en ese segundo ciclo.

        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad. 
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 5 y 25), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando por debajo de 35, máximo en 25, valor a partir se considera un riesgo para la salud según la OMS.

        - Tendencia (Trend)

        Observando los valores del eje Y practicamente  numéricamente se mantiene estable.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual , esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a  la diaria.""",

                                "mensual":"""        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 10 y 20), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo 20 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        }
    elif codigo == 'ANCCAMS11':
        comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en ANCCAMS11 a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 5 y 30 µg/m³, pero hay cimas que rebasan los 35 µg/m³ la cual se considera segun la OMS un riesgo para la salud,
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de exposición habital de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³).
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de
        contaminación más severas por ejemplo, finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",

        "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo 
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 35 µg/m³, mucho más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa.
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie, pero si una acentuación en ese segundo ciclo.

        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad.
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        "Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 5 y 25), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando por debajo de 35, máximo en 25, valor a partir se considera un riesgo para la salud según la OMS.

        - Tendencia (Trend)

        Observando los valores del eje Y practicamente  numéricamente se mantiene estable.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual , esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a  la diaria.""",

                                "mensual":"""        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 10 y 20), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo 20 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        }
    elif codigo == 'ANCCAMS01':
        comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en ANCCAMS01 a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 5 y 20 µg/m³, pero hay cimas que rebasan los 35 µg/m³ la cual se considera segun la OMS un riesgo para la salud,
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de exposición habital de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³).
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios
        donde la serie revela picos de contaminación más severas por ejemplo, finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",

        "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 35 µg/m³, mucho más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa.
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie, pero si una acentuación en ese segundo ciclo.

        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad.
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        "Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 5 y 25), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando por debajo de 35, máximo en 25, valor a partir se considera un riesgo para la salud según la OMS.

        - Tendencia (Trend)

        Observando los valores del eje Y practicamente  numéricamente se mantiene estable.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual , esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a  la diaria.""",

                                "mensual":"""        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 12.5 y 17.5), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        }
    elif codigo == 'IT0459A':
        comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en IT0459A a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 15 y 40 µg/m³, pero hay cimas que rebasan los 50 µg/m³ la cual se considera segun la OMS un riesgo para la salud,
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de exposición habital de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³).
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de
        contaminación más severas por ejemplo, finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",

        "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 50 µg/m³, mucho más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa.
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie, pero si una acentuación en ese segundo ciclo.

        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad.
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        "Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 15 y 50), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando por claramente por encima de los 35, máximo en ~50, valor a partir se considera un riesgo para la salud según la OMS.

        - Tendencia (Trend)

        Observando los valores del eje Y practicamente numéricamente se mantiene estable.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual , esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a  la diaria.""",

                                "mensual":"""        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con oscilaciones entre 10 y 35), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo igual a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        }
    elif codigo == 'ANCCAMS05':
        comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en ANCCAMS05 a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 5 y 20 µg/m³, pero hay cimas que rebasan los 35 µg/m³ la cual se considera segun la OMS un riesgo para la salud,
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de exposición habital de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³).
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de
        contaminación más severas por ejemplo, principio 2022 o  finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",

        "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 40 µg/m³, más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa. 
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad. 
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 5 y 25), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando por debajo de 35, máximo en 25, valor a partir se considera un riesgo para la salud según la OMS.

        - Tendencia (Trend)

        Observando los valores del eje Y numéricamente se mantiene estable.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual , esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a la diaria.""",

                                "mensual":"""        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con oscilaciones entre 7.5 y 17.5), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo igual a 17.5 siendo inferior a un valor peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        }
    elif codigo == 'ANCCAMS10':
        comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en ANCCAMS10 a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 5 y 25 µg/m³, pero hay cimas que rebasan los 40 µg/m³.
        Tales eventos son particularmente significativos puesto que superan ampliamente el umbral de 35 µg/m³, que se considera un riesgo para la salud, llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³).
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos meses donde la serie revela picos de 
        contaminación más severas por ejemplo, finales de 2021 y finales de 2022.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",
                            "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo 
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 40 µg/m³, mucho más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa. 
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad

        Un ciclo anual repetitivo se manifiesta en la estacionalidad, evidenciando oscilaciones aproximadas de ±1 µg/m³ en relación con la media. 
        Esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad. 
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente": """        Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con pequeñas oscilaciones entre 10 y 20), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, pero sigue habiendo grandes subidas.

        - Tendencia (Trend)

        Pese a observarse cambios en la gráfica, el valor numérico no cambia practicamente nada si se fija en los valores que toma el eje y demostrando la mejoría en la estabilidad.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual , se observan repuntes positivos coincidiendo con los meses fríos y descensos en los cálidos.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a  la diaria.""",

                                "mensual": """"        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 10 y 20), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo en 17.50 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres)

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        }
    elif codigo == 'ANCCAMS14':
        comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en ANCCAMS14 a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 7.5 y 20 µg/m³, pero hay cimas que rebasan los 35 µg/m³ la cual se considera segun la OMS un riesgo para la salud, 
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de exposición habital de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³). 
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de 
        contaminación más severas por ejemplo, finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",
                            "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo 
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 35 µg/m³, más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa. 
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad. 
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 10 y 25), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando por debajo de 35, máximo en 25, valor a partir se considera un riesgo para la salud según la OMS.

        - Tendencia (Trend)

        Observando los valores del eje Y numéricamente se mantiene estable.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual , esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a la diaria.""",

                                "mensual":"""        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 7.5 y 17.5), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo 17.5 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        }
    elif codigo == 'ANCCAMS08':
      comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en ANCCAMS08 a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 7.5 y 20 µg/m³, pero hay cimas que rebasan los 35 µg/m³ la cual se considera segun la OMS un riesgo para la salud, 
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de exposición habital de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³). 
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de 
        contaminación más severas por ejemplo, finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",
                            "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo 
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 35 µg/m³, más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa. 
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad. 
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 7.5 y 25), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando por debajo de 35, máximo en 25, valor a partir se considera un riesgo para la salud según la OMS.

        - Tendencia (Trend)

        Observando los valores del eje Y numéricamente se mantiene estable, la mayor diferencia es de 1 teniendo en cuenta los valores de la serie es mínimo.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual , esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a la diaria.""",

                                "mensual":"""        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 7.5 y 17.5), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo 17.5 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        }
    elif codigo == 'ANCCAMS09':
        comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en ANCCAMS09 a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 7.5 y 20 µg/m³, pero hay cimas que rebasan los 35 µg/m³ la cual se considera segun la OMS un riesgo para la salud, 
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de exposición habital de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³). 
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de 
        contaminación más severas por ejemplo, finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",
                            "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo 
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 35 µg/m³, más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa. 
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad. 
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 5 y 25), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando por debajo de 35, máximo en 25, valor a partir se considera un riesgo para la salud según la OMS.

        - Tendencia (Trend)

        Observando los valores del eje Y numéricamente se mantiene estable, la mayor diferencia es de 1 teniendo en cuenta los valores de la serie es mínimo.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual, esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a la diaria.""",

                                "mensual":"""        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 7.5 y 17.5), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo 17.5 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        }
    elif codigo == 'ANCCAMS07':
        comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en ANCCAMS07 a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 7.5 y 20 µg/m³, pero hay cimas que rebasan los 35 µg/m³ la cual se considera segun la OMS un riesgo para la salud, 
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de exposición habital de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³). 
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de 
        contaminación más severas por ejemplo, finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",
                            "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo 
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 35 µg/m³, más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa. 
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad. Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 5 y 25), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando por debajo de 35, máximo en 25, valor a partir se considera un riesgo para la salud según la OMS.

        - Tendencia (Trend)

        Observando los valores del eje Y numéricamente se mantiene estable, la mayor diferencia es de 1 teniendo en cuenta los valores de la serie es mínimo.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual, esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a la diaria.""",

                                "mensual":"""        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 7.5 y 17.5), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo 17.5 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        }         
    elif codigo == 'ANCCAMS03':
        comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en ANCCAMS03 a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 7.5 y 30 µg/m³, pero hay cimas que rebasan los 35 µg/m³ la cual se considera segun la OMS un riesgo para la salud, 
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de exposición habital de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³). 
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de 
        contaminación más severas por ejemplo, finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",
                            "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo 
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 35 µg/m³, más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa. 
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad. 
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 5 y 25), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando por debajo de 35, máximo en 25, valor a partir se considera un riesgo para la salud según la OMS.

        - Tendencia (Trend)

        Observando los valores del eje Y numéricamente se mantiene estable, la mayor diferencia es inferor a 1 teniendo en cuenta los valores de la serie es mínimo.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual, esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a la diaria.""",

                                "mensual":"""        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 7.5 y 17.5), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo 17.5 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        }   
    elif codigo == 'ANCCAMS06':
        comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en ANCCAMS06 a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 7.5 y 30 µg/m³, pero hay cimas que rebasan los 35 µg/m³ la cual se considera segun la OMS un riesgo para la salud, 
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de exposición habital de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³). 
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de 
        contaminación más severas por ejemplo, finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",
                            "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo 
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 35 µg/m³, más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa. 
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad. 
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 7.5 y 25), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando por debajo de 35, máximo en 25, valor a partir se considera un riesgo para la salud según la OMS.

        - Tendencia (Trend)

        Observando los valores del eje Y numéricamente se mantiene estable, la mayor diferencia es poco más de 1 teniendo en cuenta los valores de la serie es mínimo.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual, esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a la diaria.""",

                                "mensual":"""        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 7.5 y 17.5), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo 17.5 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        } 
    elif codigo == 'ANCCAMS12':
        comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en ANCCAMS12 a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 7.5 y 30 µg/m³, pero hay cimas que rebasan los 35 µg/m³ la cual se considera segun la OMS un riesgo para la salud, 
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de exposición habital de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³). 
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de 
        contaminación más severas por ejemplo, finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",
                            "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo 
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 35 µg/m³, más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa. 
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad. 
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 10 y 25), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando por debajo de 35, máximo en 25, valor a partir se considera un riesgo para la salud según la OMS.

        - Tendencia (Trend)

        Observando los valores del eje Y numéricamente se mantiene estable, la mayor diferencia es poco más de 1 teniendo en cuenta los valores de la serie es mínimo.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual, esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a la diaria.""",

                                "mensual":"""        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 7.5 y 17.5), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo 17.5 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        } 
    elif codigo == 'ANCCAMS13':
        comentario = {"serie":"""        La serie temporal indica los niveles de las partículas en suspensión detectadas en ANCCAMS13 a lo largo de dos años.

        En cuanto a sus valores absolutos, se aprecia cómo estos fluctúan usualmente entre 5 y 30 µg/m³, pero hay cimas que rebasan los 35 µg/m³ la cual se considera segun la OMS un riesgo para la salud, 
        llegando a valores asociados con graves efectos en poblaciones vulnerables.

        Al cotejar con las pautas internacionales, una porción significativa de los datos excede el límite de exposición habital de la OMS (10 µg/m³ en promedio anual) y de la normativa europea (25 µg/m³). 
        Lo anterior señala que la población expuesta en el área permanece regularmente en niveles de riesgo, de moderado a elevado, particularmente en aquellos episodios donde la serie revela picos de 
        contaminación más severas por ejemplo, finales de 2022 y principios de 2023.

        Como conclusión, los niveles de PM2.5 no sólo exhiben una alta variabilidad diaria, sino que también en reiteradas ocasiones las concentraciones implican un riesgo considerable para la salud pública.""",
                            "descomposicion":"""        Interpretación de la descomposición de PM2. 5

        La serie se descompuso empleando un modelo aditivo, contemplando la periodicidad anual (365 horas aproximadamente 2 semanas); esta metodología se ajusta a las series ambientales porque la polución por partículas a menudo 
        depende de patrones climáticos estacionales (como invierno/verano, calefacción y las condiciones del tiempo).

        - Serie observada (Observed)

        La serie original exhibe notable variación diaria, con picos que sobrepasan los 35 µg/m³, más allá de los parámetros recomendados. La OMS propone una media anual de 10 µg/m³ frente a los 25 µg/m³ de europa. 
        Esos datos indican que, en varios periodos, la calidad del aire tuvo niveles dañinos para la salud pública.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad

        Se observa un claro patrón, esto sugiere que existe un ciclo climático anual que influye en los niveles de partículas.

        - Residuos

        Los residuos muestran una variabilidad considerable, con grandes picos, indicando episodios de polución singulares que no dependen únicamente de la tendencia o la estacionalidad. 
        Probablemente debido a fenómenos meteorológicos atípicos (incendios, irrupciones de polvo del Sahara...)""",

                            "semanalmente":"""        Después de cambiar de un muestreo diario a uno semanal, la serie se vuelve más suave (con oscilaciones entre 10 y 25), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 52 que captura ciclos anuales débiles.

        - Serie observada (Mood_Score)

        La serie es relativamente más estable, con baja volatilidad en comparación con la diaria, estando por debajo de 35, máximo en 25, valor a partir se considera un riesgo para la salud según la OMS.

        - Tendencia (Trend)

        Observando los valores del eje Y numéricamente se mantiene estable, la mayor diferencia inferior a 1 teniendo en cuenta los valores de la serie es mínimo.

        - Estacionalidad (Seasonal)

        Se aprecia claramente el patrón anual, esta observación señala la presencia de un patrón climático anual que afecta las concentraciones de partículas; siendo, veranos mas limpios contrastando con inviernos más cargados.

        - Residuos (Residual/Irregular)

        Ruido mínimo (~0, con pocos valores atípicos)lo que indica una gran reducción respecto a la diaria.""",

                                "mensual":"""        Después de cambiar de un muestreo diario a uno mensual, la serie se vuelve más suave (con pequeñas oscilaciones entre 7.5 y 17.5), lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo 17.5 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""
        } 
    else:
        print("El código de su instalación no está registrado")

    comentario["diario"] = """Después de cambiar de un muestreo horario a uno diario, la serie se vuelve más suave, lo que ayuda a reducir el ruido. La descomposición aditiva con un periodo de 4 que captura ciclos trimestrales.

        - Serie observada (Mood_Score)

        La serie recoge valores significativamente menores siendo su máximo 17.5 inferior a lo reconocido como peligroso por la OMS.

        - Tendencia (Trend)

        No se aprecia ninguna tendencia predominante sino más bien se observa una combinación de subidas y bajadas probablemente asociado a la estacionalidad de la serie.

        - Estacionalidad (Seasonal)

        Se aprecia un claro patrón apoyando la idea de la estacionalidad por esaciones (trimestres).

        - Residuos (Residual/Irregular)

        Se obserban residuos pequeños de forma aleatoria reforzando la selección del modelo."""

    return comentario