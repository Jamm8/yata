# Generated by Django 2.0.5 on 2019-06-17 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chain', '0048_count_bonus'),
    ]

    operations = [
        migrations.AddField(
            model_name='faction',
            name='numberOfKeys',
            field=models.IntegerField(default=0),
        ),
    ]
