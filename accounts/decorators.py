# decorators.py
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect
from functools import wraps

def staff_approved_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        print(f"🔍 Decorator called for user: {request.user.username}")
        print(f"🔍 User is_staff: {request.user.is_staff}")
        print(f"🔍 User is_authenticated: {request.user.is_authenticated}")
        
        if not request.user.is_authenticated:
            print("❌ User not authenticated, redirecting to login")
            return redirect('login')
        
        # Check if user has staff status (approved)
        if not request.user.is_staff:
            print("❌ User not staff, blocking delete operation")
            messages.error(request, "You don't have permission to perform delete operations. Your staff status is not approved.")
            return redirect('preview')
        
        print("✅ User has staff status, allowing delete operation")
        return view_func(request, *args, **kwargs)
    return _wrapped_view