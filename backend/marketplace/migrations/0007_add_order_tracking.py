from django.db import migrations, models
import django.core.validators
from decimal import Decimal
from django.utils.translation import gettext_lazy as _

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0006_add_dual_username_pgp'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryorder',
            name='enable_real_time_tracking',
            field=models.BooleanField(
                default=False,
                help_text=_('Enable real-time location tracking for this delivery')
            ),
        ),
        migrations.AddField(
            model_name='deliveryorder',
            name='driver_location_permission',
            field=models.BooleanField(
                default=False,
                help_text=_('Driver has granted permission for location tracking')
            ),
        ),
        migrations.AddField(
            model_name='deliveryorder',
            name='last_location_update',
            field=models.DateTimeField(
                null=True,
                blank=True,
                help_text=_('Timestamp of last location update')
            ),
        ),
        migrations.AddField(
            model_name='deliverytracking',
            name='is_manual_update',
            field=models.BooleanField(
                default=True,
                help_text=_('Whether this is a manual status update vs real-time tracking')
            ),
        ),
        migrations.AddField(
            model_name='deliverytracking',
            name='driver_notes',
            field=models.TextField(
                blank=True,
                help_text=_('Additional notes from driver for manual updates')
            ),
        ),
        migrations.AlterField(
            model_name='deliverytracking',
            name='order',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='tracking_updates',
                to='marketplace.deliveryorder'
            ),
        ),
    ]
