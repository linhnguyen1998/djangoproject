# Generated by Django 2.2 on 2019-06-10 08:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20190610_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='shipper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Shipper',
        ),
    ]