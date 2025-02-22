from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
from decimal import Decimal
import django.core.validators

class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('marketplace', '0010_add_user_management'),
    ]

    operations = [
        migrations.CreateModel(
            name='DriverLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(
                    decimal_places=6,
                    help_text='Latitude coordinate',
                    max_digits=9,
                    validators=[
                        django.core.validators.MinValueValidator(Decimal('-90')),
                        django.core.validators.MaxValueValidator(Decimal('90'))
                    ]
                )),
                ('longitude', models.DecimalField(
                    decimal_places=6,
                    help_text='Longitude coordinate',
                    max_digits=9,
                    validators=[
                        django.core.validators.MinValueValidator(Decimal('-180')),
                        django.core.validators.MaxValueValidator(Decimal('180'))
                    ]
                )),
                ('accuracy', models.FloatField(
                    blank=True,
                    help_text='Location accuracy in meters',
                    null=True
                )),
                ('tracking_status', models.CharField(
                    choices=[
                        ('enabled', 'Enabled'),
                        ('paused', 'Paused'),
                        ('disabled', 'Disabled')
                    ],
                    default='disabled',
                    help_text='Current tracking status',
                    max_length=20
                )),
                ('last_update', models.DateTimeField(
                    auto_now=True,
                    help_text='When location was last updated'
                )),
                ('driver', models.ForeignKey(
                    help_text='Driver being tracked',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='locations',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Driver Location',
                'verbose_name_plural': 'Driver Locations',
                'ordering': ['-last_update'],
            },
        ),
        migrations.CreateModel(
            name='DeliveryStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(
                    choices=[
                        ('assigned', 'Assigned to Driver'),
                        ('pickup', 'At Pickup Location'),
                        ('in_transit', 'In Transit'),
                        ('nearby', 'Nearby Delivery Location'),
                        ('arrived', 'Arrived at Delivery Location'),
                        ('completed', 'Delivery Completed'),
                        ('failed', 'Delivery Failed')
                    ],
                    help_text='Current delivery status',
                    max_length=20
                )),
                ('notes', models.TextField(
                    blank=True,
                    help_text='Additional status notes'
                )),
                ('latitude', models.DecimalField(
                    blank=True,
                    decimal_places=6,
                    help_text='Optional latitude coordinate',
                    max_digits=9,
                    null=True,
                    validators=[
                        django.core.validators.MinValueValidator(Decimal('-90')),
                        django.core.validators.MaxValueValidator(Decimal('90'))
                    ]
                )),
                ('longitude', models.DecimalField(
                    blank=True,
                    decimal_places=6,
                    help_text='Optional longitude coordinate',
                    max_digits=9,
                    null=True,
                    validators=[
                        django.core.validators.MinValueValidator(Decimal('-180')),
                        django.core.validators.MaxValueValidator(Decimal('180'))
                    ]
                )),
                ('created_at', models.DateTimeField(
                    auto_now_add=True,
                    help_text='When status was created'
                )),
                ('driver', models.ForeignKey(
                    help_text='Driver making the delivery',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='status_updates',
                    to=settings.AUTH_USER_MODEL
                )),
                ('order', models.ForeignKey(
                    help_text='Order being delivered',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='status_updates',
                    to='marketplace.deliveryorder'
                )),
            ],
            options={
                'verbose_name': 'Delivery Status',
                'verbose_name_plural': 'Delivery Statuses',
                'ordering': ['-created_at'],
            },
        ),
    ]
