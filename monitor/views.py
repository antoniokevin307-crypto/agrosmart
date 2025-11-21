from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render
from .models import AbonoApplication
from django.utils import timezone

@login_required(login_url='login')
@require_POST
def update_abono_status(request, abono_id, new_status):
    abono = get_object_or_404(AbonoApplication, id=abono_id)
    if new_status in ["aplicado", "no_aplicado"]:
        abono.status = new_status
        abono.date_applied = timezone.now()
        abono.save()
    return redirect('abono_application', crop_id=abono.crop.id)
from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def crop_detail(request, crop_id):
    crop = get_object_or_404(Crop, pk=crop_id)
    # Obtener clima y recomendación IA
    weather = None
    recommendation = None
    error = None
    calendar_data = None
    try:
        weather = fetch_current_weather(lat=crop.latitude, lon=crop.longitude) if crop.latitude and crop.longitude else fetch_current_weather(settings.DEFAULT_CITY, settings.DEFAULT_COUNTRY)
        if weather.get("ok"):
            temp = weather["temperature"]
            hum = weather["humidity"]
            rain = weather["rain_mm"]
            recommendation = irrigation_recommendation(temp, hum, rain)
        else:
            error = weather.get("error", "No fue posible obtener el clima.")
    except Exception as e:
        error = str(e)
    # Simular calendario de fechas óptimas para plantar
    import calendar, datetime, random
    today = datetime.date.today()
    year = today.year
    month = today.month
    days = calendar.monthrange(year, month)[1]
    calendar_data = []
    for day in range(1, days+1):
        rec = random.choices(["verde", "amarillo", "rojo"], weights=[5,2,1])[0]
        calendar_data.append({"day": day, "color": rec})
    # Configuración del mapa
    map_center_lat = crop.latitude or 0
    map_center_lon = crop.longitude or 0
    map_zoom = 13 if crop.latitude and crop.longitude else 3
    cfg = {
        "apiKey": getattr(settings, "OPENWEATHERMAP_API_KEY", ""),
        "center": [map_center_lat, map_center_lon],
        "zoom": map_zoom,
        "weather": {
            "temperature": weather.get("temperature") if weather and weather.get("ok") else None,
            "humidity": weather.get("humidity") if weather and weather.get("ok") else None,
            "rain_mm": weather.get("rain_mm") if weather and weather.get("ok") else None,
            "wind_ms": weather.get("wind_ms") if weather and weather.get("ok") else None,
        },
        "current_crop": {
            "id": crop.id,
            "name": crop.name,
            "description": crop.description or "",
            "lat": crop.latitude,
            "lon": crop.longitude,
        },
        "is_specific_crop": True,
    }
    context = {
        "crop": crop,
        "weather": weather,
        "recommendation": recommendation,
        "error": error,
        "calendar_data": calendar_data,
        "openweather_api_key": cfg["apiKey"],
        "weather_map_config_json": json.dumps(cfg),
    }
    return render(request, "crops/crop_detail.html", context)

from django.conf import settings
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from .models import Crop, WeatherRecord, CustomUser, CropAlert, AbonoApplication
from .forms import CropForm, AbonoApplicationForm
import datetime
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.utils.timezone import now, timedelta
from dateutil.relativedelta import relativedelta

@login_required(login_url='login')
def planting_calendar(request, crop_id):
    crop = get_object_or_404(Crop, pk=crop_id)
    # Simulación: para cada día del mes, IA/clima recomienda verde/amarillo/rojo
    import calendar, datetime
    today = datetime.date.today()
    year = today.year
    month = today.month
    days = calendar.monthrange(year, month)[1]
    calendar_data = []
    for day in range(1, days+1):
        # Simular recomendación: aleatorio o basado en clima real
        import random
        rec = random.choices(["verde", "amarillo", "rojo"], weights=[5,2,1])[0]
        calendar_data.append({"day": day, "color": rec})
    return render(request, "crops/planting_calendar.html", {"crop": crop, "calendar_data": calendar_data, "month": month, "year": year})

