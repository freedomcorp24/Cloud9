from django.db import migrations, models
import django.core.validators
import django.utils.timezone

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0004_productattributevalue_productcategory_productlisting_and_more'),
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
                validators=[
                    django.core.validators.MinLengthValidator(3),
                    django.core.validators.RegexValidator(
                        message='Username can only contain letters, numbers, underscores and hyphens',
                        regex='^[a-zA-Z0-9_-]+$'
                    )
                ]
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='private_username',
            field=models.CharField(
                default='',
                help_text='Private username used for login',
                max_length=30,
                unique=True,
                validators=[
                    django.core.validators.MinLengthValidator(8),
                    django.core.validators.RegexValidator(
                        message='Username can only contain letters, numbers, underscores and hyphens',
                        regex='^[a-zA-Z0-9_-]+$'
                    )
                ]
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='pgp_verification_code',
            field=models.CharField(
                blank=True,
                help_text='Temporary code for PGP key verification',
                max_length=64
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='pgp_verification_expires',
            field=models.DateTimeField(
                blank=True,
                help_text='Expiration time for PGP verification code',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='failed_pin_attempts',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Count of consecutive failed PIN attempts'
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='pin_locked_until',
            field=models.DateTimeField(
                blank=True,
                help_text='Timestamp until PIN entry is locked',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_active',
            field=models.DateTimeField(
                auto_now=True,
                help_text='Last activity timestamp'
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_login_ip',
            field=models.GenericIPAddressField(
                blank=True,
                help_text='IP address of last login',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='pgp_key',
            field=models.TextField(
                blank=True,
                help_text='PGP public key for 2FA and secure communications'
            ),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='pgp_verified',
            field=models.BooleanField(
                default=False,
                help_text='Indicates if PGP key ownership has been verified'
            ),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='transaction_pin',
            field=models.CharField(
                help_text='6-digit PIN required for financial operations',
                max_length=6,
                validators=[
                    django.core.validators.MinLengthValidator(6),
                    django.core.validators.RegexValidator(
                        message='PIN must be exactly 6 digits',
                        regex='^\\d{6}$'
                    )
                ]
            ),
        ),
    ]
