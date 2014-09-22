import os
from utils import utils

"""
@author: CarolinaFernandez

Migrate OCF components to another physical location within the host.
"""

# Show input screen to set new path for OCF components
new_location = utils.invoke_splash_screen("migrate", utils.get_modules())

if new_location:
    # Perform migration to new location
    utils.migrate_framework(new_location[0])
