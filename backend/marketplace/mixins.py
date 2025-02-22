from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.base import ContextMixin
from typing import Optional, Any, cast
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import AbstractUser

class CategoryPermissionMixin(UserPassesTestMixin, ContextMixin):
    """Ensures only master admin can manage categories."""
    
    request: HttpRequest
    object: Optional[Any] = None
    
    def test_func(self) -> bool:
        """Check if user is a superuser (master admin)."""
        user = cast(AbstractUser, self.request.user)
        return user.is_superuser
    
    def handle_no_permission(self) -> HttpResponse:
        """Handle unauthorized access attempts."""
        messages.error(self.request, "Only master admin can manage categories.")
        return redirect(reverse('dashboard:catalogue-category-list'))

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Add user to instance for audit logging."""
        response = super().dispatch(request, *args, **kwargs)
        if self.object is not None:
            setattr(self.object, '_current_user', request.user)
        return response