@login_required(login_url='login')
def abono_application(request, crop_id):
    crop = get_object_or_404(Crop, pk=crop_id)
    if request.user != crop.user and request.user.email != 'root@gmail.com':
        messages.error(request, "No tienes permiso para registrar abono en este cultivo.")
        return redirect("dashboard_crop", crop_id=crop_id)

    today = now().date()

    # Eliminar el formulario si no es necesario
    form = None

    # Solo crear abonos si no existen para este cultivo
    if not AbonoApplication.objects.filter(crop=crop).exists():
        base_date = crop.sowing_date if crop.sowing_date else today
        import random
        tips = [
            "Primer abono: fertilización inicial para estimular raíces.",
            "Segundo abono: refuerzo de nitrógeno para crecimiento vegetativo.",
            "Tercer abono: aplicar potasio para floración.",
            "Cuarto abono: micronutrientes para resistencia a enfermedades.",
            "Quinto abono: refuerzo de fósforo antes de fructificación.",
            "Sexto abono: abono orgánico para mejorar suelo.",
            "Séptimo abono: control de plagas y refuerzo nutricional.",
            "Octavo abono: potasio para maduración de frutos.",
            "Noveno abono: micronutrientes post-cosecha.",
            "Décimo abono: compost para recuperación del suelo."
        ]
        abono_dates = [base_date]
        for i in range(1, 10):
            delta_months = random.choice([1, 2, 3])
            next_date = abono_dates[-1] + relativedelta(months=delta_months)
            abono_dates.append(next_date)
        for i, abono_date in enumerate(abono_dates):
            tip = tips[i] if i < len(tips) else "Abono de mantenimiento."
            AbonoApplication.objects.create(
                crop=crop,
                scheduled_date=abono_date,
                status="pendiente",
                tip=tip
            )

    # Optimizar consulta con paginación
    abonos_list = AbonoApplication.objects.filter(crop=crop).order_by("-scheduled_date", "-date_applied")
    paginator = Paginator(abonos_list, 10)  # Mostrar 10 registros por página
    page_number = request.GET.get('page')
    abonos = paginator.get_page(page_number)

    return render(request, "crops/abono_application.html", {"crop": crop, "abonos": abonos, "today": today})
from .services.weather import fetch_current_weather
from .services.recommender import irrigation_recommendation
from .services.pdf_generator import generate_crop_pdf, generate_crops_batch_pdf
from .services import ai_service
from .forms import ProfileForm
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import re

@login_required(login_url='login')
def home(request):
    """
    Página de inicio: lista de cultivos del usuario actual.
    Si el usuario es root, muestra todos los cultivos.
    """
    if request.user.email == 'root@gmail.com':
        crops = Crop.objects.all()
    else:
        crops = Crop.objects.filter(user=request.user)
    return render(request, "crops/crop_list.html", {"crops": crops})


@login_required(login_url='login')

def crop_create(request):
    """
    Formulario para crear un cultivo (parcela) nuevo.
    """
    BLACKLIST = ["marihuana", "cannabis", "coca", "opio", "amapola", "heroína", "cocaína", "droga"]
    # Generar calendario de fechas óptimas para plantar
    import calendar, datetime, random
    today = datetime.date.today()
    year = today.year
    month = today.month
    days = calendar.monthrange(year, month)[1]
    calendar_data = []
    for day in range(1, days+1):
        rec = random.choices(["verde", "amarillo", "rojo"], weights=[5,2,1])[0]
        calendar_data.append({"day": day, "color": rec})
    if request.method == "POST":
        form = CropForm(request.POST)
        if form.is_valid():
            crop = form.save(commit=False)
            # Verificar nombre contra lista negra
            if any(bad in crop.name.lower() for bad in BLACKLIST):
                form.add_error("name", "Este cultivo está prohibido por la ley.")
            else:
                crop.user = request.user  # Asignar el usuario actual
                crop.save()
                messages.success(request, "Cultivo creado correctamente.")
                return redirect("dashboard")
    else:
        form = CropForm(initial={
            "country_code": settings.DEFAULT_COUNTRY
        })
    return render(request, "crops/crop_form.html", {"form": form, "calendar_data": calendar_data, "month": month, "year": year})

