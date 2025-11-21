import os
import random
import string
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

from monitor.models import CustomUser, EmailVerification


def register_view(request):
    """
    Paso 1: Solicitar email del usuario.
    Genera un código OTP de 6 dígitos y lo envía por email.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        # Validar que el email no esté registrado
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'auth/register.html', {
                'error': 'Este email ya está registrado. Intenta iniciar sesión.',
                'email': email
            })
        
        if not email or '@' not in email:
            return render(request, 'auth/register.html', {
                'error': 'Por favor ingresa un email válido.'
            })
        
        # Generar código OTP de 6 dígitos
        code = ''.join(random.choices(string.digits, k=6))
        
        # Eliminar verificaciones anteriores para este email
        EmailVerification.objects.filter(email=email).delete()
        
        # Crear nuevo registro de verificación (válido por 15 minutos)
        expires_at = timezone.now() + timedelta(minutes=15)
        EmailVerification.objects.create(
            email=email,
            code=code,
            expires_at=expires_at
        )
        
        # Enviar email con el código
        try:
            send_mail(
                subject='AgroSmart - Código de Verificación',
                message=f'Tu código de verificación es: {code}\n\nEste código expirará en 15 minutos.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error al enviar email: {e}")
            import traceback
            traceback.print_exc()
            return render(request, 'auth/register.html', {
                'error': f'Error al enviar el email: {str(e)}. Verifica que EMAIL_HOST_USER y EMAIL_HOST_PASSWORD estén configurados correctamente en .env',
                'email': email
            })
        
        # Redirigir a página de verificación
        return redirect('verify_email', email=email)
    
    return render(request, 'auth/register.html')


def verify_email_view(request, email):
    """
    Paso 2: Verificar el código OTP.
    Si es correcto, redirige a crear contraseña.
    """
    verification = EmailVerification.objects.filter(email=email).first()
    
    if not verification:
        return redirect('register')
    
    if verification.is_expired():
        verification.delete()
        return render(request, 'auth/verify_code.html', {
            'error': 'El código ha expirado. Solicita uno nuevo.',
            'email': email,
            'show_request_new': True
        })
    
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        
        if not code or len(code) != 6:
            attempts_left = 5 - verification.attempts
            return render(request, 'auth/verify_code.html', {
                'error': f'Código inválido. Te quedan {attempts_left} intentos.',
                'email': email,
                'attempts_left': attempts_left
            })
        
        # Verificar que el código es correcto
        if code != verification.code:
            verification.attempts += 1
            
            if verification.attempts >= 5:
                verification.delete()
                return render(request, 'auth/verify_code.html', {
                    'error': 'Demasiados intentos fallidos. Solicita un nuevo código.',
                    'email': email,
                    'show_request_new': True
                })
            
            verification.save()
            attempts_left = 5 - verification.attempts
            return render(request, 'auth/verify_code.html', {
                'error': f'Código incorrecto. Te quedan {attempts_left} intentos.',
                'email': email,
                'attempts_left': attempts_left
            })
        
        # Código correcto, eliminar verificación y redirigir a crear password
        verification.delete()
        return redirect('create_password', email=email)
    
    attempts_left = 5 - verification.attempts
    return render(request, 'auth/verify_code.html', {
        'email': email,
        'attempts_left': attempts_left
    })


def create_password_view(request, email):
    """
    Paso 3: Usuario crea su contraseña.
    Crea la cuenta CustomUser y lo redirige a login.
    """
    if request.method == 'POST':
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        # Validaciones básicas
        if not password or len(password) < 6:
            return render(request, 'auth/create_password.html', {
                'error': 'La contraseña debe tener al menos 6 caracteres.',
                'email': email
            })
        
        if password != password_confirm:
            return render(request, 'auth/create_password.html', {
                'error': 'Las contraseñas no coinciden.',
                'email': email
            })
        
        # Crear usuario
        try:
            user = CustomUser.objects.get(email=email)
            user.set_password(password)
            user.is_verified = True
            user.save()
            return redirect('login')
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.create_user(
                    email=email,
                    password=password,
                    username=email.split('@')[0],
                    is_verified=True
                )
                return redirect('login')
            except Exception as e:
                return render(request, 'auth/create_password.html', {
                    'error': f'Error al crear la cuenta: {str(e)}',
                    'email': email
                })
    
    return render(request, 'auth/create_password.html', {'email': email})


def login_view(request):
    """
    Login con email y contraseña.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        # Autenticar
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            # Si el usuario es root, puede ir a crop_list, pero los normales siempre a dashboard
            if hasattr(user, 'email') and user.email == 'root@gmail.com':
                return redirect('dashboard')  # Si quieres root a crop_list, cambia aquí
            else:
                return redirect('dashboard')
        else:
            return render(request, 'auth/login.html', {
                'error': 'Email o contraseña incorrectos.',
                'email': email
            })
    
    return render(request, 'auth/login.html')


def logout_view(request):
    """
    Logout del usuario actual.
    """
    logout(request)
    return redirect('login')


def request_new_code_view(request):
    """
    Permite solicitar un nuevo código OTP sin registrar email nuevamente.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email or '@' not in email:
            return render(request, 'auth/request_new_code.html', {
                'error': 'Por favor ingresa un email válido.'
            })
        
        # Verificar que el email no esté ya registrado
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'auth/request_new_code.html', {
                'error': 'Este email ya está registrado.',
                'email': email
            })
        
        # Generar nuevo código
        code = ''.join(random.choices(string.digits, k=6))
        EmailVerification.objects.filter(email=email).delete()
        
        expires_at = timezone.now() + timedelta(minutes=15)
        EmailVerification.objects.create(
            email=email,
            code=code,
            expires_at=expires_at
        )
        
        # Enviar email
        try:
            send_mail(
                subject='AgroSmart - Código de Verificación',
                message=f'Tu código de verificación es: {code}\n\nEste código expirará en 15 minutos.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            return redirect('verify_email', email=email)
        except Exception as e:
            print(f"Error al enviar email: {e}")
            import traceback
            traceback.print_exc()
            return render(request, 'auth/request_new_code.html', {
                'error': f'Error al enviar el email: {str(e)}. Verifica que EMAIL_HOST_USER y EMAIL_HOST_PASSWORD estén configurados correctamente en .env',
                'email': email
            })
    
    return render(request, 'auth/request_new_code.html')


def setup_gmail_view(request):
    """
    Página con instrucciones para configurar Gmail.
    """
    return render(request, 'auth/setup_gmail.html')


def recover_account_view(request):
    """
    Solicita email y envía código de recuperación, igual que el registro.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email or '@' not in email:
            return render(request, 'auth/recover_account.html', {
                'error': 'Por favor ingresa un email válido.'
            })
        if not CustomUser.objects.filter(email=email).exists():
            return render(request, 'auth/recover_account.html', {
                'error': 'No existe una cuenta con ese email.',
                'email': email
            })
        code = ''.join(random.choices(string.digits, k=6))
        EmailVerification.objects.filter(email=email).delete()
        expires_at = timezone.now() + timedelta(minutes=15)
        EmailVerification.objects.create(
            email=email,
            code=code,
            expires_at=expires_at
        )
        try:
            send_mail(
                subject='AgroSmart - Código de Recuperación',
                message=f'Tu código de recuperación es: {code}\n\nEste código expirará en 15 minutos.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            return render(request, 'auth/recover_account.html', {
                'error': f'Error al enviar el email: {str(e)}. Verifica configuración.',
                'email': email
            })
        return redirect('verify_email', email=email)
    return render(request, 'auth/recover_account.html')

