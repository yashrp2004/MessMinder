# Generated by Django 4.1.7 on 2023-05-07 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_staff_leave_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff_leave',
            name='to_date',
            field=models.CharField(default=0, max_length=100),
        ),
    ]
