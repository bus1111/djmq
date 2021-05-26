# Generated by Django 3.2.3 on 2021-05-26 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djmq', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceType',
            fields=[
                ('type', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('latest_version', models.CharField(max_length=16)),
            ],
        ),
        migrations.AddField(
            model_name='device',
            name='type',
            field=models.CharField(default='06', max_length=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='device',
            name='version',
            field=models.CharField(default='1.0.1', max_length=16),
            preserve_default=False,
        ),
    ]