import os
import subprocess

"""
@author: CarolinaFernandez

Utils for the installation of OCF modules.
"""

ocf_path = "/opt/ofelia"
deploy_path = os.path.join(ocf_path, "deploy")
gui_path = os.path.join(deploy_path, "gui")
common_path = os.path.join(deploy_path, "common")
dependencies_path = os.path.join(deploy_path, "dependencies")

## Print

def print_header(text):
    print "\033[94m%s\033[0m" % str(text)

def print_error(text):
    print "\033[91m%s\033[0m" % str(text)

## Paths and files

def get_modules():
    ocf_modules = os.walk(ocf_path).next()[1]
    ocf_modules.remove("deploy")
    ocf_modules.remove(".git")
    return ocf_modules

def get_installed_modules():
    """
    A module is installed if it contains a .currentVersion file.
    """
    ocf_modules_installed = []
    ocf_modules = get_modules()
    for ocf_module in ocf_modules:
        try:
            with open(os.path.join(ocf_path, ocf_module, ".currentVersion")):
                ocf_modules_installed.append(ocf_module)
        except:
            pass
    return ocf_modules_installed

def get_script_files(path):
    return [ f for f in os.listdir(path) if f.endswith(".sh") and not f.startswith(".") ]

def list_modules(modules):
    print_header("\nInput all the modules you want to install: ")
    for module in modules.keys():
        print_header("%s: %s" % (str(module), str(modules[module])))

## System execution

def execute_command(arg_list):
    return_code = subprocess.call(arg_list)
    return return_code

## Screens

def invoke_step_start_screen(deploy_action, arg):
    execute_command(["%s/start_step.sh" % gui_path] + [deploy_action] + [arg])

def invoke_info_screen(title, content, height, width):
    execute_command(["%s/info.sh" % gui_path] + [title, content, height, width])

def invoke_splash_screen(deploy_action, arg_list):
    #os.system("./gui/splash.sh %s" % str(ocf_modules))
    
    #process = subprocess.Popen(["./gui/splash.sh"], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #process.stdin.write(str(arg_list))
    ## Wait for the process to terminate
    #out, err = process.communicate()
    ##errcode = process.returncode
    if not arg_list:
        invoke_info_screen("%s stopped" % deploy_action, "There are no modules available for this operation", "8", "45")
        return None
    return_code = execute_command(["%s/splash.sh" % gui_path] + [deploy_action] + arg_list)
    chosen_modules = []
    # Return code for UNIX scripts (0: good, 1: error)
    if not return_code:
        try:
            chosen_modules = open("./ocf_modules_deploy", "r").readlines()
            # Parse and convert to list of modules
            chosen_modules = " ".join(chosen_modules).replace("\"", "").replace("\n","").split(" ")
            os.remove("./ocf_modules_deploy")
        except Exception as e:
            print_error(e)
    return chosen_modules

def clear_screen():
    execute_command(["clear"])

## Operations over modules (upgrade, install, remove)

def upgrade_module(ocf_path, ocf_module):
    try:
        clear_screen()
        current_dir = os.getcwd()
        os.chdir(os.path.join(ocf_path, ocf_module, "bin"))
        print_header(">> Invoking ofver for %s\n\n" % str(ocf_module))
        return_code = execute_command(["./ofver","upgrade","-f"])
        os.chdir(current_dir)
    except Exception as e:
        print_error(e)

def upgrade_modules(ocf_modules):
    for ocf_module in ocf_modules:
        invoke_step_start_screen("upgrade", ocf_module)
        upgrade_module(ocf_path, ocf_module)

def install_module(ocf_path, ocf_module):
    try:
        clear_screen()
        current_dir = os.getcwd()
        os.chdir(os.path.join(ocf_path, ocf_module, "bin"))
        print_header(">> Invoking ofver for %s\n\n" % str(ocf_module))
        return_code = execute_command(["./ofver","install","-f"])
        os.chdir(current_dir)
    except Exception as e:
        print_error(e)

def install_modules(ocf_modules):
    for ocf_module in ocf_modules:
        invoke_step_start_screen("install", ocf_module)
        install_module(ocf_path, ocf_module)

def remove_module(ocf_path, ocf_module):
    try:
        clear_screen()
        current_dir = os.getcwd()
        os.chdir(os.path.join(ocf_path, ocf_module))
        os.remove(".currentVersion")
        os.chdir(current_dir)
    except Exception as e:
        print_error(e)

def remove_modules(ocf_modules):
    for ocf_module in ocf_modules:
        invoke_step_start_screen("remove", ocf_module)
        remove_module(ocf_path, ocf_module)

## External libraries and dependencies

def install_dependency(dependencies_path, ocf_dependency, ocf_modules):
    try:
        clear_screen()
        current_dir = os.getcwd()
        os.chdir(dependencies_path)
        print_header(">> Invoking %s\n\n" % str(ocf_dependency))
        return_code = execute_command(["./%s" % ocf_dependency, "%s" % ocf_modules])
        os.chdir(current_dir)
    except Exception as e:
        print_error(e)

def install_dependencies(path, ocf_modules):
    ocf_dependencies = get_script_files(path)
    for ocf_dependency in ocf_dependencies:
        install_dependency(path, ocf_dependency, ocf_modules)
