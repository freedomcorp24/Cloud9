from django.db import migrations, models
import django.db.models.deletion
import django.core.validators

class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0003_add_vendor_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductListing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=100)),
                ('origin_country', models.CharField(max_length=100)),
                ('escrow_enabled', models.BooleanField(default=True)),
                ('fe_enabled', models.BooleanField(default=False)),
                ('accept_btc', models.BooleanField(default=True)),
                ('accept_xmr', models.BooleanField(default=True)),
                ('accept_usdt', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('refund_policy', models.TextField()),
                ('tags', models.CharField(max_length=500)),
                ('auto_message', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('available_quantity', models.IntegerField(default=1)),
                ('unlimited_quantity', models.BooleanField(default=False)),
                ('bulk_pricing', models.JSONField(blank=True, null=True)),
                ('main_image', models.ImageField(upload_to='product_images/')),
                ('image_2', models.ImageField(blank=True, null=True, upload_to='product_images/')),
                ('image_3', models.ImageField(blank=True, null=True, upload_to='product_images/')),
                ('image_4', models.ImageField(blank=True, null=True, upload_to='product_images/')),
                ('image_5', models.ImageField(blank=True, null=True, upload_to='product_images/')),
                ('image_6', models.ImageField(blank=True, null=True, upload_to='product_images/')),
                ('ships_to', models.CharField(max_length=500)),
                ('visibility', models.CharField(choices=[('public', 'Public'), ('private', 'Private'), ('hidden', 'Hidden')], default='public', max_length=20)),
                ('restrict_buyers', models.BooleanField(default=False)),
                ('cancel_hours', models.IntegerField(help_text='Hours until buyer can cancel if not accepted', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(95)])),
                ('auto_cancel_hours', models.IntegerField(help_text='Hours until pending sale auto-cancels', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(96)])),
                ('auto_finalize_days', models.IntegerField(help_text='Days until shipped sale auto-finalizes', validators=[django.core.validators.MinValueValidator(7), django.core.validators.MaxValueValidator(90)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.vendorprofile')),
            ],
            options={
                'verbose_name': 'Product Listing',
                'verbose_name_plural': 'Product Listings',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PostageOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.productlisting')),
            ],
            options={
                'verbose_name': 'Postage Option',
                'verbose_name_plural': 'Postage Options',
            },
        ),
    ]
