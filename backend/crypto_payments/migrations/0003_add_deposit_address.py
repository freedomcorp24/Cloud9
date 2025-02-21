from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('crypto_payments', '0002_add_admin_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='DepositAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100, unique=True)),
                ('qr_code', models.ImageField(null=True, upload_to='qr_codes/')),
                ('status', models.CharField(choices=[('active', 'Active'), ('pending', 'Payment Pending'), ('completed', 'Completed'), ('expired', 'Expired')], default='active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('payment_detected_at', models.DateTimeField(null=True)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crypto_payments.cryptowallet')),
            ],
            options={
                'verbose_name': 'Deposit Address',
                'verbose_name_plural': 'Deposit Addresses',
                'ordering': ['-created_at'],
            },
        ),
    ]
