import sys
sys.path.append("/opt/ofelia/AMsoil/src/vendor/configdb/")
sys.path.append("/opt/ofelia/AMsoil/src/")
sys.path.append("/opt/ofelia/AMsoil/src/vendor/virtrm")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("config", amconfigdb.ConfigDB())
pm.registerService("configexceptions", amconfigdbexceptions)
from models.common.expiration import Expiration
import unittest

class ExpirationGettersTest(unittest.TestCase):

    def given_this_expiration(self):
        expiration = Expiration()
        return expiration

    def test_should_get_expiration(self):
        expiration = self.given_this_expiration()
        param = "get_expiration"
        expiration.expiration = param
        self.assertEquals(param, expiration.get_expiration())
    
    def test_should_get_do_save(self):
        expiration = self.given_this_expiration()
        param = "get_do_save"
        expiration.do_save = param
        self.assertEquals(param, expiration.get_do_save())

if __name__ == '__main__':
    unittest.main()

