from django.core.management.base import BaseCommand
from monitor.models import CustomUser


class Command(BaseCommand):
    help = 'Crea el usuario root@gmail.com si no existe'

    def handle(self, *args, **options):
        # Credenciales del usuario root
        email = 'root@gmail.com'
        password = 'Antho-XD07'
        
        # Verificar si el usuario ya existe
        if CustomUser.objects.filter(email=email).exists():
            self.stdout.write(self.style.SUCCESS(f'El usuario {email} ya existe.'))
            return
        
        # Crear usuario root
        user = CustomUser.objects.create_superuser(
            email=email,
            password=password
        )
        
        self.stdout.write(self.style.SUCCESS(f'Usuario root creado exitosamente: {email}'))
