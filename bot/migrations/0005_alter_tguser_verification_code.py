# Generated by Django 4.2.2 on 2023-07-26 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0004_alter_tguser_verification_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tguser',
            name='verification_code',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]
