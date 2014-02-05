import os
import subprocess

"""
@author: CarolinaFernandez

Utils for the installation of OCF modules.
"""

ocf_path = "/opt/ofelia"
dependencies_path = os.path.join(ocf_path, "deploy", "dependencies")

def print_header(text):
    print "\033[94m%s\033[0m" % str(text)

def print_error(text):
    print "\033[91m%s\033[0m" % str(text)

def get_modules():
    ocf_modules = os.walk(ocf_path).next()[1]
    ocf_modules.remove("deploy")
    ocf_modules.remove(".git")
    return ocf_modules

def list_modules(modules):
    print_header("\nInput all the modules you want to install: ")
    for module in modules.keys():
        print_header("%s: %s" % (str(module), str(modules[module])))

def execute_command(arg_list):
    return_code = subprocess.call(arg_list)
    return return_code

def invoke_info_screen(deploy_action, arg):
    execute_command(["./info_step.sh"] + [deploy_action] + [arg])

def invoke_splash_screen(deploy_action, arg_list):
    #os.system("./splash.sh %s" % str(ocf_modules))
    
    #process = subprocess.Popen(["./splash.sh"], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #process.stdin.write(str(arg_list))
    ## Wait for the process to terminate
    #out, err = process.communicate()
    ##errcode = process.returncode
    
    return_code = execute_command(["./splash.sh"] + [deploy_action] + arg_list)
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

def upgrade_module(ocf_path, ocf_module):
    try:
        current_dir = os.getcwd()
        os.chdir(os.path.join(ocf_path, ocf_module, "bin"))
        print_header(">> Invoking ofver for %s\n\n" % str(ocf_module))
        return_code = execute_command(["./ofver","upgrade","-f"])
        os.chdir(current_dir)
    except Exception as e:
        print_error(e)

def install_module(ocf_path, ocf_module):
    try:
        current_dir = os.getcwd()
        os.chdir(os.path.join(ocf_path, ocf_module, "bin"))
        print_header(">> Invoking ofver for %s\n\n" % str(ocf_module))
        return_code = execute_command(["./ofver","install","-f"])
        os.chdir(current_dir)
    except Exception as e:
        print_error(e)

def install_dependency(ocf_path, ocf_dependency, ocf_modules):
    try:
        current_dir = os.getcwd()
        os.chdir(os.path.join(ocf_path, "deploy", "dependencies"))
        print_header(">> Invoking %s\n\n" % str(ocf_dependency))
        return_code = execute_command(["./%s" % ocf_dependency, "%s" % ocf_modules])
        os.chdir(current_dir)
    except Exception as e:
        print_error(e)

def remove_module(ocf_path, ocf_module):
    try:
        current_dir = os.getcwd()
        os.chdir(os.path.join(ocf_path, ocf_module))
        os.remove(".currentVersion")
        os.chdir(current_dir)
    except Exception as e:
        print_error(e)
