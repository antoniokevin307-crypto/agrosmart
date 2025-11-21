from datetime import datetime
import requests

def get_moon_phase(date):
    dt = datetime.strptime(date, "%Y-%m-%d")
    timestamp = int(dt.timestamp())
    url = f"https://api.farmsense.net/v1/moonphases/?d={timestamp}"
    try:
        resp = requests.get(url)
        data = resp.json()
        print(data)  # Debug: print the API response
        if data and isinstance(data, list):
            return data[0].get("PhaseName") or data[0].get("phase") or data[0].get("Phase") or "Desconocida"
        return "Desconocida"
    except Exception:
        return "Desconocida"

if __name__ == "__main__":
    print(get_moon_phase("2025-11-21"))
