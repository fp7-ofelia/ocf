import os
import utils

"""
@author: CarolinaFernandez

Upgrades OCF modules.
"""

ocf_path = "/opt/ofelia"

## Obtain OCF modules
ocf_modules = os.walk(ocf_path).next()[1]
ocf_modules.remove("deploy")
ocf_modules.remove(".git")

ocf_modules_to_upgrade = []
for ocf_module in ocf_modules:
    try:
        with open(os.path.join(ocf_path, ocf_module, ".currentVersion")):
            ocf_modules_to_upgrade.append(ocf_module)
    except:
        pass

## Show choice screen for OCF modules
ocf_modules_upgrade = utils.invoke_splash_screen("upgrade", ocf_modules_to_upgrade)

## Perform upgrade of already installed modules
for ocf_module in ocf_modules_upgrade:
    utils.upgrade_module(ocf_path, ocf_module)
