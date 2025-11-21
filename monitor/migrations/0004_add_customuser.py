from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("monitor", "0003_replace_city_with_description"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('username', models.CharField(blank=True, default='', max_length=80, verbose_name='Usuario')),
                ('is_verified', models.BooleanField(default=False, verbose_name='Email verificado')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Staff')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Creado')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='customuser_groups', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='customuser_user_permissions', to='auth.permission')),
            ],
            options={
                'verbose_name': 'Usuario',
                'verbose_name_plural': 'Usuarios',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='EmailVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('code', models.CharField(max_length=6, verbose_name='Código OTP')),
                ('attempts', models.IntegerField(default=0, verbose_name='Intentos fallidos')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Creado')),
                ('expires_at', models.DateTimeField(verbose_name='Expira')),
            ],
            options={
                'verbose_name': 'Verificación de Email',
                'verbose_name_plural': 'Verificaciones de Email',
            },
        ),
        migrations.AddField(
            model_name='crop',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crops', to='monitor.customuser'),
        ),
    ]

