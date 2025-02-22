from django.urls import path
from ..views.tracking import (
    OrderTrackingView,
    UpdateDeliveryStatusView,
    ToggleTrackingView,
    UpdateLocationView
)

app_name = 'tracking'

urlpatterns = [
    path('order/<int:order_id>/', OrderTrackingView.as_view(), name='order'),
    path('order/<int:order_id>/status/', UpdateDeliveryStatusView.as_view(), name='update_status'),
    path('order/<int:order_id>/toggle/', ToggleTrackingView.as_view(), name='toggle'),
    path('location/update/', UpdateLocationView.as_view(), name='update_location'),
]
