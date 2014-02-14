from datetime import datetime, timedelta
from sqlalchemy.dialects.mysql import TINYINT, DOUBLE
from utils.base import db
import amsoil.core.log
import amsoil.core.pluginmanager as pm

logging=amsoil.core.log.getLogger('Expires')

'''@author: SergioVidiella'''

class Expires(db.Model):
    """Expiration time of the Virtual Machine (only GeniV3)."""

    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'expires'
    __table_args__ = {'extend_existing':True}

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    expires = db.Column(db.DateTime, nullable=False)
    do_save = True
    
    @staticmethod
    def constructor(expiration, save=True):
        self = Expires()
        try:
            self.expires = expiration
            do_save = save
            if save:
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            raise e
        return self
    
    def auto_save(self):
        if self.do_save:
            db.session.add(self)
            db.session.commit()
    
    '''Getters and Setters'''
    def set_expiration(self, expires):
        # XXX: Expiration validator?
        self.expires = expires
        self.auto_save()
    
    def get_expiration(self):
        return self.expires
    
    def get_vm(self):
        if self.expires_vm:
            return self.expires_vm[0].vm
        elif self.allocated_vm:
            return self.allocated_vm
        else:
            return None

    def destroy(self):
        db.session.delete(self)
        db.session.commit()
