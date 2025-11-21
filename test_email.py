#!/usr/bin/env python
"""
Script para probar la configuración de email en Django.
Uso: python test_email.py
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrosmart.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 60)
print("PRUEBA DE CONFIGURACIÓN DE EMAIL")
print("=" * 60)

print(f"\n📧 EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"🔐 EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"🔒 EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"👤 EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"🔑 EMAIL_HOST_PASSWORD: {'***' if settings.EMAIL_HOST_PASSWORD else 'NO CONFIGURADA'}")
print(f"📤 DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
    print("\n❌ ERROR: EMAIL_HOST_USER o EMAIL_HOST_PASSWORD no están configurados.")
    print("   Configúralos en el archivo .env")
    sys.exit(1)

print("\n⏳ Intentando enviar email de prueba...")

try:
    send_mail(
        subject='AgroSmart - Prueba de Email',
        message='Si recibes este mensaje, la configuración de email está funcionando correctamente.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.EMAIL_HOST_USER],
        fail_silently=False,
    )
    print("✅ EMAIL ENVIADO EXITOSAMENTE")
    print(f"✉️  Se envió un email de prueba a: {settings.EMAIL_HOST_USER}")
except Exception as e:
    print(f"❌ ERROR AL ENVIAR EMAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("Ahora puedes usar el sistema de registro con OTP por email.")
print("=" * 60)
