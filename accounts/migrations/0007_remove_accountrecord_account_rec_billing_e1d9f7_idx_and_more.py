# Generated by Django 5.2.4 on 2025-07-04 07:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_remove_account_mailing_city_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='accountrecord',
            name='account_rec_Billing_e1d9f7_idx',
        ),
        migrations.RemoveField(
            model_name='accountrecord',
            name='billing_city',
        ),
        migrations.RemoveField(
            model_name='accountrecord',
            name='billing_country',
        ),
        migrations.RemoveField(
            model_name='accountrecord',
            name='billing_postal_code',
        ),
        migrations.RemoveField(
            model_name='accountrecord',
            name='billing_state',
        ),
        migrations.RemoveField(
            model_name='accountrecord',
            name='billing_street',
        ),
        migrations.RemoveField(
            model_name='accountrecord',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='accountrecord',
            name='website',
        ),
        migrations.AddField(
            model_name='accountrecord',
            name='city',
            field=models.CharField(blank=True, db_column='City', max_length=100, null=True, verbose_name='City'),
        ),
        migrations.AddField(
            model_name='accountrecord',
            name='country',
            field=models.CharField(blank=True, db_column='Country', max_length=100, null=True, verbose_name='Country'),
        ),
        migrations.AddField(
            model_name='accountrecord',
            name='state',
            field=models.CharField(blank=True, db_column='State', max_length=100, null=True, verbose_name='State'),
        ),
        migrations.AlterField(
            model_name='account',
            name='account_name',
            field=models.TextField(blank=True, db_column='Account_Name', null=True, verbose_name='Account Name'),
        ),
        migrations.AlterField(
            model_name='account',
            name='account_owner',
            field=models.CharField(blank=True, db_column='Account Owner', max_length=100, null=True, verbose_name='Account Owner'),
        ),
        migrations.AlterField(
            model_name='account',
            name='city',
            field=models.CharField(blank=True, db_column='City', max_length=100, null=True, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='account',
            name='country',
            field=models.CharField(blank=True, db_column='Country', max_length=100, null=True, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='account',
            name='created_by_id',
            field=models.CharField(blank=True, db_column='CreatedById', max_length=18, null=True, verbose_name='Created by Name'),
        ),
        migrations.AlterField(
            model_name='account',
            name='created_date',
            field=models.DateField(blank=True, db_column='CreatedDate', null=True, verbose_name='Created Date Timestamp'),
        ),
        migrations.AlterField(
            model_name='account',
            name='department',
            field=models.CharField(blank=True, db_column='Department', max_length=100, null=True, verbose_name='Department'),
        ),
        migrations.AlterField(
            model_name='account',
            name='email',
            field=models.CharField(blank=True, db_column='Email', max_length=200, null=True, verbose_name='Email ID'),
        ),
        migrations.AlterField(
            model_name='account',
            name='industry',
            field=models.CharField(blank=True, db_column='Industry', max_length=100, null=True, verbose_name='Industry'),
        ),
        migrations.AlterField(
            model_name='account',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last Modified Timestamp'),
        ),
        migrations.AlterField(
            model_name='account',
            name='last_modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='account_last_modified', to=settings.AUTH_USER_MODEL, verbose_name='Last Modified by Name'),
        ),
        migrations.AlterField(
            model_name='account',
            name='mobile',
            field=models.TextField(blank=True, db_column='MobilePhone', null=True, verbose_name='Mobile Phone'),
        ),
        migrations.AlterField(
            model_name='account',
            name='organization_level',
            field=models.CharField(blank=True, db_column='OrganizationLevel', max_length=100, null=True, verbose_name='Organisational Level'),
        ),
        migrations.AlterField(
            model_name='account',
            name='other_phone',
            field=models.TextField(blank=True, db_column='OtherPhone', null=True, verbose_name='Alternate Phone'),
        ),
        migrations.AlterField(
            model_name='account',
            name='region',
            field=models.CharField(db_column='REGION', max_length=20, verbose_name='Region'),
        ),
        migrations.AlterField(
            model_name='account',
            name='remarks',
            field=models.TextField(blank=True, db_column='Remarks', null=True, verbose_name='Remarks'),
        ),
        migrations.AlterField(
            model_name='account',
            name='state',
            field=models.CharField(blank=True, db_column='State', max_length=100, null=True, verbose_name='State'),
        ),
        migrations.AlterField(
            model_name='account',
            name='title',
            field=models.TextField(blank=True, db_column='Title', null=True, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='account',
            name='zone',
            field=models.CharField(blank=True, db_column='Zone', max_length=50, null=True, verbose_name='Zone'),
        ),
        migrations.AlterField(
            model_name='accountrecord',
            name='account_name',
            field=models.CharField(db_column='Account_Name', max_length=400, verbose_name='Account Name'),
        ),
        migrations.AlterField(
            model_name='accountrecord',
            name='account_owner',
            field=models.CharField(blank=True, db_column='Account Owner', max_length=100, null=True, verbose_name='Account Owner'),
        ),
        migrations.AlterField(
            model_name='accountrecord',
            name='created_by_id',
            field=models.CharField(blank=True, db_column='CreatedById', max_length=18, null=True, verbose_name='Created by Name'),
        ),
        migrations.AlterField(
            model_name='accountrecord',
            name='created_date',
            field=models.DateField(blank=True, db_column='CreatedDate', null=True, verbose_name='Created Date Timestamp'),
        ),
        migrations.AlterField(
            model_name='accountrecord',
            name='description',
            field=models.TextField(blank=True, db_column='Description', null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='accountrecord',
            name='industry',
            field=models.CharField(db_column='Industry', max_length=100, verbose_name='Industry'),
        ),
        migrations.AlterField(
            model_name='accountrecord',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last Modified Timestamp'),
        ),
        migrations.AlterField(
            model_name='accountrecord',
            name='last_modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='account_record_last_modified', to=settings.AUTH_USER_MODEL, verbose_name='Last Modified by Name'),
        ),
        migrations.AlterField(
            model_name='accountrecord',
            name='region',
            field=models.CharField(blank=True, db_column='REGION', max_length=100, null=True, verbose_name='Region'),
        ),
        migrations.AlterField(
            model_name='accountrecord',
            name='zone',
            field=models.CharField(blank=True, db_column='Zone', max_length=50, null=True, verbose_name='Zone'),
        ),
        migrations.AddIndex(
            model_name='accountrecord',
            index=models.Index(fields=['country'], name='account_rec_Country_b0ed37_idx'),
        ),
    ]
