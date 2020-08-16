# Generated by Django 2.2.5 on 2020-08-16 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0006_auto_20200816_1539'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='ai',
        ),
        migrations.AlterField(
            model_name='state',
            name='reward',
            field=models.FloatField(default=0.0, null=True),
        ),
        migrations.DeleteModel(
            name='AI',
        ),
    ]