import os
from utils import utils

"""
@author: CarolinaFernandez

Upgrades OCF modules.
"""

## Obtain OCF modules
ocf_modules = utils.get_modules()

ocf_modules_to_upgrade = []
for ocf_module in ocf_modules:
    try:
        with open(os.path.join(utils.ocf_path, ocf_module, ".currentVersion")):
            ocf_modules_to_upgrade.append(ocf_module)
    except:
        pass

## Show choice screen for OCF modules
ocf_modules_upgrade = utils.invoke_splash_screen("upgrade", ocf_modules_to_upgrade)

## Perform upgrade of already installed modules
for ocf_module in ocf_modules_upgrade:
    utils.invoke_info_screen("upgrade", ocf_module)
    utils.upgrade_module(utils.ocf_path, ocf_module)
