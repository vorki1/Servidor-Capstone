from .matriz_a import (
    datos_matriz_a,
    ids_booleanos,
    INSTRUMENTOS_CONTROL_OPERACIONAL
)
import pandas as pd


AREAS_SERVICIOS_GENERALES = ["3100"]
AREAS_SECA = ["3200"]
AREAS_HUMEDA = ["3300", "3400", "3500", "3600", "3610"]
AREAS_RELAVES = ["3700", "3800"]
AREAS_CONCENTRADUCTO = ["4100"]

CONTROLES_EXTERNOS_RELAVES = [
    9543,
    9544,
    9282,
    9283,
]

def eliminar_booleanos(df):
    ids_a_eliminar = ids_booleanos()

    return df[
        ~df["Identificador"].isin(ids_a_eliminar)
    ].copy()


def eliminar_instrumentos_control_operacional(df):
    return df[
        ~df["Identificador"].isin(
            INSTRUMENTOS_CONTROL_OPERACIONAL
        )
    ].copy()


def normalizar_area_subarea(df):
    df = df.copy()

    df["Area"] = df["Area"].astype(str).str.strip()
    df["Subarea"] = df["Subarea"].astype(str).str.strip()

    return df


def filtrar_por_subarea(subarea: str, area: str = "3200"):
    df_general_a = datos_matriz_a()
    df_general_a = normalizar_area_subarea(df_general_a)

    return df_general_a[
        (df_general_a["Area"] == str(area))
        & (df_general_a["Subarea"] == subarea)
    ].copy()


def filtrar_por_areas(areas):
    df_general_a = datos_matriz_a()
    df_general_a = normalizar_area_subarea(df_general_a)

    areas = [str(area).strip() for area in areas]

    return df_general_a[
        df_general_a["Area"].isin(areas)
    ].copy()


def subarea_chancado_primario():
    return filtrar_por_subarea("Chancado Primario", "3200")


def subarea_chancado_secundario():
    return filtrar_por_subarea("Chancado Secundario", "3200")


def subarea_chancado_terciario():
    return filtrar_por_subarea("Chancado Terciario", "3200")


def subarea_chancado_cuaternario():
    return filtrar_por_subarea("Chancado Cuaternario", "3200")


def subarea_acopio_fino():
    return filtrar_por_subarea("Acopio Fino", "3200")


def grupo_area_humeda():
    return filtrar_por_areas(AREAS_HUMEDA)

def agregar_controles_externos(df, controles, area, subarea, sistema="CONTROL_OPERACIONAL"):
    df_controles = pd.DataFrame({
        "Identificador": controles,
        "Nombre_TAG": "CONTROL_EXTERNO",
        "Descripcion": "CONTROL OPERACIONAL EXTERNO",
        "TAG_OPC": "CONTROL_EXTERNO",
        "Area": str(area),
        "Subarea": subarea,
        "Sistema": sistema,
        "Unidad_de_Ingenieria": "BOOL",
        "Criticidad": "CONTROL"
    })

    return pd.concat(
        [df, df_controles],
        ignore_index=True
    ).drop_duplicates(
        subset=["Identificador"]
    )
def grupo_relaves():
    df = filtrar_por_areas(AREAS_RELAVES)

    return agregar_controles_externos(
        df=df,
        controles=CONTROLES_EXTERNOS_RELAVES,
        area="3700",
        subarea="Relaves"
    )


def grupo_servicios_generales():
    return filtrar_por_areas(AREAS_SERVICIOS_GENERALES)


def grupo_concentraducto():
    return filtrar_por_areas(AREAS_CONCENTRADUCTO)