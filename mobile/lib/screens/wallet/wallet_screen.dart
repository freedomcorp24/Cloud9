import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/wallet.dart';
import '../../services/api_service.dart';

class WalletScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: Text('Wallet'),
          bottom: TabBar(
            tabs: [
              Tab(text: 'BTC'),
              Tab(text: 'XMR'),
              Tab(text: 'USDT'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            WalletTab(currency: 'BTC'),
            WalletTab(currency: 'XMR'),
            WalletTab(currency: 'USDT'),
          ],
        ),
      ),
    );
  }
}

class WalletTab extends StatelessWidget {
  final String currency;

  const WalletTab({Key? key, required this.currency}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<ApiService>(
      builder: (context, apiService, child) {
        return FutureBuilder<Wallet>(
          future: apiService.getWallet(currency),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return Center(child: CircularProgressIndicator());
            }

            if (snapshot.hasError) {
              return Center(
                child: Text('Error loading wallet: ${snapshot.error}'),
              );
            }

            final wallet = snapshot.data!;
            return SingleChildScrollView(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Card(
                      child: Padding(
                        padding: EdgeInsets.all(16),
                        child: Column(
                          children: [
                            Text(
                              'Balance',
                              style: Theme.of(context).textTheme.titleMedium,
                            ),
                            SizedBox(height: 8),
                            Text(
                              '${wallet.balance} ${wallet.currency}',
                              style: Theme.of(context).textTheme.headlineMedium,
                            ),
                          ],
                        ),
                      ),
                    ),
                    SizedBox(height: 24),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        ElevatedButton.icon(
                          icon: Icon(Icons.call_received),
                          label: Text('Deposit'),
                          onPressed: () => _showDepositDialog(context, wallet),
                        ),
                        ElevatedButton.icon(
                          icon: Icon(Icons.call_made),
                          label: Text('Withdraw'),
                          onPressed: () => _showWithdrawDialog(context, wallet),
                        ),
                      ],
                    ),
                    SizedBox(height: 24),
                    Text(
                      'Transaction History',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    SizedBox(height: 8),
                    ListView.builder(
                      shrinkWrap: true,
                      physics: NeverScrollableScrollPhysics(),
                      itemCount: wallet.transactions.length,
                      itemBuilder: (context, index) {
                        final transaction = wallet.transactions[index];
                        return TransactionListItem(transaction: transaction);
                      },
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  void _showDepositDialog(BuildContext context, Wallet wallet) async {
    final apiService = Provider.of<ApiService>(context, listen: false);
    final address = await apiService.generateDepositAddress(currency);
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Deposit Address'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Send funds to this address:'),
            SizedBox(height: 8),
            SelectableText(address),
            SizedBox(height: 16),
            Text(
              'Address expires in 2 hours',
              style: TextStyle(color: Colors.red),
            ),
          ],
        ),
        actions: [
          TextButton(
            child: Text('Close'),
            onPressed: () => Navigator.pop(context),
          ),
        ],
      ),
    );
  }

  void _showWithdrawDialog(BuildContext context, Wallet wallet) {
    final addressController = TextEditingController();
    final amountController = TextEditingController();
    final formKey = GlobalKey<FormState>();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Withdraw'),
        content: Form(
          key: formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: addressController,
                decoration: InputDecoration(
                  labelText: 'Address',
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter an address';
                  }
                  return null;
                },
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: amountController,
                decoration: InputDecoration(
                  labelText: 'Amount',
                  suffixText: currency,
                ),
                keyboardType: TextInputType.numberWithOptions(decimal: true),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter an amount';
                  }
                  final amount = double.tryParse(value);
                  if (amount == null || amount <= 0) {
                    return 'Please enter a valid amount';
                  }
                  if (amount > wallet.balance) {
                    return 'Insufficient funds';
                  }
                  return null;
                },
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            child: Text('Cancel'),
            onPressed: () => Navigator.pop(context),
          ),
          TextButton(
            child: Text('Withdraw'),
            onPressed: () async {
              if (formKey.currentState!.validate()) {
                try {
                  final apiService = Provider.of<ApiService>(
                    context,
                    listen: false,
                  );
                  await apiService.withdraw(
                    currency: currency,
                    amount: double.parse(amountController.text),
                    address: addressController.text,
                  );
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Withdrawal initiated')),
                  );
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error: $e')),
                  );
                }
              }
            },
          ),
        ],
      ),
    );
  }
}

class TransactionListItem extends StatelessWidget {
  final Transaction transaction;

  const TransactionListItem({Key? key, required this.transaction})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(
        transaction.type == 'deposit'
            ? Icons.call_received
            : Icons.call_made,
        color: transaction.type == 'deposit'
            ? Colors.green
            : Colors.red,
      ),
      title: Text(transaction.type.toUpperCase()),
      subtitle: Text(
        transaction.timestamp.toString(),
      ),
      trailing: Text(
        '${transaction.type == 'deposit' ? '+' : '-'}${transaction.amount} ${transaction.currency}',
        style: TextStyle(
          color: transaction.type == 'deposit'
              ? Colors.green
              : Colors.red,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}
