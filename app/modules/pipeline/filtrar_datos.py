from app.core.logger import crear_logger
import pandas as pd

logger = crear_logger("Pipeline")

def filtrar_chancado_primario(df_historico):
    print("Soy el chancado primario")
    df_historico = df_historico[df_historico["Identificador"] != 89932]
    serie_runsignal_chancador_primario = df_historico[df_historico["Identificador"] == 8954]
    print("Serie runsignal chancador primario:\n",serie_runsignal_chancador_primario.iloc[:10])
    
    for _,fila in df_historico.iterrows():
        valores = fila.drop(labels=["Identificador"])
        # Convertir a numérico
        valores = pd.to_numeric(valores, errors="coerce")
        # Redondear floats
        valores = valores.round(1)
        
        valores_unicos = set(valores.unique())
        print(f"Valores únicos para el identificador: {list(valores_unicos)[:5]}")
        print("Total valores:", len(valores))
        print("No NaN:", valores.notna().sum())
        print("NaN:", valores.isna().sum())
    return df_historico

def filtrar_chancado_secundario(df_historico):
    print("Soy el chancado secundario")
    return df_historico

ACCIONES_SUBAREA = {
    "Chancado Primario": filtrar_chancado_primario,
    "Chancado Secundario": filtrar_chancado_secundario,
}
def filtrar_datos_historicos(df_datos_historicos, subarea):
    print(df_datos_historicos,"\n",subarea)

    funcion = ACCIONES_SUBAREA.get(subarea)
    if funcion:
        resultado = funcion(df_datos_historicos)
        return resultado
    else:
        logger.warning(f"No existe accion para subarea: {subarea}")
    logger.info("Filtramos la matriz A -----> Generando la matriz B")
    return df_datos_historicos