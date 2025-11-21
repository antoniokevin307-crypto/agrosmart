#!/usr/bin/env python
"""
Script para probar envío de email directamente desde Django (como hace la vista de registro).
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrosmart.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.core.mail import send_mail
from django.conf import settings

print('=== PRUEBA DE ENVÍO DE EMAIL DESDE DJANGO ===')
print(f'EMAIL_HOST: {settings.EMAIL_HOST}')
print(f'EMAIL_PORT: {settings.EMAIL_PORT}')
print(f'EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
print(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
print(f'EMAIL_HOST_PASSWORD set: {bool(settings.EMAIL_HOST_PASSWORD)}')
print(f'EMAIL_HOST_PASSWORD length: {len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 0}')

print('\nIntentando enviar email de prueba...')

try:
    send_mail(
        subject='AgroSmart - Prueba de Email desde Django',
        message='Este es un email de prueba para verificar que el envío funciona correctamente.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=['antoniokevin307@gmail.com'],
        fail_silently=False,
    )
    print('✅ EMAIL ENVIADO EXITOSAMENTE')
except Exception as e:
    print(f'❌ ERROR: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
