from django.core.management.base import BaseCommand
from accounts.models import UserRegion

class Command(BaseCommand):
    help = 'Populate UserRegion table with updated mappings from cleaned source'

    def handle(self, *args, **options):
        # Define raw mappings (clean and consistent)
        user_region_mappings = [
            # Singapore (SG) users
        {"name": "Richy Isaac", "alias": "richy", "regions": "Singapore", "is_super_admin": False},
        {"name": "Apoorva Johri", "alias": "apoorva", "regions": "Singapore", "is_super_admin": False},
        {"name": "Rohit Gupta", "alias": "rohit", "regions": "Singapore", "is_super_admin": False},
        {"name": "Shon Tang", "alias": "shon", "regions": "Singapore", "is_super_admin": False},
        {"name": "Ashish Singh", "alias": "asingh", "regions": "Singapore", "is_super_admin": False},
        {"name": "Chandan Roy", "alias": "croy", "regions": "Singapore,International", "is_super_admin": False},
        {"name": "Nikhil Chopra", "alias": "nchopra", "regions": "Singapore,International", "is_super_admin": False},
        
        # India (IND) users
        {"name": "Hitesh Gupta", "alias": "hgupta", "regions": "India,Singapore", "is_super_admin": False},
        {"name": "Vinay Sharma", "alias": "vsharma", "regions": "India", "is_super_admin": False},
        {"name": "Somya Shukla", "alias": "somya", "regions": "India", "is_super_admin": False},
        {"name": "Srishti Singh", "alias": "shristi", "regions": "India", "is_super_admin": False},
        {"name": "Ruchita Katkar", "alias": "ruchita", "regions": "India", "is_super_admin": False},
        {"name": "Sultana Shaikh", "alias": "sultana", "regions": "India", "is_super_admin": False},
        
        # International (INTL) users
        {"name": "Ashish Chopra", "alias": "achopra", "regions": "India,International", "is_super_admin": False},
        
        # Super Admins
        {"name": "Somi Agarwal", "alias": "somi", "regions": "", "is_super_admin": True},
        {"name": "Harshit Tiwari", "alias": "harshit", "regions": "", "is_super_admin": True},
        {"name": "Ananya Rohatgi", "alias": "ananya", "regions": "", "is_super_admin": True},
        {"name": "Prayag Kirad", "alias": "prayag", "regions": "", "is_super_admin": True},
        {"name": "Rakesh Chopra", "alias": "rakesh", "regions": "", "is_super_admin": True},
            
        ]

        # Step 1: Get a unique set of all regions in use
        all_regions = set()
        for mapping in user_region_mappings:
            for region in mapping["regions"].split(','):
                if region.strip():
                    all_regions.add(region.strip())

        # Step 2: Replace regions for super admins with the full set
        for mapping in user_region_mappings:
            if mapping.get("is_super_admin"):
                mapping["regions"] = ",".join(sorted(all_regions))

        # Step 3: Clear existing entries
        UserRegion.objects.all().delete()

        # Step 4: Populate table
        for mapping in user_region_mappings:
            UserRegion.objects.create(
                account_owner_name=mapping["name"],
                account_owner_alias=mapping["alias"],
                regions=mapping["regions"],
                is_super_admin=mapping["is_super_admin"]
            )
            self.stdout.write(self.style.SUCCESS(
                f'✅ Added {mapping["name"]} ({mapping["alias"]}) → Regions: {mapping["regions"]}'
                f'{" (Super Admin)" if mapping["is_super_admin"] else ""}'
            ))

        self.stdout.write(self.style.SUCCESS(
            f'🎉 Successfully populated {len(user_region_mappings)} user-region mappings.'
        ))
