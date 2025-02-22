from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
from decimal import Decimal

class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('marketplace', '0009_add_marketplace_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='status',
            field=models.CharField(
                choices=[
                    ('active', 'Active'),
                    ('frozen', 'Frozen'),
                    ('suspended', 'Suspended'),
                    ('banned', 'Banned')
                ],
                default='active',
                help_text='Account status',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='status_reason',
            field=models.TextField(
                blank=True,
                help_text='Reason for current status'
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='frozen_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Admin who froze the account',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='accounts_frozen',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='frozen_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the account was frozen',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='daily_transaction_count',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Number of transactions in last 24 hours'
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='daily_transaction_volume',
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0'),
                help_text='Total transaction volume in last 24 hours',
                max_digits=12
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_transaction_reset',
            field=models.DateTimeField(
                auto_now_add=True,
                help_text='When daily transaction counters were last reset'
            ),
        ),
    ]
