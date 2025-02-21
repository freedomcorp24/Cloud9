from django.contrib import admin
from .models import SupportCategory, SupportTicket, TicketMessage

@admin.register(SupportCategory)
class SupportCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'requires_staff', 'auto_assign_to')
    list_filter = ('requires_staff',)
    search_fields = ('name', 'description')

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'user', 'category', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('subject', 'description', 'user__username')
    raw_id_fields = ('user', 'assigned_to')
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(category__requires_staff=False)

@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'message_type', 'created_at')
    list_filter = ('message_type', 'created_at')
    search_fields = ('message', 'user__username')
    raw_id_fields = ('ticket', 'user')
    date_hierarchy = 'created_at'
