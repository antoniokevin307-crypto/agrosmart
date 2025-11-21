from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse
from monitor.models import CustomUser, Crop
from monitor.services.pdf_generator import generate_crop_pdf, generate_crops_batch_pdf
from monitor.services.weather import fetch_current_weather


def require_root(view_func):
    """Decorator para verificar que el usuario es root"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.email != 'root@gmail.com':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required(login_url='login')
@require_root
def admin_panel(request):
    """
    Panel de administración: lista de usuarios y sus cultivos.
    Solo accesible para root@gmail.com
    """
    users = CustomUser.objects.filter(email__isnull=False).exclude(email='root@gmail.com').order_by('-created_at')
    
    users_data = []
    for user in users:
        crops_count = user.crops.count()
        users_data.append({
            'user': user,
            'crops_count': crops_count,
        })
    
    context = {
        'users_data': users_data,
        'total_users': len(users_data),
    }
    
    return render(request, 'admin/panel.html', context)


@login_required(login_url='login')
@require_root
def user_detail(request, user_id):
    """
    Ver detalles de un usuario y sus cultivos.
    """
    user = get_object_or_404(CustomUser, pk=user_id)
    crops = user.crops.all()
    
    context = {
        'user': user,
        'crops': crops,
        'crops_count': crops.count(),
    }
    
    return render(request, 'admin/user_detail.html', context)


@login_required(login_url='login')
@require_root
def delete_user(request, user_id):
    """
    Eliminar un usuario (con confirmación) y todos sus cultivos.
    """
    user = get_object_or_404(CustomUser, pk=user_id)
    
    # No permitir eliminar el usuario root
    if user.email == 'root@gmail.com':
        messages.error(request, "No puedes eliminar el usuario root.")
        return redirect('admin_panel')
    
    if request.method == 'POST':
        email = user.email
        crops_count = user.crops.count()
        user.delete()
        messages.success(request, f'Usuario {email} y sus {crops_count} cultivos han sido eliminados.')
        return redirect('admin_panel')
    
    context = {
        'user': user,
        'crops_count': user.crops.count(),
    }
    
    return render(request, 'admin/confirm_delete_user.html', context)


@login_required(login_url='login')
@require_root
def delete_crop_admin(request, crop_id):
    """
    Eliminar un cultivo desde el panel de admin.
    """
    crop = get_object_or_404(Crop, pk=crop_id)
    user_id = crop.user.id
    crop_name = crop.name
    crop.delete()
    messages.success(request, f'Cultivo "{crop_name}" ha sido eliminado.')
    return redirect('user_detail', user_id=user_id)


@login_required(login_url='login')
@require_root
def download_crop_pdf(request, crop_id):
    """
    Descargar PDF con detalles del cultivo, mapa y clima.
    """
    crop = get_object_or_404(Crop, pk=crop_id)
    
    # Obtener clima actual
    weather_data = None
    if crop.latitude and crop.longitude:
        weather_data = fetch_current_weather(lat=crop.latitude, lon=crop.longitude)
    
    # Generar PDF
    pdf_buffer = generate_crop_pdf(crop, weather_data)
    
    # Retornar como descarga
    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    filename = f'cultivo_{crop.name.replace(" ", "_")}_{crop.id}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required(login_url='login')
@require_root
def download_user_crops_pdf(request, user_id):
    """
    Descargar PDF con todos los cultivos de un usuario.
    """
    user = get_object_or_404(CustomUser, pk=user_id)
    crops = user.crops.all()
    
    if not crops.exists():
        messages.warning(request, 'Este usuario no tiene cultivos para descargar.')
        return redirect('user_detail', user_id=user_id)
    
    # Generar PDF
    pdf_buffer = generate_crops_batch_pdf(crops)
    
    # Retornar como descarga
    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    filename = f'cultivos_{user.email.replace("@", "_").replace(".", "_")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
