"""
Initialize vendor account for pushpaksystem
Run this script once to create the initial vendor account
"""

import json
from pathlib import Path
from datetime import datetime

# Configuration
DATA_DIR = Path("portal_data")
VENDORS_FILE = DATA_DIR / "vendors.json"

# Create data directory if it doesn't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load existing vendors or create new
if VENDORS_FILE.exists():
    with open(VENDORS_FILE, 'r') as f:
        vendors = json.load(f)
else:
    vendors = {}

# Add pushpaksystem vendor
vendors['pushpaksystem'] = {
    'company_name': 'Pushpak Systems',
    'email': 'contact@pushpaksystems.com',
    'phone': '+1 (555) 000-0000',
    'password': 'pushpak123',  # Change this password after first login!
    'contact_person': 'Pushpak Mohanty',
    'status': 'active',
    'created_date': datetime.now().isoformat(),
    'total_submissions': 0
}

# Save vendors
with open(VENDORS_FILE, 'w') as f:
    json.dump(vendors, f, indent=2)

print("✅ Vendor 'pushpaksystem' created successfully!")
print("\nLogin Credentials:")
print("==================")
print("Username: pushpaksystem")
print("Password: pushpak123")
print("\n⚠️  Please change the password after first login!")

# Made with Bob
