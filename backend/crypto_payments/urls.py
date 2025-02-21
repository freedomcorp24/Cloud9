from django.urls import path
from .views import (
    payment_dashboard,
    batch_detail,
    user_payment_history,
    admin_action_log,
    deposit_address
)

app_name = 'crypto_payments'

urlpatterns = [
    path('dashboard/', payment_dashboard, name='dashboard'),
    path('batch/<int:pk>/', batch_detail, name='batch_detail'),
    path('history/<int:user_id>/', user_payment_history, name='user_history'),
    path('actions/', admin_action_log, name='action_log'),
    path('deposit/<int:pk>/', deposit_address, name='deposit_address'),
]
