# Generated by Django 4.1.5 on 2023-04-29 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_satisfaction_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='id',
            field=models.IntegerField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='satisfaction',
            name='id',
            field=models.IntegerField(auto_created=True, primary_key=True, serialize=False),
        ),
    ]