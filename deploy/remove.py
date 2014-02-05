from utils import utils

"""
@author: CarolinaFernandez

Removes OCF modules and external libraries/dependencies.
"""

ocf_modules = utils.get_modules()

## Show choice screen for OCF modules
ocf_modules_remove = utils.invoke_splash_screen("remove", ocf_modules)

for ocf_module in ocf_modules_remove:
    utils.invoke_info_screen("remove", ocf_module)
    utils.remove_module(utils.ocf_path, ocf_module)
