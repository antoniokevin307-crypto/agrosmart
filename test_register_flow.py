#!/usr/bin/env python
"""
Simula el flujo de registro: crea un código OTP y lo envía por email, como hace la vista.
"""
import os
import sys
import django
import random
import string
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrosmart.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from monitor.models import EmailVerification, CustomUser

print('=== SIMULANDO REGISTRO CON OTP ===')
print(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
print(f'EMAIL_HOST_PASSWORD configurado: {bool(settings.EMAIL_HOST_PASSWORD)}')

# Email de prueba
test_email = 'adustgeymer@gmail.com'  # Prueba con este correo
print(f'\nRegistrando: {test_email}')

# Generar código OTP
code = ''.join(random.choices(string.digits, k=6))
print(f'Código OTP generado: {code}')

# Eliminar verificaciones anteriores
EmailVerification.objects.filter(email=test_email).delete()

# Crear verificación
expires_at = timezone.now() + timedelta(minutes=15)
EmailVerification.objects.create(
    email=test_email,
    code=code,
    expires_at=expires_at
)
print(f'Registro de verificación guardado en BD')

# Enviar email (como hace la vista)
try:
    send_mail(
        subject='AgroSmart - Código de Verificación',
        message=f'Tu código de verificación es: {code}\n\nEste código expirará en 15 minutos.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[test_email],
        fail_silently=False,
    )
    print(f'✅ EMAIL ENVIADO A: {test_email}')
except Exception as e:
    print(f'❌ ERROR: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('\n✅ FLUJO COMPLETADO EXITOSAMENTE')
print(f'Deberías recibir el correo en: {test_email}')
