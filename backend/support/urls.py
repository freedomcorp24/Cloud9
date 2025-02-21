from django.urls import path
from .views import (
    SupportDashboardView,
    TicketCreateView,
    TicketDetailView,
    TicketMessageCreateView,
    BondWaiverRequestView
)

app_name = 'support'

urlpatterns = [
    path('', SupportDashboardView.as_view(), name='dashboard'),
    path('ticket/new/', TicketCreateView.as_view(), name='ticket_create'),
    path('ticket/<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),
    path(
        'ticket/<int:ticket_pk>/message/',
        TicketMessageCreateView.as_view(),
        name='message_create'
    ),
    path(
        'bond-waiver/',
        BondWaiverRequestView.as_view(),
        name='bond_waiver_request'
    ),
]