@login_required(login_url='login')

def crop_edit(request, crop_id):
    """
    Editar un cultivo existente (modificar ubicación y descripción).
    """
    crop = get_object_or_404(Crop, pk=crop_id)
    # Generar calendario de fechas óptimas para plantar
    import calendar, datetime, random
    today = datetime.date.today()
    year = today.year
    month = today.month
    days = calendar.monthrange(year, month)[1]
    calendar_data = []
    for day in range(1, days+1):
        rec = random.choices(["verde", "amarillo", "rojo"], weights=[5,2,1])[0]
        calendar_data.append({"day": day, "color": rec})
    # Verificar permiso: solo el propietario o root pueden editar
    if request.user != crop.user and request.user.email != 'root@gmail.com':
        messages.error(request, "No tienes permiso para editar este cultivo.")
        return redirect("crop_list")
    if request.method == "POST":
        form = CropForm(request.POST, instance=crop)
        if form.is_valid():
            form.save()
            messages.success(request, "Cultivo actualizado correctamente.")
            return redirect("dashboard")
    else:
        form = CropForm(instance=crop)
    return render(request, "crops/crop_form.html", {"form": form, "edit_mode": True, "crop": crop, "calendar_data": calendar_data, "month": month, "year": year})

@login_required(login_url='login')
def crop_delete(request, crop_id):
    """
    Eliminar un cultivo (con confirmación).
    """
    crop = get_object_or_404(Crop, pk=crop_id)
    
    # Verificar permiso: solo el propietario o root pueden eliminar
    if request.user != crop.user and request.user.email != 'root@gmail.com':
        messages.error(request, "No tienes permiso para eliminar este cultivo.")
        return redirect("dashboard")
    
    if request.method == "POST":
        crop.delete()
        messages.success(request, "Cultivo eliminado correctamente.")
        return redirect("dashboard")
    return render(request, "crops/crop_confirm_delete.html", {"crop": crop})

