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

## Perform installation of external libraries, dependencies and modules
ocf_dependencies = [ f for f in os.listdir(utils.dependencies_path) ]
for ocf_dependency in ocf_dependencies:
    utils.install_dependency(utils.ocf_path, ocf_dependency, ocf_modules_install)

for ocf_module in ocf_modules_install:
    utils.invoke_info_screen("install", ocf_module)
    utils.install_module(utils.ocf_path, ocf_module)
