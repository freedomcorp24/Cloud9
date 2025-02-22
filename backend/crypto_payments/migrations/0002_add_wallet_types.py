from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('crypto_payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cryptowallet',
            name='wallet_type',
            field=models.CharField(
                choices=[
                    ('hot', 'Hot Wallet'),
                    ('cold', 'Cold Storage'),
                    ('deposit', 'Deposit Address'),
                    ('withdrawal', 'Withdrawal Address')
                ],
                default='deposit',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='cryptowallet',
            name='hot_wallet_threshold',
            field=models.DecimalField(
                blank=True,
                decimal_places=8,
                help_text='Maximum amount to keep in hot wallet',
                max_digits=18,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='cryptowallet',
            name='last_rebalance',
            field=models.DateTimeField(
                blank=True,
                null=True
            ),
        ),
        migrations.AddIndex(
            model_name='cryptowallet',
            index=models.Index(
                fields=['wallet_type', 'currency_type'],
                name='crypto_wallet_type_currency_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='cryptowallet',
            index=models.Index(
                fields=['address'],
                name='crypto_wallet_address_idx'
            ),
        ),
    ]