@login_required(login_url='login')
def dashboard(request, crop_id: int | None = None):
    """
    Dashboard principal:
    - Si se pasa crop_id, usa esa parcela con zoom cercano.
    - Si no, toma la primera o muestra vista general (zoom 3).
    - Consulta clima, calcula recomendación y guarda registro.
    """
    is_specific_crop = crop_id is not None
    
    if crop_id:
        crop = get_object_or_404(Crop, pk=crop_id)
        
        # Verificar permisos: usuario actual o root
        if request.user != crop.user and request.user.email != 'root@gmail.com':
            messages.error(request, "No tienes permiso para ver este dashboard.")
            return redirect("crop_list")
    else:
        # Obtener el primer cultivo del usuario o de cualquiera si es root
        if request.user.email == 'root@gmail.com':
            crop = Crop.objects.first()
        else:
            crop = Crop.objects.filter(user=request.user).first()
        
        if not crop:
            # Sin cultivo aún: usar valores por defecto del .env para demo.
            crop = Crop(name="Demo", country_code=settings.DEFAULT_COUNTRY)
            # No guardamos en DB para no ensuciar en demo.

    # Obtener clima: preferir coordenadas del cultivo si existen, sino usar ciudad por defecto
    if crop.latitude is not None and crop.longitude is not None:
        weather = fetch_current_weather(lat=crop.latitude, lon=crop.longitude)
    else:
        # No hay coordenadas: usar ciudad predeterminada desde settings
        weather = fetch_current_weather(settings.DEFAULT_CITY, settings.DEFAULT_COUNTRY)

    # Obtener cultivos para el dashboard (todos si root, solo propios si usuario normal)
    if request.user.email == 'root@gmail.com':
        crops = Crop.objects.all()
    else:
        crops = Crop.objects.filter(user=request.user)

    context = {"crop": crop, "weather": None, "recommendation": None, "error": None, "crops": crops}

    if weather.get("ok"):
        temp = weather["temperature"]
        hum = weather["humidity"]
        rain = weather["rain_mm"]
        rec = irrigation_recommendation(temp, hum, rain)

        # Guardar histórico sólo si el cultivo está en BD (tiene id)
        if crop.id:
            WeatherRecord.objects.create(
                crop=crop, temperature=temp, humidity=hum, rain_mm=rain,
                wind_ms=weather["wind_ms"], recommendation=rec
            )

            # ALERTA AUTOMÁTICA: Si la recomendación es crítica, crear alerta y enviar email
            rec_lower = rec.lower() if rec else ""
            if any(word in rec_lower for word in ["regar", "abono", "fertilizante", "alta temperatura"]):
                # Solo crear si no hay alerta pendiente igual
                from .models import CropAlert
                last_alert = CropAlert.objects.filter(crop=crop, resolved=False, alert_type__in=["irrigation","fertilizer","general"]).order_by('-created_at').first()
                if not last_alert or last_alert.message != rec:
                    alert_type = "irrigation" if "regar" in rec_lower else ("fertilizer" if "abono" in rec_lower or "fertilizante" in rec_lower else "general")
                    alert = CropAlert.objects.create(
                        crop=crop,
                        alert_type=alert_type,
                        message=rec,
                        notified=True,
                        resolved=False
                    )
                    # Enviar email automático
                    subject = f"Alerta automática para tu cultivo: {crop.name}"
                    msg = f"Se ha detectado una condición que requiere atención en tu cultivo '{crop.name}':\n\n{rec}\n\nPor favor revisa el sistema para más detalles."
                    try:
                        send_mail(subject, msg, settings.DEFAULT_FROM_EMAIL, [crop.user.email], fail_silently=True)
                    except Exception:
                        pass

        context.update({
            "weather": weather,
            "recommendation": rec,
        })
    else:
        context["error"] = weather.get("error", "No fue posible obtener el clima.")

    # Mapa: si es crop específico y tiene coordenadas, centrar en él. Si no, vista general.
    map_center_lat = 0
    map_center_lon = 0
    map_zoom = 3  # Vista general mundial
    
    if is_specific_crop and crop.latitude and crop.longitude:
        map_center_lat = crop.latitude
        map_center_lon = crop.longitude
        map_zoom = 13  # Zoom cercano al cultivo
    elif weather.get("ok") and isinstance(weather.get("raw"), dict):
        # Usar ubicación de la API como fallback
        loc = weather.get("raw", {}).get("location", {})
        map_center_lat = loc.get("lat", 0) or 0
        map_center_lon = loc.get("lon", 0) or 0
        map_zoom = 8

    # Construir objeto de configuración para pasar al template como JSON seguro
    cfg = {
        "apiKey": getattr(settings, "OPENWEATHERMAP_API_KEY", ""),
        "center": [map_center_lat or 0, map_center_lon or 0],
        "zoom": map_zoom,
        "weather": {
            "temperature": weather.get("temperature") if weather.get("ok") else None,
            "humidity": weather.get("humidity") if weather.get("ok") else None,
            "rain_mm": weather.get("rain_mm") if weather.get("ok") else None,
            "wind_ms": weather.get("wind_ms") if weather.get("ok") else None,
        },
        "current_crop": {
            "id": crop.id,
            "name": crop.name,
            "description": crop.description or "",
            "lat": crop.latitude,
            "lon": crop.longitude,
        },
        "is_specific_crop": is_specific_crop,
    }

    cfg["apiKey"] = settings.OPENWEATHERMAP_API_KEY  # Pasar la clave al frontend

    # Añadir marcadores para cultivos guardados con lat/lon
    crops_with_geo = []
    for c in Crop.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True):
        if c.latitude is not None and c.longitude is not None:
            # Determinar si es un cultivo del usuario actual (para colorear en verde)
            is_owner = (c.user == request.user)
            crops_with_geo.append({
                "id": c.id,
                "name": c.name,
                "description": c.description or "",
                "lat": c.latitude,
                "lon": c.longitude,
                "is_owner": is_owner,  # Verde si es del usuario, gris si es de otro
                "owner_email": c.user.email,
            })
    cfg["crops"] = crops_with_geo

    context.update({
        "openweather_api_key": cfg["apiKey"],
        "map_center_lat": map_center_lat,
        "map_center_lon": map_center_lon,
        "weather_map_config_json": json.dumps(cfg),
    })

    return render(request, "dashboard.html", context)


