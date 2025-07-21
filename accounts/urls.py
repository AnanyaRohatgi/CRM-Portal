from django.urls import path, include
from django.conf import settings
from . import views
from accounts.views import no_access_view

urlpatterns = [
    # Auth
    path('', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Setup and Home
    path('setup/', views.setup_view, name='setup'),
    path('setup-accounts/', views.setup_accounts_view, name='setup-accounts'),
    path('home/', views.home_view, name='home'),


    # Account Management
    path('preview/', views.preview_view, name='preview'),
    path('preview-accounts/', views.accounts_preview_view, name='preview-accounts'),
    path('update/<int:pk>/', views.update_account, name='update_account'),
    path('no-access/', no_access_view, name='no_access'),
    
   
    # Clear separation between account and record deletion
    path('delete-account/<str:account_id>/', views.delete_account, name='delete_account'),
    path('delete-record/<str:contact_id>/', views.delete_account_record, name='delete_account_record'),
    path('delete-all/', views.delete_all_accounts, name='delete_all_accounts'),
    path('contacts-for-account/<path:account_name>/', views.contacts_for_account, name='contacts_for_account'),

    # Download Requests
    path('download/accounts/', views.download_accounts_csv, name='download_accounts_csv'),
    path('download/request/', views.request_download, name='request_download'),
    path('download/approve/<uuid:request_id>/', views.approve_download, name='approve_download'),
    path('download/reject/<uuid:request_id>/', views.reject_download, name='reject_download'),
    path('download/contacts/', views.download_accounts_csv, name='download_contacts_csv'),
    path('download/contacts-for-account/', views.download_accounts_csv, name='download_contacts_for_account_csv'),


    # AJAX Endpoints (grouped together)
    path('api/', include([
        path('filter-options/', views.get_filter_options_ajax, name='filter_options_ajax'),
        path('get-account/', views.get_account_by_name, name='get_account_by_name'),
        path('get-account-record/', views.get_account_record_details, name='get_account_record_details'),
        path('autocomplete-contacts/', views.autocomplete_contacts, name='autocomplete_contacts'),
        path('autocomplete-accounts/', views.autocomplete_accounts, name='autocomplete_accounts'),
        path('search-contacts/', views.search_contacts, name='search_contacts'),
        path('search-accounts/', views.search_accounts, name='search_accounts'),
        

    ])),
    
    # Record updates
    path('update-record/<int:pk>/', views.update_account_record, name='update_account_record'),
    path('no-access/', no_access_view, name='no_access'),
]

# # Debug Toolbar URLs (only in development)
# if settings.DEBUG:
#     import debug_toolbar  # Import moved inside the DEBUG block
#     urlpatterns = [
#         path('__debug__/', include(debug_toolbar.urls)),
#     ] + urlpatterns