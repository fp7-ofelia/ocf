from datetime import datetime
from utils.base import db
import amsoil.core.log
import amsoil.core.pluginmanager as pm

logging=amsoil.core.log.getLogger('Expires')

'''@author: SergioVidiella'''

class Expiration(db.Model):
    """Expiration time of the Virtual Machine (only GeniV3)."""

    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'expiration'
    __table_args__ = {'extend_existing':True}

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    expiration = db.Column(db.DateTime, nullable=False, default=datetime.now())
    do_save = True

    @staticmethod    
    def __init__(self,expiration=None,save=False):
        self.expiration = expiration
        do_save = save
        if save:
            db.session.add(self)
            db.session.commit()
    
    def destroy(self):
        db.session.delete(self)
        db.session.commit()
     
    def auto_save(self):
        if self.do_save:
            db.session.add(self)
            db.session.commit()
    
    '''Getters and Setters'''
    def set_expiration(self, expiration):
        self.expiration = expiration
        self.auto_save()
    
    def get_expiration(self):
        return self.expiration

    def set_do_save(self, save):
        self.do_save = save
    
    def get_do_save(self):
        return self.do_save
