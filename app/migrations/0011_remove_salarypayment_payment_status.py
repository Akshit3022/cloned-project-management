# Generated by Django 5.0.3 on 2024-04-18 11:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_delete_salary'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salarypayment',
            name='payment_status',
        ),
    ]