from utils import utils

"""
@author: CarolinaFernandez

Upgrades OCF modules.
"""

# Show choice screen for OCF modules installed (available for upgrade)
ocf_modules_upgrade = utils.invoke_splash_screen("upgrade", utils.get_installed_modules())

if ocf_modules_upgrade:
    # Perform installation of common files
    utils.install_dependencies(utils.common_path, ocf_modules_upgrade)
    # Perform upgrade of already installed modules
    utils.upgrade_modules(ocf_modules_upgrade)
