#!/usr/bin/env python
import os, sys, traceback
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrosmart.settings')
sys.path.insert(0, os.path.dirname(__file__))

import django
django.setup()

from django.conf import settings
from monitor.models import CustomUser, Crop, WeatherRecord
from monitor.services.weather import fetch_current_weather

print('Iniciando diagnóstico de guardado de WeatherRecord')

# Obtener o crear un usuario de prueba
email = 'test_local@example.com'
user, created = CustomUser.objects.get_or_create(email=email)
if created:
    user.set_password('testpass123')
    user.save()
    print(f'Usuario creado: {email}')
else:
    print(f'Usuario existente: {email}')

# Crear un cultivo con coordenadas (si ya existe, lo usamos)
crop, c_created = Crop.objects.get_or_create(user=user, name='Diagnostico Demo', defaults={
    'country_code': settings.DEFAULT_COUNTRY,
    'latitude': 13.4333,
    'longitude': -89.8333,
})
if not c_created:
    # Asegurar coordenadas presentes
    crop.latitude = crop.latitude or 13.4333
    crop.longitude = crop.longitude or -89.8333
    crop.save()

print(f'Usando cultivo id={crop.id}, lat={crop.latitude}, lon={crop.longitude}')

# Llamar al servicio de clima
weather = fetch_current_weather(lat=crop.latitude, lon=crop.longitude)
print('Resultado fetch_current_weather:', weather)

# Intentar crear el WeatherRecord y atrapar excepciones
try:
    wr = WeatherRecord.objects.create(
        crop=crop,
        temperature=weather.get('temperature'),
        humidity=weather.get('humidity'),
        rain_mm=weather.get('rain_mm'),
        wind_ms=weather.get('wind_ms'),
        recommendation='Diagnóstico automático'
    )
    print('WeatherRecord creado con id=', wr.id)
except Exception as e:
    print('ERROR al crear WeatherRecord:')
    traceback.print_exc()
    sys.exit(1)

print('Diagnóstico completado correctamente')
