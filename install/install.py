import os
import utils

"""
@author: CarolinaFernandez

Installs OCF modules and external libraries/dependencies.
"""

ocf_path = "/opt/ofelia"
dependencies_path = os.path.join(ocf_path, "install", "dependencies")

## Obtain OCF modules
ocf_modules = os.walk(ocf_path).next()[1]
ocf_modules.remove("install")
ocf_modules.remove(".git")

## Show choice screen for OCF modules
ocf_modules_install = utils.invoke_splash_screen(ocf_modules)

## Perform installation of external libraries, dependencies and modules
ocf_dependencies = [ f for f in os.listdir(dependencies_path) ]
for ocf_dependency in ocf_dependencies:
    utils.install_dependency(ocf_path, ocf_dependency)

for ocf_module in ocf_modules_install:
    utils.install_module(ocf_path, ocf_module)
