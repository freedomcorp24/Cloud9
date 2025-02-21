from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r'ws/delivery/(?P<order_id>\w+)/$',
        consumers.LocationConsumer.as_asgi(),
        name='delivery_tracking'
    ),
]
