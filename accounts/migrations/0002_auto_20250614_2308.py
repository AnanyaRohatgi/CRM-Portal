from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DownloadRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4, unique=True, editable=False)),
                ('requested_by', models.EmailField(max_length=254)),
                ('status', models.CharField(
                    max_length=10,
                    choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                    default='pending'
                )),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
