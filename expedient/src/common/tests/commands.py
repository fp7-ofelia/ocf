'''
Created on May 13, 2010

@author: jnaous
'''

def call_env_command(project_path, *args, **kwargs):
    from django.core.management import setup_environ, call_command
    import sys, imp
    
    backup = sys.path[0]
    sys.path[0] = project_path
    
    import settings
    setup_environ(settings)
    call_command(*args, **kwargs)

    sys.path[0] = backup

class Env(object):
    """
    Use to switch between different django environments.
    """
    
    def __init__(self, project_path):
        self.project_path = project_path
        
    def switch_to(self):
        from django.core.management import setup_environ
        import sys
        
        self.curr_mods = sys.modules.copy()

        self.backup_path = sys.path[0]
        sys.path[0] = self.project_path
        
        import settings
        setup_environ(settings)
        
        from django.db.models.loading import get_models
        loaded_models = get_models()

    def switch_from(self):
        import sys
        sys.path[0] = self.backup_path
