# Generated by Django 3.0.6 on 2021-01-28 21:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_app', '0005_timetable_reservation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timetable',
            name='reservation',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='project_app.Reservation'),
            preserve_default=False,
        ),
    ]
