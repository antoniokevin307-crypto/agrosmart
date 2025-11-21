from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("monitor", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name='crop',
            name='latitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Latitud'),
        ),
        migrations.AddField(
            model_name='crop',
            name='longitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Longitud'),
        ),
    ]
