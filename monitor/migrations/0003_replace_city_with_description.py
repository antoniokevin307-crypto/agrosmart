from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("monitor", "0002_add_latitude_longitude"),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crop',
            name='city',
        ),
        migrations.AddField(
            model_name='crop',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='Descripción (fecha, cantidad, etc.)'),
        ),
    ]
