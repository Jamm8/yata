# Generated by Django 3.0.1 on 2020-01-27 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faction', '0005_faction_memberstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='faction',
            name='memberStatusUpda',
            field=models.IntegerField(default=0),
        ),
    ]
