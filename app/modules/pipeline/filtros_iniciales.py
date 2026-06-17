from .matriz_a import (
    datos_matriz_a,
    ids_booleanos,
    INSTRUMENTOS_CONTROL_OPERACIONAL
)


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


def filtrar_por_subarea(subarea: str):
    df_general_a = datos_matriz_a()

    return df_general_a[
        df_general_a["Subarea"] == subarea
    ].copy()


def subarea_chancado_primario():
    return filtrar_por_subarea("Chancado Primario")


def subarea_chancado_secundario():
    return filtrar_por_subarea("Chancado Secundario")


def subarea_chancado_terciario():
    return filtrar_por_subarea("Chancado Terciario")


def subarea_chancado_cuaternario():
    return filtrar_por_subarea("Chancado Cuaternario")


def subarea_acopio_fino():
    return filtrar_por_subarea("Acopio Fino")