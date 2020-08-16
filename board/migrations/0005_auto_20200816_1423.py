# Generated by Django 2.2.5 on 2020-08-16 12:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0004_auto_20200815_2100'),
    ]

    operations = [
        migrations.CreateModel(
            name='AI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='player',
            name='ai',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='AI', to='board.AI'),
        ),
    ]