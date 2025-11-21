from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class AbonoApplication(models.Model):
    """
    Historial de aplicación de abono/fertilizante por cultivo.
    """
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("aplicado", "Aplicado"),
        ("no_aplicado", "No Aplicado"),
    ]

    crop = models.ForeignKey('Crop', on_delete=models.CASCADE, related_name="abono_applications")
    user = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name="abono_applications")
    date_applied = models.DateTimeField("Fecha de aplicación", null=True, blank=True)
    scheduled_date = models.DateField("Fecha programada", default=timezone.now)
    status = models.CharField("Estado", max_length=20, choices=ESTADOS, default="pendiente")
    notes = models.TextField("Notas", blank=True, default="")
    tip = models.CharField("Tip de abono", max_length=255, blank=True, default="")

    class Meta:
        verbose_name = "Aplicación de Abono"
        verbose_name_plural = "Aplicaciones de Abono"
        ordering = ["-scheduled_date", "-date_applied"]

    def __str__(self):
        return f"Abono en {self.crop.name} ({self.get_status_display()}) el {self.scheduled_date}"

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es requerido")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Usuario personalizado basado en email con verificación por código OTP.
    """
    email = models.EmailField("Email", unique=True)
    username = models.CharField("Usuario", max_length=80, blank=True, default="")
    # Perfil público
    display_name = models.CharField("Nombre visible", max_length=120, blank=True, default="")
    profile_photo = models.ImageField("Foto de perfil", upload_to="profiles/", null=True, blank=True)
    bio = models.TextField("Descripción", blank=True, default="")
    is_verified = models.BooleanField("Email verificado", default=False)
    is_active = models.BooleanField("Activo", default=True)
    is_staff = models.BooleanField("Staff", default=False)
    created_at = models.DateTimeField("Creado", auto_now_add=True)

    # Groups and user_permissions con related_names alternativos para evitar conflictos
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='customuser_groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='customuser_user_permissions',
        help_text='Specific permissions for this user.',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email


class EmailVerification(models.Model):
    """
    Códigos OTP temporales para verificación de email durante registro.
    """
    email = models.EmailField("Email")
    code = models.CharField("Código OTP", max_length=6)
    attempts = models.IntegerField("Intentos fallidos", default=0)
    created_at = models.DateTimeField("Creado", auto_now_add=True)
    expires_at = models.DateTimeField("Expira")

    class Meta:
        verbose_name = "Verificación de Email"
        verbose_name_plural = "Verificaciones de Email"

    def __str__(self):
        return f"{self.email} - {self.code}"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        return not self.is_expired() and self.attempts < 5


class Crop(models.Model):
    """
    Modelo simple de 'Cultivo' (parcela) para asociar una ciudad/país
    y así obtener el clima y recomendaciones específicas.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="crops")
    name = models.CharField("Nombre del cultivo", max_length=80)
    description = models.TextField("Descripción (fecha, cantidad, etc.)", blank=True, default="")
    country_code = models.CharField("País (ISO2)", max_length=2, default="SV")
    latitude = models.FloatField("Latitud", null=True, blank=True)
    longitude = models.FloatField("Longitud", null=True, blank=True)
    sowing_date = models.DateField("Fecha de siembra", null=True, blank=True)
    created_at = models.DateTimeField("Creado", auto_now_add=True)

    class Meta:
        verbose_name = "Cultivo"
        verbose_name_plural = "Cultivos"
        ordering = ["-created_at"]

    def __str__(self):
        coords = f" {self.latitude:.4f},{self.longitude:.4f}" if self.latitude and self.longitude else ""
        return f"{self.name} ({self.country_code}){coords}"


class WeatherRecord(models.Model):
    """
    Registro histórico simple para auditoría y gráficos.
    Se puede poblar al consultar el dashboard.
    """
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name="records")
    timestamp = models.DateTimeField(auto_now_add=True)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    rain_mm = models.FloatField(null=True, blank=True)
    wind_ms = models.FloatField(null=True, blank=True)
    recommendation = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Registro Climático"
        verbose_name_plural = "Registros Climáticos"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.crop.name} @ {self.timestamp:%Y-%m-%d %H:%M}"


class CropAlert(models.Model):
    """
    Alerta generada por el sistema (o IA) para un cultivo.
    Se persiste para poder auditar notificaciones y respuestas de usuario.
    """
    ALERT_TYPES = [
        ("irrigation", "Riego"),
        ("fertilizer", "Fertilizante"),
        ("pest", "Plaga / Enfermedad"),
        ("general", "General"),
    ]

    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name="alerts")
    alert_type = models.CharField(max_length=32, choices=ALERT_TYPES, default="general")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)
    user_response = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        verbose_name = "Alerta de Cultivo"
        verbose_name_plural = "Alertas de Cultivo"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Alerta {self.alert_type} para {self.crop.name} ({self.created_at:%Y-%m-%d %H:%M})"
