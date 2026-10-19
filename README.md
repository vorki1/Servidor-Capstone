# Servidor Backend | Capstone Project (FastAPI)

Servicio backend asíncrono de alto rendimiento desarrollado en **FastAPI (Python)**, diseñado para la ingesta de datos operacionales desde la plataforma **Metris**, procesamiento de reglas estadísticas en tiempo real, disparo automatizado de alertas y provisión de endpoints para el visualizador web de instrumentación industrial.

---

## 📌 Arquitectura y Alcance

El servidor actúa como el motor central de procesamiento del ecosistema Capstone, estructurando el ciclo completo del dato:

1. **Ingesta e Integración:** Conexión y extracción periódica de telemetría y datos operativos desde Metris.
2. **Motor de Reglas Estadísticas:** Procesamiento algorítmico sobre series temporales y métricas de instrumentos para identificar anomalías, desviaciones operativas y cambios de tendencia.
3. **Módulo de Alertamiento:** Detección de condiciones críticas fuera de umbral y generación de notificaciones automáticas para el equipo de mantenimiento.
4. **Capa de Servicio (APIs):** Endpoints RESTful optimizados y serializados para alimentar al visualizador frontend con baja latencia.

---

## 🛠️ Stack Tecnológico

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Servidor ASGI:** [Uvicorn](https://www.uvicorn.org/)
- **Validación y Modelado:** [Pydantic v2](https://docs.pydantic.dev/)
- **Procesamiento Numérico y Estadístico:** NumPy / Pandas
- **Bases de Datos & Caché:** PostgreSQL / Redis
- **Documentación Interactiva:** OpenAPI (Swagger UI) y ReDoc integrados nativamente

---

## ✨ Características Principales

- **Ejecución Asíncrona:** Arquitectura basada en `async/await` para soportar múltiples consultas concurrentes y llamadas a APIs externas sin bloquear el hilo principal.
- **Validación Estricta:** Serialización y validación de esquemas de entrada/salida mediante modelos Pydantic, garantizando consistencia de datos en toda la canalización.
- **Alertas Proactivas:** Lógica de monitoreo continuo que evalúa estados de instrumentos contra límites predefinidos.
- **Documentación Viva:** Generación automática de especificaciones Swagger accesibles en tiempo de ejecución.

---

