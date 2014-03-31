from utils import utils

"""
@author: CarolinaFernandez

Removes OCF modules and external libraries/dependencies.
"""

# Show choice screen for OCF modules installed (available for removal)
ocf_modules_remove = utils.invoke_splash_screen("remove", utils.get_installed_modules())

if ocf_modules_remove:
    utils.remove_modules(ocf_modules_remove)
