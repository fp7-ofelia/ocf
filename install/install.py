import os
import utils

"""
@author: CarolinaFernandez

Installs OCF modules and external libraries/dependencies.
"""

ocf_path = "/opt/ofelia"
#unallowed_files = [__file__, "utils.py"]

ocf_modules = os.walk(ocf_path).next()[1]
ocf_modules.remove("install")
ocf_modules.remove(".git")

# Show modules to be installed
enum_modules = [ x for x in enumerate(ocf_modules) ]
ocf_modules = dict()
for enum in enum_modules:
    ocf_modules[enum[0]] = enum[1]

# Choose modules to install
ocf_modules_install = dict()
choosing_modules_install = True
while choosing_modules_install:
    utils.list_modules(ocf_modules)
    module_install = raw_input("Enter module: ")
    try:
        if isinstance(module_install, int):
            # Using number for module
            if module_install in ocf_modules.keys():
                ocf_modules_install[ocf_modules.get(module_install)] = True
        else:
            try:
                # Using number for module
                if int(module_install) in ocf_modules.keys():
                    ocf_modules_install[ocf_modules.get(int(module_install))] = True
            except:
                # Using name of module
                if module_install in ocf_modules.values():
                    ocf_modules_install[module_install] = True
    except:
        pass
    print "The following modules will be installed: %s" % str(ocf_modules_install.keys())
    # Default value: "y"
    choosing_modules_install = raw_input("Do you want to add some other? [Y/n]: ") or "y"
    choosing_modules_install = True if choosing_modules_install in ["y","Y","yes"] else False

# Install modules 
print "\n\n\nThe following modules will be installed: %s\n\n\n" % str(ocf_modules_install.keys())
current_dir = os.getcwd()
for ocf_module in ocf_modules_install.keys():
    utils.install_module(ocf_path, ocf_module)

# Install external libraries, dependencies, etc
ocf_dependencies = [ f for f in os.listdir(os.path.join(ocf_path, "install")) if os.path.isfile(os.path.join(ocf_path, "install", f)) ]
#ocf_dependencies = [ f for f in ocf_dependencies if f not in unallowed_files ]
ocf_dependencies = [ f for f in ocf_dependencies if ".py" not in f ]
for ocf_dependency in ocf_dependencies:
    utils.install_dependency(ocf_path, ocf_dependency)
