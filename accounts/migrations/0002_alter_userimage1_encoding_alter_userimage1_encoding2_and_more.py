# Generated by Django 4.2.7 on 2023-12-20 11:32

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userimage1',
            name='encoding',
            field=models.CharField(),
        ),
        migrations.AlterField(
            model_name='userimage1',
            name='encoding2',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='userimage1',
            name='image',
            field=models.ImageField(upload_to=accounts.models.user_directory_path),
        ),
        migrations.AlterModelTable(
            name='userimage1',
            table='accounts_userimage1',
        ),
    ]
