# Generated by Django 5.1.7 on 2025-06-24 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountrecord',
            name='account_id',
            field=models.CharField(blank=True, db_column='Account_Id', max_length=98, null=True),
        ),
        migrations.AlterField(
            model_name='accountrecord',
            name='account_name',
            field=models.CharField(db_column='Account_Name', max_length=400),
        ),
    ]
