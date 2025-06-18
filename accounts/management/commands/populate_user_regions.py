from django.core.management.base import BaseCommand
from accounts.models import UserRegion  

class Command(BaseCommand):
    help = 'Populate UserRegion table with predefined user-region mappings'

    def handle(self, *args, **options):
        # Define the user-region mappings based on your data
        user_region_mappings = [
            # India region users
            {"name": "Vinay Sharma", "alias": "Vinays", "regions": "India"},
            {"name": "Nikhil Chopra", "alias": "NikhChop", "regions": "India,International,Singapore"},
            {"name": "Hitesh Rajesh Gupta", "alias": "HiteGupt", "regions": "India,Singapore"},
            {"name": "Rohit Jee", "alias": "rjee", "regions": "India,Singapore"},
            {"name": "Ashish Chopra", "alias": "achopra", "regions": "India"},
            {"name": "hrms Admin", "alias": "admin", "regions": "India,Singapore"},
            {"name": "Somya Shukla", "alias": "sshuk", "regions": "India"},
            {"name": "Ambika Singh", "alias": "asing", "regions": "India"},
            {"name": "Mohan G.N.", "alias": "MohaG.N", "regions": "India"},
            {"name": "Ruchita Katkar", "alias": "rkatk", "regions": "India"},
            {"name": "Srishti Singh", "alias": "ssingh", "regions": "India"},
            {"name": "Richy Isaac", "alias": "risaa", "regions": "India"},
            
            # Singapore region users
            {"name": "Chandan Roy", "alias": "CR", "regions": "India,Singapore"},
            {"name": "Love Jain", "alias": "ljain", "regions": "International,Singapore"},
            {"name": "Shon Tang", "alias": "stang", "regions": "India,Singapore"},
            {"name": "Christopher Jefferson Galistan", "alias": "cgali", "regions": "Singapore"},
            {"name": "Anthony Eng", "alias": "aeng", "regions": "Singapore"},
            {"name": "Monique Tay", "alias": "mtay", "regions": "Singapore"},
            {"name": "Mohan Kumar", "alias": "mkuma", "regions": "Singapore"},
            {"name": "Malkhan Ali", "alias": "mali", "regions": "Singapore"},
            {"name": "Ashra Sachdeva", "alias": "asach", "regions": "International,Singapore"},
            {"name": "Rahel Tribhuvan", "alias": "rtrib", "regions": "Singapore"},
            {"name": "Sukanta Lahiri", "alias": "slahi", "regions": "Singapore"},
            {"name": "Apoorva Johri", "alias": "ajohr", "regions": "Singapore"},
            {"name": "Rohit Gupta", "alias": "rgupt", "regions": "Singapore"},
            
            # International region users
            {"name": "Subham Choudhary", "alias": "schou", "regions": "International"},
            {"name": "Saurabh Sadhu", "alias": "ssadh", "regions": "International"},
        ]
        
        # Clear existing data
        UserRegion.objects.all().delete()
        
        # Populate with new data
        for mapping in user_region_mappings:
            UserRegion.objects.create(
                account_owner_name=mapping["name"],
                account_owner_alias=mapping["alias"],
                regions=mapping["regions"]
            )
            self.stdout.write(
                self.style.SUCCESS(f'Added {mapping["name"]} with regions: {mapping["regions"]}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully populated {len(user_region_mappings)} user-region mappings')
        )