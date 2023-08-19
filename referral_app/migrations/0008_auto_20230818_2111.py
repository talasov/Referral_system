# Generated by Django 3.2 on 2023-08-18 18:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('referral_app', '0007_auto_20230818_2053'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='referred_by',
        ),
        migrations.AddField(
            model_name='customuser',
            name='referred_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referrals', to=settings.AUTH_USER_MODEL),
        ),
    ]