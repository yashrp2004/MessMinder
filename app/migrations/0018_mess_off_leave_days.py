# Generated by Django 4.1.7 on 2023-05-07 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_alter_mess_off_leave_off_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mess_off_leave',
            name='days',
            field=models.IntegerField(default=0),
        ),
    ]
