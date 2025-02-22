from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
from decimal import Decimal
import django.core.validators
from django.utils import timezone

class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('marketplace', '0007_add_order_tracking'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bond_paid', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Amount of vendor bond paid', max_digits=10)),
                ('bond_required', models.DecimalField(decimal_places=2, default=Decimal('500.00'), help_text='Required bond amount', max_digits=10)),
                ('bond_waived', models.BooleanField(default=False, help_text='Whether bond requirement has been waived by admin')),
                ('status', models.CharField(choices=[('pending', 'Pending Bond'), ('active', 'Active'), ('suspended', 'Suspended'), ('banned', 'Banned')], default='pending', max_length=20)),
                ('rating', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=3, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('total_ratings', models.PositiveIntegerField(default=0)),
                ('can_finalize_early', models.BooleanField(default=False, help_text='Permission to finalize orders early')),
                ('finalize_early_threshold', models.DecimalField(decimal_places=2, default=Decimal('4.50'), help_text='Rating threshold for automatic finalize early permission', max_digits=3)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_active', models.DateTimeField(default=timezone.now)),
                ('bond_waived_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bond_waivers_granted', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Vendor Profile',
                'verbose_name_plural': 'Vendor Profiles',
            },
        ),
    ]
