# Generated by Django 5.1.7 on 2025-04-04 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_add_teacher_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ] 