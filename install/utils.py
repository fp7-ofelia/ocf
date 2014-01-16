import os
import subprocess

"""
@author: CarolinaFernandez

Utils for the installation of OCF modules.
"""

def print_header(text):
    print "\033[94m%s\033[0m" % str(text)

def print_error(text):
    print "\033[91m%s\033[0m" % str(text)

def list_modules(modules):
    print_header("\nInput all the modules you want to install: ")
    for module in modules.keys():
        print_header("%s: %s" % (str(module), str(modules[module])))

def install_module(ocf_path, ocf_module):
    try:
        os.chdir(os.path.join(ocf_path, ocf_module, "bin"))
        print_header(">> Invoking ofver for %s\n\n" % str(ocf_module))
        # TODO uncomment
        #subprocess.call(["./ofver","install","-f"])
    except Exception as e:
        print_error(e)

def install_dependency(ocf_path, ocf_dependency):
    try:
        os.chdir(os.path.join(ocf_path, "install"))
        print_header(">> Invoking %s\n\n" % str(ocf_dependency))
        # TODO uncomment
        #subprocess.call(["./%s" % ocf_dependency])
    except Exception as e:
        print_error(e)
