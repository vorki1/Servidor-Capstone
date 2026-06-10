import numpy as np
from app.modules.alertas.alerta_service import procesar_alertas_dataframe
from app.modules.alertas.alerta_repository import obtener_activas
from ..pipeline.data_loader import datos_matriz_a
from app.db.database import SessionLocal
import pandas as pd
from app.core.logger import crear_logger

logger = crear_logger("Alertas")

# =========================Criterios de alertas=========================#
def detectar_todos_cero(df):
    df["Alerta_Todos_Cero"] = "NORMAL"

    condicion_todos_cero = (
        (df["Media_b"] == 0)
        &
        (df["Desviacion_Estandar_b"] == 0)
        &
        (df["Gradiente_Max_b"] == 0)
        &
        (df["Gradiente_Intensidad_b"] == 0)
        &
        (df["Media_c"] == 0)
        &
        (df["Desviacion_Estandar_c"] == 0)
        &
        (df["Gradiente_Max_c"] == 0)
        &
        (df["Gradiente_Intensidad_c"] == 0)
    )

    df.loc[
        condicion_todos_cero,
        "Alerta_Todos_Cero"
    ] = "CRITICO"

    return df
def detectar_media_congelada(df):
    df["Alerta_Media_Congelada"] = "NORMAL"

    tolerancia_media = 0.01

    condicion_media_congelada = (
        (df["Media_b"].notna())
        &
        (df["Media_c"].notna())
        &
        (df["Media_b"] != 0)
        &
        (df["Media_c"] != 0)
        &
        (df["Desviacion_Estandar_b"] == 0)
        &
        (df["Desviacion_Estandar_c"] == 0)
        &
        (df["Gradiente_Max_b"] == 0)
        &
        (df["Gradiente_Max_c"] == 0)
        &
        (df["Gradiente_Intensidad_b"] == 0)
        &
        (df["Gradiente_Intensidad_c"] == 0)
        &
        (
            abs(df["Media_b"] - df["Media_c"])
            <=
            tolerancia_media
        )
    )

    df.loc[
        condicion_media_congelada,
        "Alerta_Media_Congelada"
    ] = "CRITICO"

    return df
def detectar_cambio_brusco(df):#Aux
    # Evitar división por cero
    epsilon = 1e-6
    # =========================
    # Ratios
    # =========================
    df["Ratio_STD"] = (df["Desviacion_Estandar_c"]/(df["Desviacion_Estandar_b"] + epsilon)).round(3)
    #El promedio de variacion del instrumento
    df["Ratio_Gradiente"] = (df["Gradiente_Max_c"]/(df["Gradiente_Max_b"] + epsilon)).round(3)
    # =========================================================
    # Clasificación de severidad
    # =========================================================
    df["Alerta_Cambio_Brusco"] = "NORMAL"
    # -------------------------
    # Preventivo
    # -------------------------
    df.loc[((df["Ratio_STD"] >= 2)|(df["Ratio_Gradiente"] >= 2)),"Alerta_Cambio_Brusco"] = "PREVENTIVO"
    # -------------------------
    # Crítico
    # -------------------------
    df.loc[((df["Ratio_STD"] >= 5)|(df["Ratio_Gradiente"] >= 5)),"Alerta_Cambio_Brusco"] = "CRITICO"
    # -------------------------
    # Emergencia
    # -------------------------
    df.loc[((df["Ratio_STD"] >= 10)|(df["Ratio_Gradiente"] >= 10)),"Alerta_Cambio_Brusco"] = "EMERGENCIA"
    return df
def detectar_oscilacion(df):#Aux
    epsilon = 1e-6
    # =====================================================
    # Ratio de oscilación
    # =====================================================
    df["Ratio_Oscilacion"] = (
        df["Gradiente_Intensidad_c"]
        /
        (df["Gradiente_Intensidad_b"] + epsilon)
    ).round(3)
    # =====================================================
    # Clasificación
    # =====================================================
    df["Alerta_Oscilacion"] = "NORMAL"
    # Preventivo
    df.loc[
        df["Ratio_Oscilacion"] >= 2,
        "Alerta_Oscilacion"
    ] = "PREVENTIVO"
    # Crítico
    df.loc[
        df["Ratio_Oscilacion"] >= 5,
        "Alerta_Oscilacion"
    ] = "CRITICO"
    # Emergencia
    df.loc[
        df["Ratio_Oscilacion"] >= 10,
        "Alerta_Oscilacion"
    ] = "EMERGENCIA"
    return df
def detectar_sensor_congelado(df):#Aux

    df["Alerta_Senal_Congelada"] = "NORMAL"
    condicion_congelada = (
        (df["Desviacion_Estandar_b"] > 0.1) #No evalua sensores son ultra constantes, por lo tanto historicamente variaba
        &
        (df["Desviacion_Estandar_c"] <= 0.001)#std actual casi 0, lo que indica que la señal ahora está plana
        &
        (df["Gradiente_Intensidad_c"] <= 0.001)#gradiente actual casi 0, lo que indica que ahora no cambia entre muestras
    )
    df.loc[
        condicion_congelada,
        "Alerta_Senal_Congelada"
    ] = "CRITICO"
    return df

