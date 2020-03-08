# Generated by Django 3.0.1 on 2020-02-20 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0030_guild_systemchannel'),
    ]

    operations = [
        migrations.AddField(
            model_name='guild',
            name='botContactId',
            field=models.IntegerField(default=2000607),
        ),
        migrations.AddField(
            model_name='guild',
            name='botContactName',
            field=models.CharField(default='Kivou', max_length=32),
        ),
        migrations.AlterField(
            model_name='guild',
            name='guildContactId',
            field=models.IntegerField(default=0),
        ),
    ]