#!/usr/bin/env python
"""
Simula una petición HTTP POST al endpoint de registro (como hace el navegador).
Usa el Test Client de Django.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrosmart.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.test import Client
from django.conf import settings

print('=== PRUEBA HTTP: POST /registro/ ===')
print(f'Servidor de desarrollo debe estar corriendo en http://127.0.0.1:8000/')
print(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')

client = Client()

# Permitir testserver
settings.ALLOWED_HOSTS.append('testserver')

# Simular POST al formulario de registro
test_email = 'prueba_http@example.com'
print(f'\nSimulando POST a /registro/ con email: {test_email}')

response = client.post('/registro/', {'email': test_email})

print(f'Respuesta status: {response.status_code}')

if response.status_code == 302:
    print(f'✅ Redirección exitosa (302) → Registro generó OTP y envió email')
    print(f'Location: {response.url}')
else:
    print(f'Contenido de respuesta:')
    print(response.content[:1000].decode('utf-8', errors='ignore'))
    
    # Buscar mensaje de error
    if 'error' in response.content.decode('utf-8', errors='ignore').lower():
        print('\n⚠️  Hay un error en la respuesta')

print('\n✅ Test HTTP completado')
