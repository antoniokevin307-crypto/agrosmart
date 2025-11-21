from django.core.management.base import BaseCommand
from monitor.models import Crop, CropAlert
from monitor.services.weather import fetch_current_weather
from monitor.services.recommender import irrigation_recommendation
from monitor.services import ai_service
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Comprueba cultivos, usa IA para evaluar riesgos y envía alertas por correo si aplica.'

    def handle(self, *args, **options):
        crops = Crop.objects.all()
        for c in crops:
            if c.latitude is None or c.longitude is None:
                continue
            weather = fetch_current_weather(lat=c.latitude, lon=c.longitude)
            if not weather.get('ok'):
                continue
            temp = weather.get('temperature')
            hum = weather.get('humidity')
            rain = weather.get('rain_mm')
            rec = irrigation_recommendation(temp, hum, rain)

            # Determinar si IA considera que debe ser alerta
            prompt_question = f"¿Debería enviar una alerta al agricultor del cultivo '{c.name}' con lat={c.latitude} lon={c.longitude} si la recomendación automática es: {rec}? Responde sí/no y breve razón."
            ai_resp = ai_service.get_agriculture_answer(prompt_question, {"name": c.name, "lat": c.latitude, "lon": c.longitude})
            should_alert = False
            reason = ''
            if ai_resp.get('ok'):
                ans = ai_resp.get('answer', '').lower()
                if 'sí' in ans or 'si' in ans or 'alert' in ans:
                    should_alert = True
                    reason = ai_resp.get('answer')
            # Fallback heurístico
            if not should_alert and ('regar' in rec.lower() or 'alta temperatura' in rec.lower()):
                should_alert = True
                reason = rec

            if should_alert:
                # Crear o actualizar alerta
                msg = f"Recomendación: {rec}\nTemperatura: {temp}\nHumedad: {hum}\nFuente: {ai_resp.get('source')}"
                alert = CropAlert.objects.create(crop=c, alert_type='irrigation', message=msg, notified=False)
                subject = f'Alerta: {c.name} necesita atención'
                message = f"Hola {c.user.display_name or c.user.email},\n\n{msg}\n\nIngresa a la app para más detalles.\n"
                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [c.user.email], fail_silently=False)
                    alert.notified = True
                    alert.save()
                    self.stdout.write(self.style.SUCCESS(f'Correo enviado a {c.user.email} para cultivo {c.id} (alert {alert.id})'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error enviando correo a {c.user.email}: {e}'))
