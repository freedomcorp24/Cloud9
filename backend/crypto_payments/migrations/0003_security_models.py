from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('crypto_payments', '0002_add_wallet_types'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecurityThreshold',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('threshold_type', models.CharField(choices=[('withdrawal_daily', 'Daily Withdrawal Limit'), ('withdrawal_monthly', 'Monthly Withdrawal Limit'), ('hot_wallet_max', 'Hot Wallet Maximum'), ('suspicious_amount', 'Suspicious Transaction Amount'), ('max_failed_attempts', 'Maximum Failed Attempts'), ('address_risk_score', 'Address Risk Score Threshold')], max_length=50, unique=True)),
                ('value', models.DecimalField(decimal_places=8, max_digits=18)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='security_thresholds', to='auth.user')),
            ],
            options={
                'verbose_name': 'Security Threshold',
                'verbose_name_plural': 'Security Thresholds',
            },
        ),
        migrations.CreateModel(
            name='AccountFreeze',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('freeze_type', models.CharField(choices=[('automated', 'Automated Freeze'), ('manual', 'Manual Admin Freeze'), ('suspicious', 'Suspicious Activity')], max_length=20)),
                ('reason', models.TextField()),
                ('status', models.CharField(choices=[('active', 'Active'), ('expired', 'Expired'), ('lifted', 'Manually Lifted')], default='active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('lifted_at', models.DateTimeField(blank=True, null=True)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='freezes', to='crypto_payments.cryptowallet')),
                ('lifted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lifted_freezes', to='auth.user')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_freezes', to='auth.user')),
            ],
            options={
                'verbose_name': 'Account Freeze',
                'verbose_name_plural': 'Account Freezes',
            },
        ),
        migrations.CreateModel(
            name='WithdrawalAutomation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency_type', models.CharField(max_length=10)),
                ('automation_type', models.CharField(choices=[('instant', 'Instant Processing'), ('scheduled', 'Scheduled Processing'), ('manual', 'Manual Review Required')], max_length=20)),
                ('min_amount', models.DecimalField(decimal_places=8, help_text='Minimum amount for this automation rule', max_digits=18)),
                ('max_amount', models.DecimalField(decimal_places=8, help_text='Maximum amount for this automation rule', max_digits=18)),
                ('is_active', models.BooleanField(default=True)),
                ('requires_2fa', models.BooleanField(default=True, help_text='Require 2FA verification for automated withdrawals')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Withdrawal Automation',
                'verbose_name_plural': 'Withdrawal Automations',
                'unique_together': {('currency_type', 'automation_type')},
            },
        ),
    ]
