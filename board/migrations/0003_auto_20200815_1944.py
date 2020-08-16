# Generated by Django 2.2.5 on 2020-08-15 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0002_auto_20200108_0647'),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(max_length=30)),
                ('totalGames', models.IntegerField(null=True)),
                ('isAI', models.BooleanField(default=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Node',
        ),
        migrations.AlterField(
            model_name='board',
            name='name',
            field=models.CharField(max_length=30),
        ),
    ]
