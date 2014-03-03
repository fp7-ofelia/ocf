from translator import Translator
import amsoil.core.pluginmanager as pm

def setup():
    pm.registerService("translator", Translator)
