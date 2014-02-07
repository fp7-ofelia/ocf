import os
from utils import utils

"""
@author: CarolinaFernandez

Installs OCF modules and external libraries/dependencies.
"""

# Show choice screen for OCF modules available for install
ocf_modules_install = utils.invoke_splash_screen("install", utils.get_modules())

if ocf_modules_install:
    # Perform installation of common files
    utils.install_dependencies(utils.common_path, ocf_modules_install)
    # Perform installation of external libraries+dependencies
    utils.install_dependencies(utils.dependencies_path, ocf_modules_install)
    # Perform installation of available modules
    utils.install_modules(ocf_modules_install)
