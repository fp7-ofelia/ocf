import os
from utils import utils

"""
@author: CarolinaFernandez

Installs OCF modules and external libraries/dependencies.
"""

## Obtain OCF modules
ocf_modules = utils.get_modules()

## Show choice screen for OCF modules
ocf_modules_install = utils.invoke_splash_screen("install", ocf_modules)

## Perform installation of common files, external libraries+dependencies and modules
if ocf_modules_install:
    ocf_commons = [ f for f in os.listdir(utils.common_path) ]
    for ocf_common in ocf_commons:
        utils.install_dependency(utils.common_path, ocf_common, ocf_modules_install)
    
    ocf_dependencies = [ f for f in os.listdir(utils.dependencies_path) ]
    for ocf_dependency in ocf_dependencies:
        utils.install_dependency(utils.dependencies_path, ocf_dependency, ocf_modules_install)
    
    for ocf_module in ocf_modules_install:
        utils.invoke_info_screen("install", ocf_module)
        utils.install_module(utils.ocf_path, ocf_module)