#==========================Recuperación de señal=======================#
def detectar_senal_recuperada(df):
    df["Alerta_Senal_Recuperada"] = "NORMAL"

    condicion_recuperada_desde_cero = (
        (df["Media_b"] == 0)
        &
        (df["Desviacion_Estandar_b"] == 0)
        &
        (df["Gradiente_Max_b"] == 0)
        &
        (df["Gradiente_Intensidad_b"] == 0)
        &
        (
            (df["Desviacion_Estandar_c"] > 0.001)
            |
            (df["Gradiente_Max_c"] > 0.001)
            |
            (df["Gradiente_Intensidad_c"] > 0.001)
        )
    )

    condicion_recuperada_desde_media = (
        (df["Media_b"].notna())
        &
        (df["Media_b"] != 0)
        &
        (df["Desviacion_Estandar_b"] == 0)
        &
        (df["Gradiente_Max_b"] == 0)
        &
        (df["Gradiente_Intensidad_b"] == 0)
        &
        (
            (df["Desviacion_Estandar_c"] > 0.001)
            |
            (df["Gradiente_Max_c"] > 0.001)
            |
            (df["Gradiente_Intensidad_c"] > 0.001)
        )
    )

    df.loc[
        condicion_recuperada_desde_cero | condicion_recuperada_desde_media,
        "Alerta_Senal_Recuperada"
    ] = "PREVENTIVO"

    return df

def tabla_alertas(df_matriz_b, df_matriz_c):
    df_merge = df_matriz_b.merge(
        df_matriz_c,
        on="Identificador",
        suffixes=("_b", "_c")
    )

    logger.info(f"Métricas B: {len(df_matriz_b)}")
    logger.info(f"Métricas C: {len(df_matriz_c)}")
    logger.info(f"Merge B-C: {len(df_merge)}")

    df_merge = detectar_cambio_brusco(df_merge)
    df_merge = detectar_oscilacion(df_merge)
    df_merge = detectar_sensor_congelado(df_merge)
    df_merge = detectar_todos_cero(df_merge)
    df_merge = detectar_media_congelada(df_merge)
    df_merge = detectar_senal_recuperada(df_merge)

    df_merge = df_merge.replace({np.nan: None})

    columnas_frontend = [
        "Identificador",
        "Alerta_Cambio_Brusco",
        "Alerta_Oscilacion",
        "Alerta_Senal_Congelada",
        "Alerta_Todos_Cero",
        "Alerta_Media_Congelada",
        "Alerta_Senal_Recuperada",
    ]

    return df_merge[columnas_frontend]

def datos_y_alertas_instrumentos(df_tabla_alertas):
    df_info_instrumentos = datos_matriz_a()

    columnas_info = [
        "Identificador",
        "Nombre_TAG",
        "Descripcion",
        "Unidad_de_Ingenieria",
        "Area",
        "Subarea",
        "Sistema",
    ]

    df_info_instrumentos = df_info_instrumentos[columnas_info]

    df_tabla_alertas_enriquecida = df_tabla_alertas.merge(
        df_info_instrumentos,
        on="Identificador",
        how="left"
    )

    columnas_alertas = [
        "Alerta_Cambio_Brusco",
        "Alerta_Oscilacion",
        "Alerta_Senal_Congelada",
        "Alerta_Todos_Cero",
        "Alerta_Media_Congelada",
        "Alerta_Senal_Recuperada",
    ]

    df_tabla_alertas_enriquecida[columnas_alertas] = (
        df_tabla_alertas_enriquecida[columnas_alertas]
        .astype(str)
        .apply(lambda col: col.str.strip().str.upper())
    )

    db = SessionLocal()

    try:
        # IMPORTANTE:
        # Se procesa TODO el dataframe, incluyendo NORMAL,
        # para poder cerrar alertas antiguas.
        procesar_alertas_dataframe(
            db,
            df_tabla_alertas_enriquecida
        )

        alertas_activas = obtener_activas(db)

        data_alertas = []

        for alerta in alertas_activas:
            data_alertas.append({
                "Identificador": alerta.identificador,
                "Tipo_Alerta_DB": alerta.tipo_alerta,
                "Nivel_Alerta_DB": alerta.nivel_alerta,
                "Fecha_Inicio_Alarma": alerta.fecha_inicio,
                "Fecha_Ultima_Actualizacion": alerta.fecha_ultima_actualizacion,
                "Fecha_Fin": alerta.fecha_fin,
                "Ciclos_Alarma": alerta.ciclos,
                "Alarma_Activa": alerta.activa,
            })

        df_alertas_db = pd.DataFrame(data_alertas)

        if not df_alertas_db.empty:
            df_tabla_alertas_enriquecida = df_info_instrumentos.merge(
                df_alertas_db,
                on="Identificador",
                how="inner"
            )
        else:
            df_tabla_alertas_enriquecida = pd.DataFrame()

    finally:
        db.close()

    if df_tabla_alertas_enriquecida.empty:
        return df_tabla_alertas_enriquecida

    df_tabla_alertas_enriquecida = df_tabla_alertas_enriquecida.drop(
        columns=[
            "Alerta_Cambio_Brusco",
            "Alerta_Oscilacion",
            "Alerta_Senal_Congelada",
            "Alerta_Todos_Cero",
            "Alerta_Media_Congelada",
            "Alerta_Senal_Recuperada",
        ],
        errors="ignore"
    )

    df_tabla_alertas_enriquecida = df_tabla_alertas_enriquecida.rename(
        columns={
            "Tipo_Alerta_DB": "Tipo_Alerta",
            "Nivel_Alerta_DB": "Nivel_Alerta",
        }
    )

    df_tabla_alertas_enriquecida = (
        df_tabla_alertas_enriquecida
        .replace({np.nan: None})
    )

    return df_tabla_alertas_enriquecida