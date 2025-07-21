# accounts/utils.py

from accounts.models import UserRegion  # ✅ Fix: Import UserRegion

def get_user_allowed_regions(user):
    try:
        user_region = UserRegion.objects.get(account_owner_name=user.get_full_name())
        return [r.strip().title() for r in user_region.regions.split(',')]
    except UserRegion.DoesNotExist:
        return []
