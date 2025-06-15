from django.contrib import admin
from django.urls import path, include
from accounts.views import login_view  # import the login view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='home'),
    path('login/', login_view, name='login'),
    path('', include('accounts.urls')),  # now all accounts paths are direct
    path('setup/', include('accounts.urls')),
]