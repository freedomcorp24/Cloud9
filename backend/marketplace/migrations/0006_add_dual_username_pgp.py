from django.db import migrations, models
import django.utils.timezone
from ..models.user_profile import validate_username

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0005_user_profile_enhancements'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='public_username',
            field=models.CharField(
                default='',
                help_text='Public username visible to other users',
                max_length=30,
                unique=True,
                validators=[validate_username],
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='private_username',
            field=models.CharField(
                default='',
                help_text='Private username for login',
                max_length=30,
                unique=True,
                validators=[validate_username],
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='pgp_key',
            field=models.TextField(
                blank=True,
                help_text='PGP public key for 2FA'
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='pgp_key_fingerprint',
            field=models.CharField(
                blank=True,
                help_text='Fingerprint of PGP public key',
                max_length=40
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='pgp_enabled',
            field=models.BooleanField(
                default=False,
                help_text='Whether PGP 2FA is enabled'
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='pgp_verification_code',
            field=models.CharField(
                blank=True,
                help_text='Temporary code for PGP key verification',
                max_length=32,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='pgp_verification_expires_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Expiration time for PGP verification code',
                null=True
            ),
        ),
    ]
