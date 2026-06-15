# instrumento_debug.py

from datetime import datetime, timedelta, timezone

import requests
import urllib3

from app.core.config import settings

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)


def historico_instrumento_metris_api(
    instrumento_id=8942,
    horas=1
):
    headers = {
        "Authorization": f"Bearer {settings.METRIS_TOKEN}"
    }

    url = (
        f"{settings.METRIS_BASE_URI}"
        "/api/public/Historian/trendvalues"
    )

    fecha_fin = datetime.now(timezone.utc)
    fecha_inicio = fecha_fin - timedelta(hours=horas)

    params = {
        "ID": instrumento_id,
        "TagID": instrumento_id,
        "get_tag_values": instrumento_id,
        "Start": fecha_inicio.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "End": fecha_fin.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "InterpolationMethod": 1,
        "AggregateFunction": 0,
        "InterpolationResolutionType": 1,
        "interpolationresolution": 600000000
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        verify=False
    )

    response.raise_for_status()

    return response.json()