# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_add_gender_to_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='class_subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.classsubject'),
        ),
    ] 