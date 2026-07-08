import asyncio
import json
from datetime import timedelta
from app.infrastructure.aws.aws_publisher import enviar_json_a_aws, enviar_lista_json_por_tamano
import pandas as pd

from .historian_debug import historico_instrumento_metris_api

from ..pipeline.data_loader import (
    datos_historicos_por_instrumento,
    tiempo_actual
)
from ..pipeline.matriz_a import datos_matriz_a


def historico_instrumento():
    data = historico_instrumento_metris_api()

    df = pd.DataFrame(data)

    return df.to_dict(orient="records")

def instrumentos_matriz_a():
    df = datos_matriz_a()

    columnas_jerarquia = [
        "Area",
        "Subarea",
        "Sistema"
    ]

    df = df.dropna(
        subset=columnas_jerarquia
    )

    for columna in columnas_jerarquia:
        df[columna] = (
            df[columna]
            .astype(str)
            .str.strip()
        )

    df = df[
        (df["Area"] != "")
        & (df["Subarea"] != "")
        & (df["Sistema"] != "")
        & (df["Area"].str.upper() != "VACIO")
        & (df["Subarea"].str.upper() != "VACIO")
        & (df["Sistema"].str.upper() != "VACIO")
        & (df["Area"].str.upper() != "S/D")
        & (df["Subarea"].str.upper() != "S/D")
        & (df["Sistema"].str.upper() != "S/D")
    ]

    instrumentos = df.to_dict(
        orient="records"
    )

    enviado = enviar_lista_json_por_tamano(
        nombre_base="instrumentos",
        clave_lista="instrumentos",
        lista=instrumentos
    )

    return {
        "total_instrumentos": len(instrumentos),
        "enviado_aws": enviado,
        "instrumentos": instrumentos
    }
async def areas_unicas():
    df_response = datos_matriz_a()

    areas = (
        df_response["Area"]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda x: x.str.upper() != "VACIO"]
        .loc[lambda x: x.str.upper() != "S/D"]
        .loc[lambda x: x.str.isnumeric()]
        .astype(int)
        .unique()
        .tolist()
    )

    return {
        "areas": sorted(areas)
    }