@login_required(login_url='login')
def get_crop_weather(request, crop_id):
    """
    Endpoint AJAX para obtener el clima de un cultivo específico.
    Retorna JSON con clima, recomendación, etc.
    """
    crop = get_object_or_404(Crop, pk=crop_id)
    
    # Verificar permisos
    if request.user != crop.user and request.user.email != 'root@gmail.com':
        return JsonResponse({
            "ok": False,
            "error": "No tienes permiso para acceder a este cultivo."
        }, status=403)
    
    if crop.latitude is not None and crop.longitude is not None:
        weather = fetch_current_weather(lat=crop.latitude, lon=crop.longitude)
    else:
        weather = fetch_current_weather(settings.DEFAULT_CITY, settings.DEFAULT_COUNTRY)
    
    response = {"ok": False}
    
    if weather.get("ok"):
        temp = weather["temperature"]
        hum = weather["humidity"]
        rain = weather["rain_mm"]
        rec = irrigation_recommendation(temp, hum, rain)
        
        response = {
            "ok": True,
            "crop_id": crop.id,
            "crop_name": crop.name,
            "crop_description": crop.description,
            "crop_lat": crop.latitude,
            "crop_lon": crop.longitude,
            "temperature": temp,
            "humidity": hum,
            "rain_mm": rain,
            "wind_ms": weather["wind_ms"],
            "recommendation": rec,
        }
    else:
        response = {
            "ok": False,
            "error": weather.get("error", "No fue posible obtener el clima."),
        }
    
    return JsonResponse(response)


@login_required(login_url='login')
def download_crop_pdf_user(request, crop_id):
    """
    Descargar PDF de un cultivo específico (usuarios normales).
    Solo pueden descargar sus propios cultivos.
    """
    crop = get_object_or_404(Crop, pk=crop_id)
    
    # Verificar permiso: solo el propietario
    if crop.user != request.user:
        messages.error(request, "No tienes permiso para descargar este cultivo.")
        return redirect('crop_list')
    
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
def download_my_crops_pdf(request):
    """
    Descargar PDF con todos los cultivos del usuario actual.
    """
    crops = Crop.objects.filter(user=request.user)
    
    if not crops.exists():
        messages.warning(request, 'No tienes cultivos para descargar.')
        return redirect('crop_list')
    
    # Generar PDF
    pdf_buffer = generate_crops_batch_pdf(crops)
    
    # Retornar como descarga
    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    filename = f'mis_cultivos_{request.user.email.replace("@", "_").replace(".", "_")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required(login_url='login')
def profile_view(request):
    """
    Ver perfil del usuario actual (o editar desde otro lado).
    """
    user = request.user
    return render(request, "auth/profile.html", {"user_obj": user})


@login_required(login_url='login')
def profile_edit(request):
    """
    Editar perfil: display_name, profile_photo y bio.
    """
    user = request.user
    error = None
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Perfil actualizado correctamente.")
                return redirect('profile')
            except Exception as e:
                error = f"Error al guardar el perfil: {e}"
        else:
            error = "Formulario inválido. Revisa los campos."
    else:
        form = ProfileForm(instance=user)
    return render(request, "auth/profile_form.html", {"form": form, "error": error})


