'''
Created on May 11, 2010

@author: jnaous
'''
from decorator import decorator

@decorator
def setup_mgmt_env(func, *args, **kwargs):
    from django.core.management import setup_environ, call_command
    import sys
    
    assert(args[1].endswith(".json"))
    
    backup = sys.path[0]
    sys.path[0] = args[0]
    
    import settings
    setup_environ(settings, args[1])
    
    func(*args, **kwargs)
    
    sys.path[0] = backup

@setup_mgmt_env
def store_db(project_path, fixture_path):
    """
    Store the DB from project path into a fixture.
    
    @param project_path: directory of the django project
    @param fixture_path: path to file to store the fixture. Must end in .json
    """
    data = call_command("dumpdata")
    f = open(fixture_path, "w")
    f.write(data)
    f.close()

@setup_mgmt_env
def load_db(project_path, fixture_path):
    """
    Flush the DB for the project specified in project_path.
    Load the fixture in fixture_path.

    @param project_path: directory of the django project
    @param fixture_path: path to file storing the fixture. Must end in .json
    """
    call_command("flush", noinput=True)
    call_command("loaddata", fixture_path)
