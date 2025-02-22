from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0011_add_driver_tracking'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryorder',
            name='actual_delivery',
            field=models.DateTimeField(
                blank=True,
                help_text='When order was actually delivered',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='deliveryorder',
            name='estimated_delivery',
            field=models.DateTimeField(
                blank=True,
                help_text='Estimated delivery time',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='deliveryorder',
            name='pickup_latitude',
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                help_text='Pickup location latitude',
                max_digits=9,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='deliveryorder',
            name='pickup_longitude',
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                help_text='Pickup location longitude',
                max_digits=9,
                null=True
            ),
        ),
    ]
