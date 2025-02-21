from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('crypto_payments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('frozen', 'Frozen')], default='pending', max_length=20)),
                ('total_amount', models.DecimalField(decimal_places=8, default=0, max_digits=18)),
                ('transaction_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'verbose_name': 'Payment Batch',
                'verbose_name_plural': 'Payment Batches',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BatchTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crypto_payments.paymentbatch')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crypto_payments.cryptotransaction')),
            ],
            options={
                'verbose_name': 'Batch Transaction',
                'verbose_name_plural': 'Batch Transactions',
                'unique_together': {('batch', 'transaction')},
            },
        ),
        migrations.CreateModel(
            name='AdminAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('freeze_wallet', 'Freeze Wallet'), ('unfreeze_wallet', 'Unfreeze Wallet'), ('freeze_batch', 'Freeze Payment Batch'), ('unfreeze_batch', 'Unfreeze Payment Batch'), ('approve_withdrawal', 'Approve Withdrawal'), ('reject_withdrawal', 'Reject Withdrawal'), ('blacklist_address', 'Blacklist Address'), ('other', 'Other Action')], max_length=50)),
                ('target_type', models.CharField(max_length=50)),
                ('target_id', models.IntegerField()),
                ('details', models.JSONField(default=dict)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('admin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'verbose_name': 'Admin Action',
                'verbose_name_plural': 'Admin Actions',
                'ordering': ['-timestamp'],
            },
        ),
    ]
