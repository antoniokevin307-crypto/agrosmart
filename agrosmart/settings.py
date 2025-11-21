from pathlib import Path
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Directorio base donde se encuentra el proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Clave secreta (cámbiala al desplegar el proyecto en producción)
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-key-solo-local")

# Activar el modo de depuración (solo en desarrollo)
DEBUG = os.getenv("DEBUG", "True") == "True"

# Listar dominios permitidos (al desplegar en producción, agrega los dominios aquí)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '26.143.65.69']

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'monitor',  # Nuestra app del proyecto
]

# Middleware de seguridad y sesiones
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL principal para las vistas
ROOT_URLCONF = 'agrosmart.urls'

# Configuración de plantillas (directorio de plantillas y contexto)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Configuración WSGI (para el servidor)
WSGI_APPLICATION = 'agrosmart.wsgi.application'

# Configuración de la base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'agrosmart.db',  # Nombre de la base de datos SQLite
    }
}

# Validadores de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Configuración de idioma y zona horaria
LANGUAGE_CODE = 'es-sv'
TIME_ZONE = 'America/El_Salvador'
USE_I18N = True
USE_TZ = True

# Configuración de archivos estáticos (CSS, JavaScript, imágenes)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media files (uploads de usuarios: fotos de perfil, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Usar claves de tipo BigAutoField para las nuevas tablas en Django 3.2+
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# API Key para Google Cloud Vision
GOOGLE_CLOUD_VISION_API_KEY = os.getenv("GOOGLE_CLOUD_VISION_API_KEY", "AIzaSyBu4N-TxpS-M_NPmzm6rCgvM3G_GnLTmZg")

# Clave API de OpenWeatherMap
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "")
if not OPENWEATHERMAP_API_KEY:
    raise ValueError("Falta OPENWEATHERMAP_API_KEY en .env")

DEFAULT_CITY = os.getenv("DEFAULT_CITY", "San Miguel")  # Ciudad predeterminada
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "SV")  # País predeterminado

# Verificación de la clave API
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "default-weather-api-key")
if not WEATHER_API_KEY:
    raise ValueError("Falta WEATHER_API_KEY en .env")

# ===== AUTENTICACIÓN =====
# Custom User Model para autenticación con email
AUTH_USER_MODEL = 'monitor.CustomUser'

# ===== EMAIL SMTP (Gmail) =====
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")  # tu_email@gmail.com
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")  # Contraseña de app
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