async def subareas_de_area(area):
    df_response = datos_matriz_a()

    df_response["Area"] = (
        df_response["Area"]
        .astype(str)
        .str.strip()
    )

    df_response["Subarea"] = (
        df_response["Subarea"]
        .astype(str)
        .str.strip()
    )

    area = str(area).strip()

    df_filtrado = df_response[
        df_response["Area"] == area
    ]

    subareas = (
        df_filtrado["Subarea"]
        .dropna()
        .loc[lambda x: x.str.upper() != "VACIO"]
        .loc[lambda x: x.str.upper() != "S/D"]
        .loc[lambda x: x != ""]
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    return {
        "area": area,
        "subareas": subareas
    }


async def sistemas_por_subarea(subarea):
    df = datos_matriz_a()

    df["Subarea"] = df["Subarea"].astype(str).str.strip()
    df["Sistema"] = df["Sistema"].astype(str).str.strip()

    subarea = str(subarea).strip()

    sistemas = (
        df[df["Subarea"] == subarea]["Sistema"]
        .dropna()
        .loc[lambda x: x.str.upper() != "VACIO"]
        .loc[lambda x: x.str.upper() != "S/D"]
        .loc[lambda x: x != ""]
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    return sistemas


async def instrumentos_por_sistema(sistema):
    df = datos_matriz_a()

    instrumentos = df[
        df["Sistema"] == sistema
    ]

    return instrumentos.to_dict(orient="records")


async def informacion_instrumento(id):
    df_response = datos_matriz_a()

    datos_instrumento = df_response[
        df_response["Identificador"] == id
    ]

    return {
        "informacion_general": datos_instrumento.to_dict(
            orient="records"
        )
    }


async def datos_historicos_por_id(id, minutos):
    if minutos <= 0:
        return {
            "error": "El número de minutos debe ser mayor que cero."
        }

    if minutos > 720:
        return {
            "error": "Intervalo de minutos no válido."
        }

    fecha_fin = tiempo_actual()
    fecha_inicio = fecha_fin - timedelta(minutes=minutos)

    if minutos < 60:
        minutos_muestreo = 0
        segundos_muestreo = 30
    else:
        minutos_muestreo = 1
        segundos_muestreo = 0

    data = await asyncio.to_thread(
        datos_historicos_por_instrumento,
        id,
        fecha_inicio,
        fecha_fin,
        minutos_muestreo,
        segundos_muestreo
    )

    return data

async def obtener_jerarquia_planta():
    df = datos_matriz_a()

    df = df[["Area", "Subarea", "Sistema"]].copy()

    df["Area"] = df["Area"].astype(str).str.strip()
    df["Subarea"] = df["Subarea"].astype(str).str.strip()
    df["Sistema"] = df["Sistema"].astype(str).str.strip()

    df = df[
        (df["Area"].str.upper() != "VACIO")
        & (df["Area"].str.upper() != "S/D")
        & (df["Area"].str.isnumeric())
        & (df["Subarea"].str.upper() != "VACIO")
        & (df["Subarea"].str.upper() != "S/D")
        & (df["Sistema"].str.upper() != "VACIO")
        & (df["Sistema"].str.upper() != "S/D")
    ]

    df["Area"] = df["Area"].astype(int)

    jerarquia = []

    for area, df_area in df.groupby("Area"):
        subareas = []

        for subarea, df_subarea in df_area.groupby("Subarea"):
            sistemas = (
                df_subarea["Sistema"]
                .dropna()
                .drop_duplicates()
                .sort_values()
                .tolist()
            )

            subareas.append({
                "subarea": subarea,
                "sistemas": sistemas
            })

        jerarquia.append({
            "area": int(area),
            "subareas": sorted(
                subareas,
                key=lambda item: item["subarea"]
            )
        })

    contenido = {
        "jerarquia": sorted(
            jerarquia,
            key=lambda item: item["area"]
        )
    }

    # ==============================
    # REPORTE JSON ANTES DE AWS
    # ==============================
    areas = [
        item["area"]
        for item in contenido["jerarquia"]
    ]

    print("\n========== REPORTE JERARQUIA A AWS ==========")
    print(f"Total áreas: {len(areas)}")
    print(f"Áreas: {areas}")
    print("Peso KB:")

    payload_prueba = {
        "nombre": "jerarquia1.json",
        **contenido
    }

    print(
        len(
            json.dumps(
                payload_prueba,
                ensure_ascii=False
            ).encode("utf-8")
        ) / 1024
    )

    print("JSON completo que se enviará:")
    print(
        json.dumps(
            payload_prueba,
            indent=4,
            ensure_ascii=False
        )
    )

    print("==============================================\n")

    enviar_json_a_aws(
        "jerarquia1.json",
        contenido
    )

    return contenido

def limpiar_texto_columna(serie):
    return (
        serie
        .fillna("")
        .astype(str)
        .str.strip()
    )


def es_valido(serie):
    return (
        (serie != "")
        & (serie.str.upper() != "VACIO")
        & (serie.str.upper() != "S/D")
        & (serie.str.upper() != "NAN")
    )


async def analisis_matriz_a():
    df = datos_matriz_a().copy()

    columnas = [
        "Area",
        "Subarea",
        "Sistema",
        "Unidad_de_Ingenieria"
    ]

    for columna in columnas:
        df[columna] = limpiar_texto_columna(df[columna])

    df_validos = df[
        es_valido(df["Area"])
        & es_valido(df["Subarea"])
        & es_valido(df["Sistema"])
    ].copy()

    resumen_general = {
        "total_registros_excel": int(len(df)),
        "total_instrumentos_validos": int(len(df_validos)),
        "areas": int(df_validos["Area"].nunique()),
        "subareas": int(df_validos["Subarea"].nunique()),
        "sistemas": int(df_validos["Sistema"].nunique()),
        "unidades_ingenieria": int(
            df_validos[
                es_valido(df_validos["Unidad_de_Ingenieria"])
            ]["Unidad_de_Ingenieria"].nunique()
        )
    }

    areas = (
        df_validos["Area"]
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    subareas_por_area = (
        df_validos
        .groupby("Area")["Subarea"]
        .unique()
        .apply(lambda x: sorted(x.tolist()))
        .to_dict()
    )

    sistemas_por_subarea = (
        df_validos
        .groupby(["Area", "Subarea"])["Sistema"]
        .unique()
        .reset_index()
    )

    sistemas_por_subarea = [
        {
            "area": row["Area"],
            "subarea": row["Subarea"],
            "sistemas": sorted(row["Sistema"].tolist())
        }
        for _, row in sistemas_por_subarea.iterrows()
    ]

    instrumentos_por_area = (
        df_validos
        .groupby("Area")
        .size()
        .reset_index(name="cantidad_instrumentos")
        .sort_values("Area")
        .to_dict(orient="records")
    )

    instrumentos_por_subarea = (
        df_validos
        .groupby(["Area", "Subarea"])
        .size()
        .reset_index(name="cantidad_instrumentos")
        .sort_values(["Area", "Subarea"])
        .to_dict(orient="records")
    )

    instrumentos_por_sistema = (
        df_validos
        .groupby(["Area", "Subarea", "Sistema"])
        .size()
        .reset_index(name="cantidad_instrumentos")
        .sort_values(["Area", "Subarea", "Sistema"])
        .to_dict(orient="records")
    )

    unidades_ingenieria = (
        df_validos[
            es_valido(df_validos["Unidad_de_Ingenieria"])
        ]
        .groupby("Unidad_de_Ingenieria")
        .size()
        .reset_index(name="cantidad_instrumentos")
        .sort_values("cantidad_instrumentos", ascending=False)
        .to_dict(orient="records")
    )

    registros_invalidos = {
        "area_invalida": int((~es_valido(df["Area"])).sum()),
        "subarea_invalida": int((~es_valido(df["Subarea"])).sum()),
        "sistema_invalido": int((~es_valido(df["Sistema"])).sum()),
        "unidad_ingenieria_invalida": int(
            (~es_valido(df["Unidad_de_Ingenieria"])).sum()
        )
    }

    contenido = {
        "resumen_general": resumen_general,
        "areas": areas,
        "subareas_por_area": subareas_por_area,
        "sistemas_por_subarea": sistemas_por_subarea,
        "instrumentos_por_area": instrumentos_por_area,
        "instrumentos_por_subarea": instrumentos_por_subarea,
        "instrumentos_por_sistema": instrumentos_por_sistema,
        "unidades_ingenieria": unidades_ingenieria,
        "registros_invalidos": registros_invalidos
    }

    enviar_json_a_aws(
        "analisis_matriz_a.json",
        contenido
    )

    return contenido