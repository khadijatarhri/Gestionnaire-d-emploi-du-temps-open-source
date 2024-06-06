# Generated by Django 5.0.6 on 2024-06-06 11:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_message'),
        ('people', '0002_remove_tutor_training_programmes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='training_program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='people.trainingprogramme'),
        ),
    ]