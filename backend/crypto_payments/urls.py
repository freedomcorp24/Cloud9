from django.urls import path
from .views import (
    DepositAddressCreateView,
    DepositAddressDetailView
)

app_name = 'crypto_payments'

urlpatterns = [
    path(
        'deposit/create/',
        DepositAddressCreateView.as_view(),
        name='deposit_address_create'
    ),
    path(
        'deposit/<int:pk>/',
        DepositAddressDetailView.as_view(),
        name='deposit_address_detail'
    ),
]