@login_required(login_url='login')
@require_http_methods(["POST"])
@csrf_exempt
def ai_chat(request):
    """
    Endpoint de chat IA agrícola, ahora solo maneja mensajes.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception:
            data = request.POST
        question = data.get('question', '').strip()
        crop_id = data.get('crop_id') or None
    else:
        question = request.POST.get('question', '').strip()
        crop_id = request.POST.get('crop_id') or None
    if not question:
        return JsonResponse({"ok": False, "answer": "Pregunta vacía."}, status=400)
    crop_info = None
    if crop_id:
        try:
            c = Crop.objects.get(pk=int(crop_id))
            crop_info = {"name": c.name, "lat": c.latitude, "lon": c.longitude}
        except Exception:
            crop_info = None
    ai_result = ai_service.get_agriculture_answer(question, crop_info)
    response = {
        "ok": ai_result.get('ok', False),
        "question": question,
        "answer": ai_result.get('answer'),
        "source": ai_result.get('source'),
        "image_url": ai_result.get('image_url'),
    }
    return JsonResponse(response)


@login_required(login_url='login')
@require_http_methods(["POST"])
def alert_response(request, crop_id):
    """
    Registrar la respuesta del usuario a una alerta (ej. 'abono_aplicado' o 'no_aplicado').
    Guardamos la última acción en la sesión para simplicidad.
    """
    action = request.POST.get('action')
    if action not in ('abono_aplicado', 'no_aplicado'):
        return JsonResponse({"ok": False, "error": "Acción inválida."}, status=400)

    # Verificar permiso: solo propietario o root puede responder alertas de ese cultivo
    crop = get_object_or_404(Crop, pk=crop_id)
    if request.user != crop.user and request.user.email != 'root@gmail.com':
        return JsonResponse({"ok": False, "error": "No tienes permiso para responder esta alerta."}, status=403)

    # Buscar la alerta más reciente no resuelta para este cultivo
    alert = CropAlert.objects.filter(crop=crop, resolved=False).order_by('-created_at').first()
    if alert:
        alert.user_response = action
        alert.resolved = True
        alert.save()
    else:
        # Si no existe una alerta pendiente, crear una entrada que registre la acción del usuario
        alert = CropAlert.objects.create(crop=crop, alert_type='general', message=f'Respuesta manual: {action}', notified=False, resolved=True, user_response=action)

    return JsonResponse({"ok": True, "crop_id": crop_id, "action": action, "alert_id": alert.id})



def _send_alert_email(user_email: str, subject: str, message: str):
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
        return True
    except Exception:
        return False


@login_required(login_url='login')
def alerts_list(request):
    """Listar alertas para el usuario (o todas para root)."""
    if request.user.email == 'root@gmail.com':
        alerts = CropAlert.objects.select_related('crop', 'crop__user').all()
    else:
        alerts = CropAlert.objects.select_related('crop').filter(crop__user=request.user)
    return render(request, 'alerts/alerts_list.html', {'alerts': alerts})


@login_required(login_url='login')
@require_http_methods(['POST'])
def resolve_alert(request, alert_id):
    alert = get_object_or_404(CropAlert, pk=alert_id)
    # Permiso: propietario del cultivo o root
    if request.user != alert.crop.user and request.user.email != 'root@gmail.com':
        return JsonResponse({"ok": False, "error": "No tienes permiso para resolver esta alerta."}, status=403)
    alert.resolved = True
    alert.user_response = request.POST.get('response', '')
    alert.save()
    return JsonResponse({"ok": True, "alert_id": alert.id})

def about(request):
    return render(request, "about.html")

def contact_page(request):
    contact_success = False
    contact_error = False
    if request.method == "POST":
        name = request.POST.get("contact_name", "")
        email = request.POST.get("contact_email", "")
        subject = request.POST.get("contact_subject", "")
        message = request.POST.get("contact_message", "")
        full_message = f"De: {name} <{email}>\n\n{message}"
        try:
            send_mail(
                subject,
                full_message,
                settings.DEFAULT_FROM_EMAIL,
                ["antoniokevin307@gmail.com"],
                fail_silently=False,
            )
            contact_success = True
        except Exception:
            contact_error = True
    return render(request, "contact.html", {
        "contact_success": contact_success,
        "contact_error": contact_error,
    })
