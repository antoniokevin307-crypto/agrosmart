from django.shortcuts import render
from .forms_moon import MoonCalendarForm
import requests
from datetime import datetime
import os

# Usar WeatherAPI para fase lunar
# La API key ya está en .env como WEATHER_API_KEY

def get_moon_phase(date):
    api_key = os.getenv("WEATHER_API_KEY", "")
    city = os.getenv("DEFAULT_CITY", "San Miguel")
    url = f"https://api.weatherapi.com/v1/astronomy.json?key={api_key}&q={city}&dt={date}"
    phase_map = {
        'New Moon': 'Luna nueva',
        'Waxing Crescent': 'Creciente iluminante',
        'First Quarter': 'Cuarto creciente',
        'Waxing Gibbous': 'Gibosa creciente',
        'Full Moon': 'Luna llena',
        'Waning Gibbous': 'Gibosa menguante',
        'Last Quarter': 'Cuarto menguante',
        'Waning Crescent': 'Menguante iluminante'
    }
    try:
        resp = requests.get(url)
        data = resp.json()
        phase_en = data['astronomy']['astro']['moon_phase']
        return phase_map.get(phase_en, 'Desconocida')
    except Exception:
        return "Desconocida"


def moon_calendar(request):
    moon_phase_es = None
    moon_icon = None
    moon_phase_slug = None
    if request.method == "POST":
        form = MoonCalendarForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data["date"].strftime("%Y-%m-%d")
            phase_map = {
                'New Moon': {'es': 'Luna nueva', 'icon': '🌑', 'slug': 'luna-nueva'},
                'Waxing Crescent': {'es': 'Creciente iluminante', 'icon': '🌒', 'slug': 'creciente-iluminante'},
                'First Quarter': {'es': 'Cuarto creciente', 'icon': '🌓', 'slug': 'cuarto-creciente'},
                'Waxing Gibbous': {'es': 'Gibosa creciente', 'icon': '🌔', 'slug': 'gibosa-creciente'},
                'Full Moon': {'es': 'Luna llena', 'icon': '🌕', 'slug': 'luna-llena'},
                'Waning Gibbous': {'es': 'Gibosa menguante', 'icon': '🌖', 'slug': 'gibosa-menguante'},
                'Last Quarter': {'es': 'Cuarto menguante', 'icon': '🌗', 'slug': 'cuarto-menguante'},
                'Waning Crescent': {'es': 'Menguante iluminante', 'icon': '🌘', 'slug': 'menguante-iluminante'}
            }
            api_key = os.getenv("WEATHER_API_KEY", "")
            city = os.getenv("DEFAULT_CITY", "San Miguel")
            url = f"https://api.weatherapi.com/v1/astronomy.json?key={api_key}&q={city}&dt={date}"
            try:
                resp = requests.get(url)
                data = resp.json()
                phase_en = data['astronomy']['astro']['moon_phase']
                phase_info = phase_map.get(phase_en)
                if phase_info:
                    moon_phase_es = phase_info['es']
                    moon_icon = phase_info['icon']
                    moon_phase_slug = phase_info['slug']
                else:
                    moon_phase_es = 'Desconocida'
                    moon_icon = '🌙'
                    moon_phase_slug = 'desconocida'
            except Exception:
                moon_phase_es = 'Desconocida'
                moon_icon = '🌙'
                moon_phase_slug = 'desconocida'
    else:
        form = MoonCalendarForm()
    return render(request, "moon_calendar.html", {
        "form": form,
        "moon_phase_es": moon_phase_es,
        "moon_icon": moon_icon,
        "moon_phase_slug": moon_phase_slug
    })
