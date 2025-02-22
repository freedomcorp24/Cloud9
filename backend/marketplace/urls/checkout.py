from django.urls import path
from ..views.checkout import CheckoutView, PINVerificationView, DeliveryDetailsView

app_name = 'checkout'

urlpatterns = [
    path('', CheckoutView.as_view(), name='index'),
    path('verify-pin/', PINVerificationView.as_view(), name='verify_pin'),
    path('delivery-details/', DeliveryDetailsView.as_view(), name='delivery_details'),
]
