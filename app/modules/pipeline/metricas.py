from .matriz_main_builder import construccion_matriz_b
from .data_loader import quality_code_metris_api
import asyncio
import math
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from app.core.logger import crear_logger

logger = crear_logger("Pipeline")

def metrics_save(df_metricas):#Aux para guardar las metricas de la matriz main ([B])
    logger.info("====Medidas estadisticas de la matriz [B] guardadas=====")
    # Archivo actual
    ruta_actual = Path(__file__).resolve()
    ruta_csv = (
        ruta_actual.parent.parent.parent
        / "data"
        / "metricas_matriz_b.csv"
    )
    # =========================
    # Archivo en caso que no exista
    # =========================
    if not ruta_csv.exists():
        ruta_csv.parent.mkdir(parents=True, exist_ok=True)
        df_metricas.to_csv(
            ruta_csv,
            index=False
        )
        logger.info("CSV creado correctamente")
        return

    # =========================
    # Revisar fecha modificación si existe
    # =========================
    fecha_modificacion = datetime.fromtimestamp(
        ruta_csv.stat().st_mtime
    )
    fecha_actual = datetime.now()
    diferencia = fecha_actual - fecha_modificacion
    logger.info(f"Fecha de la creacion del archivo csv: {fecha_modificacion}, fecha actual: {fecha_actual}, la diferencia entre fechas: {diferencia}")
    # =========================
    # Sobrescribir si pasó 1 mes
    # =========================
    if diferencia >= timedelta(days=30):#Aca verifico el tiempo cada 1 mes
        df_metricas.to_csv(
            ruta_csv,
            index=False
        )
        logger.info("CSV actualizado después de 1 mes")
    else:
        logger.info("No ha pasado 1 mes, no se actualiza CSV")
    return
def redondeo_arriba_abs(x):#Aux para redondear el z-score
    return math.ceil(x * 100) / 100
def calcular_z_score(valor, media, desviacion_estandar): #Aux para calcular z-score
    if desviacion_estandar == 0:
        return 0  # Evitar división por cero, si la desviación estándar es cero, el z-score es 0
    z_score = redondeo_arriba_abs((valor - media) / desviacion_estandar)
    if abs(z_score) >= 3:
        pass
        # activar alerta
    return z_score
async def integracion_quality_code(id):
    data = await quality_code_metris_api(id)

    if not data:
        return None
    return {
        "identificador": id,
        "Quality_code": data[0]["quality"],
    }
async def metricas_de_matrices(df_datos_matriz):#Matriz general para calcular las metricas de cualquier matriz de datos
    #=================================Acscendente=========================================
    cols = df_datos_matriz.columns.drop("Identificador")
    cols_sorted = sorted(cols)  # ascendente
    df_datos_matriz = df_datos_matriz[["Identificador"] + cols_sorted]
    #=====================================================================================
    df_medidas_estadisticas = pd.DataFrame({
        "Identificador": pd.Series(dtype="Int64"),  # entero
        "Media": pd.Series(dtype="float"),
        "Desviacion_Estandar": pd.Series(dtype="float"),
    })

    #Trabajo n°1 añadir identificadores a cada fila de la matriz de metricas
    df_medidas_estadisticas["Identificador"] = df_datos_matriz["Identificador"]
    df_medidas_estadisticas=df_medidas_estadisticas.fillna(0)
    
    #Trabajo n°2 calcular medidas estadisticas para cada instrumento
    valores = df_datos_matriz.drop(columns=["Identificador"])
    #================= Quality Code =============================================
    # =========================
    # Obtención concurrente
    # =========================
    identificadores = df_medidas_estadisticas["Identificador"].to_list()
    tasks = [#Esto crea ordenes de hacer algo, pero no lo hace aún
            integracion_quality_code(id)
            for id in identificadores
        ]
    resultados = await asyncio.gather(*tasks, return_exceptions=True)#Esto es el trabajo todo junto y concurrente
    registros = []
    for resultado in resultados:
        if isinstance(resultado, Exception):
            print(resultado)
            continue
        if resultado is None:
            continue
        registros.append({
            "Identificador": resultado["identificador"],
            "Quality_code": resultado["Quality_code"]
        })
    if registros:
        df_quality = pd.DataFrame(registros)

        df_medidas_estadisticas = df_medidas_estadisticas.merge(
            df_quality,
            on="Identificador",
            how="left"
        )
    else:
        df_medidas_estadisticas["Quality_Code"] = None
    #============ Media y Desviación Estándar====================================
    df_medidas_estadisticas["Media"] = valores.mean(axis=1).round(3)
    df_medidas_estadisticas["Desviacion_Estandar"] = valores.std(axis=1).round(3)

    #============ Gradiente ====================================================
    valores_sorted = valores[cols_sorted]  # Datos ordenados, sin la columna identificador
    gradiente = valores_sorted.diff(axis=1)
    gradiente = gradiente.fillna(0)

    df_gradiente = pd.DataFrame({
        "Identificador": df_datos_matriz["Identificador"],
        "Gradiente_Promedio": gradiente.mean(axis=1).round(3),
        "Gradiente_Max": gradiente.abs().max(axis=1).round(3),
        "Gradiente_Intensidad": gradiente.abs().mean(axis=1).round(3),
    })
    df_medidas_estadisticas = df_medidas_estadisticas.merge(
        df_gradiente,
        on="Identificador",
        how="left"
    )

    """     for identificador in df_datos_matriz["Identificador"]: #Calculo del z_score para el ultimo valor de cada instrumento
        desviacion_estandar = df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"]== identificador, "Desviacion_Estandar"].values[0]
        if abs(desviacion_estandar) < 1e-10:
            desviacion_estandar = 0
        media = round(df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"]==identificador, "Media"].values[0],3)
        #fila_medidas = df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"]==identificador]
        ultimo_valor = df_datos_matriz.loc[df_datos_matriz["Identificador"]==identificador].iloc[:, -1].values[0]
        z_score = calcular_z_score(ultimo_valor, media, desviacion_estandar) #Posible envio de alerta
     """
    return df_medidas_estadisticas
async def metricas_matriz_b():
    df_datos_matriz_b = await construccion_matriz_b() #Datos historicos matriz B
    df_medidas_estadisticas = await metricas_de_matrices(df_datos_matriz_b) #Medidas estadisticas
    metrics_save(df_medidas_estadisticas)#Almacenar medidas estadisticas
    return df_datos_matriz_b, df_medidas_estadisticas
