from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

class CategoryPermissionMixin(UserPassesTestMixin):
    """Ensures only master admin can manage categories."""
    
    def test_func(self):
        """Check if user is a superuser (master admin)."""
        # UserPassesTestMixin provides self.request
        if not hasattr(self, 'request'):
            return False
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        """Handle unauthorized access attempts."""
        if hasattr(self, 'request'):
            messages.error(self.request, "Only master admin can manage categories.")
            return redirect(reverse('dashboard:catalogue-category-list'))
        return super().handle_no_permission()

    def dispatch(self, request, *args, **kwargs):
        """Add user to instance for audit logging."""
        response = super().dispatch(request, *args, **kwargs)
        if hasattr(self, 'object') and self.object is not None:
            setattr(self.object, '_current_user', request.user)
        return response
