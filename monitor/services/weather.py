import requests
from django.conf import settings

def fetch_current_weather(city: str | None = None, country_code: str | None = None, lat: float | None = None, lon: float | None = None) -> dict:
    """
    Consulta el clima actual a WeatherAPI.
    Se puede consultar por ciudad/país (city, country_code) o por coordenadas (lat, lon).
    Devuelve un dict normalizado con temperature (°C), humidity (%), rain_mm (última hora), wind_ms.
    Maneja errores de red y respuestas incompletas.
    """
    # Obtener la clave API desde las configuraciones
    api_key = settings.WEATHER_API_KEY
    if not api_key:
        # Si no se encuentra la clave API en las configuraciones, devolvemos un error controlado
        return {"ok": False, "error": "Falta WEATHER_API_KEY en .env"}

    # URL de la API de WeatherAPI
    url = "http://api.weatherapi.com/v1/current.json"

    # Construir parámetro 'q' según coordenadas o ciudad/país
    if lat is not None and lon is not None:
        q = f"{lat},{lon}"
    elif city:
        # country_code puede ser None o vacío
        q = f"{city},{country_code or ''}"
    else:
        # Fallback a valores por defecto en settings
        q = f"{settings.DEFAULT_CITY},{settings.DEFAULT_COUNTRY}"

    params = {
        "q": q,
        "key": api_key,
        "aqi": "no",
    }

    try:
        # Hacer la solicitud HTTP a WeatherAPI
        r = requests.get(url, params=params, timeout=8)

        # Verificar si la respuesta fue exitosa (código 2xx)
        r.raise_for_status()

        # Convertir la respuesta JSON a un diccionario de Python
        data = r.json()

        # Comprobamos si la respuesta contiene la clave 'current' (que es la que contiene la temperatura)
        if "current" not in data:
            return {"ok": False, "error": "Respuesta inesperada de la API. Falta la clave 'current'."}

        # Extraer los datos relevantes de la respuesta
        current = data.get("current", {})
        wind = current.get("wind_kph", 0.0)
        rain = current.get("precip_mm", 0.0)  # Precipitación en mm

        # Retornar los datos normalizados
        return {
            "ok": True,
            "temperature": current.get("temp_c", None),  # Temperatura en °C
            "humidity": current.get("humidity", None),  # Humedad relativa en %
            "rain_mm": rain,  # Lluvia en mm (última hora)
            "wind_ms": wind / 3.6,  # Convertir de km/h a m/s
            "raw": data,  # Respuesta completa de la API para depuración
        }

    except requests.RequestException as exc:
        # Manejo de errores de red o conexión
        return {"ok": False, "error": f"Error de red: {exc}"}
    
    except ValueError as exc:
        # Error al procesar los datos JSON de la respuesta
        return {"ok": False, "error": f"Error al procesar los datos de la API (JSON inválido): {exc}"}
    
    except Exception as exc:
        # Captura cualquier otro tipo de excepción inesperada
        return {"ok": False, "error": f"Error inesperado: {exc}"}
