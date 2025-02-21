from django.urls import path
from . import views
from .views.vendor import VendorDashboardView, VendorBondPaymentView
from .views.auth import CustomPasswordChangeView, TransactionPINView
from .views import delivery

app_name = 'marketplace'

urlpatterns = [
    # Delivery URLs
    path('delivery/<int:order_id>/tracking/', 
         delivery.tracking_view, 
         name='delivery-tracking'),
    path('delivery/<int:order_id>/status/', 
         delivery.update_status, 
         name='tor-delivery-status'),
    path('delivery/<int:order_id>/tracking-mode/',
         delivery.toggle_tracking_mode,
         name='toggle-tracking-mode'),
         
    # Vendor URLs
    path('vendor/dashboard/', 
         VendorDashboardView.as_view(), 
         name='vendor_dashboard'),
    path('vendor/bond/payment/', 
         VendorBondPaymentView.as_view(), 
         name='vendor_bond_payment'),
         
    # Auth URLs
    path('auth/change-pin/', 
         TransactionPINView.as_view(), 
         name='change_pin'),
    path('auth/change-password/', 
         CustomPasswordChangeView.as_view(), 
         name='change_password'),
         
    # Wallet URLs
    path('wallet/', 
         views.wallet.WalletDashboardView.as_view(), 
         name='wallet_dashboard'),
    path('wallet/deposit/<str:currency>/', 
         views.wallet.WalletDepositView.as_view(), 
         name='wallet_deposit'),
    path('wallet/withdraw/<str:currency>/', 
         views.wallet.WalletWithdrawView.as_view(), 
         name='wallet_withdraw'),
]
