'''
Created on May 13, 2010

@author: jnaous
'''

def call_env_command(project_path, *args, **kwargs):
    from django.core.management import setup_environ, call_command
    import sys
    
    backup = sys.path[0]
    sys.path[0] = project_path
    
    import settings
    
    setup_environ(settings)
    
    call_command(*args, **kwargs)
    
    sys.path[0] = backup
