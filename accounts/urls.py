from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('setup/', views.setup_view, name='setup'),  # Only one instance
    path('preview/', views.preview_view, name='preview'),
    path('delete/<int:contact_id>/', views.delete_account, name='delete_account'),
    path('update/<int:pk>/', views.update_account, name='update_account'),
    path('home/', views.home_view, name='home'),  
    path('download/accounts/', views.download_accounts_csv, name='download_accounts_csv'),
    path('download/request/', views.request_download, name='request_download'),
    path('download/approve/<uuid:token>/', views.approve_download, name='approve_download'),
    path('download/reject/<uuid:token>/', views.reject_download, name='reject_download'),
    path('delete_all/', views.delete_all_accounts, name='delete_all_accounts'),
]