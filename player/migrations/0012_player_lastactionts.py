# Generated by Django 2.0.5 on 2019-06-03 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0011_player_factionna'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='lastActionTS',
            field=models.IntegerField(default=0),
        ),
    ]
