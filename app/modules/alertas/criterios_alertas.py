import numpy as np
# =========================Criterios de alertas=========================#
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
def tabla_alertas(df_matriz_b, df_matriz_c):#Tabla importante de alertas que se mandan al frontend
    # Unir por identificador
    df_merge = df_matriz_b.merge(
        df_matriz_c,
        on="Identificador",
        suffixes=("_b", "_c")
    )
    df_merge = detectar_cambio_brusco(df_merge)
    df_merge = detectar_oscilacion(df_merge)
    df_merge = detectar_sensor_congelado(df_merge)
    df_merge = df_merge.replace({np.nan: None})
    columnas_frontend = [
        "Identificador",
        "Alerta_Cambio_Brusco",
        "Alerta_Oscilacion",
        "Alerta_Senal_Congelada"
    ]

    df_merge = df_merge[columnas_frontend]
    return df_merge
