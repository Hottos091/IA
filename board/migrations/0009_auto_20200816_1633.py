# Generated by Django 2.2.5 on 2020-08-16 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0008_auto_20200816_1621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ai',
            name='player',
            field=models.IntegerField(null=True),
        ),
    ]
