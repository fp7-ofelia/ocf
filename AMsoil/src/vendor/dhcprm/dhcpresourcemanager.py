from datetime import datetime, timedelta

import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('dhcpresourcemanager')

from ip import IP
from dhcpexceptions import *

worker = pm.getService('worker')

class DHCPResourceManager(object):
    """
    Please see the wiki for more information on Resource Managers.
    Also to undestand the database concepts invloved her (e.g. what the hell does 'expunge' mean?), please read the Database page in the wiki.
    Other than this, this class provides the necessary functions to manage DHCP leases.
    
    Leases have two meaning depending on where they live:
    - If you you find it within this class: The lease is a database record which is an object in the current database session.
    - If you find it as parameter or return value: The lease is a value object (no connection to the database at all) and holds the values relevant for the delegate.
    """
    config = pm.getService("config")
    
    RESERVATION_TIMEOUT = config.get("dhcprm.max_reservation_duration") # sec in the allocated state
    MAX_LEASE_DURATION = config.get("dhcprm.max_lease_duration") # sec in the provisioned state (you can always call renew)

    EXPIRY_CHECK_INTERVAL = 10 # sec
    
    def __init__(self):
        super(DHCPResourceManager, self).__init__()
        # register callback for regular updates
        worker.addAsReccurring("dhcpresourcemanager", "expire_leases", None, self.EXPIRY_CHECK_INTERVAL)
    
    def get_all_leases(self):
        leases = []
        for ip in IP([192,168,1,1]).upto(IP([192,168,1,20])): # for the sake of simplicity, we set the ip range statically (should be a config option)
            lease = db_session.query(DHCPLease).filter(DHCPLease.ip_str == str(ip)).first()
            if lease == None: # there is no lease currently, so we return a blank object with just the ip set
                leases.append(DHCPLease(ip_str=str(ip)))
            else:
                leases.append(lease)
        db_session.expunge_all() # detach the objects from the database session, so the user can not directly change the database
        return leases
    
    def reserve_lease(self, ip_str, slice_name, owner_uuid, owner_email=None, end_time=None):
        lease = db_session.query(DHCPLease).filter(DHCPLease.ip_str == ip_str).first()
        if lease != None:
            raise DHCPLeaseAlreadyTaken(ip_str)

        # change database entry
        lease = DHCPLease(ip_str=ip_str, slice_name=slice_name, owner_uuid=str(owner_uuid), owner_email=owner_email)
        lease.set_end_time_with_max(end_time, self.RESERVATION_TIMEOUT)
        db_session.add(lease)
        db_session.commit()
        db_session.expunge_all() # detach the objects from the database session, so the user can not directly change the database
        return lease
    
    def extend_lease(self, lease, end_time=None):
        lease = find_lease(lease.ip) # find the internal data object
        lease.set_end_time_with_max(end_time, self.MAX_LEASE_DURATION)
        db_session.commit()
        db_session.expunge_all() # detach the objects from the database session, so the user can not directly change the database
        return lease
    
    def leases_in_slice(self, slice_name):
        leases = db_session.query(DHCPLease).filter(DHCPLease.slice_name == slice_name).all()
        db_session.expunge_all() # detach the objects from the database session, so the user can not directly change the database
        return leases
        
    
    def free_lease(self, lease):
        lease = find_lease(lease.ip) # find the internal data object
        db_session.delete(lease)
        db_session.commit()
        return None
        
    @worker.outsideprocess
    def expire_leases(self, params):
        leases = db_session.query(DHCPLease).filter(DHCPLease.end_time < datetime.utcnow()).all()
        for lease in leases:
            logger.info("Removing expired DHCP lease: %s" % (lease.ip_str,))
            self.free_lease(lease)
        return


# ----------------------------------------------------
# ------------------ database stuff ------------------
# ----------------------------------------------------
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import exists

import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('worker')

from amsoil.config import expand_amsoil_path

from ip import IP

# initialize sqlalchemy
DHCPDB_PATH = expand_amsoil_path(pm.getService('config').get('dhcprm.dbpath'))
DHCPDB_ENGINE = "sqlite:///%s" % (DHCPDB_PATH,)

db_engine = create_engine(DHCPDB_ENGINE, pool_recycle=6000) # please see the wiki for more info
db_session_factory = sessionmaker(autoflush=True, bind=db_engine, expire_on_commit=False) # the class which can create sessions (factory pattern)
db_session = scoped_session(db_session_factory) # still a session creator, but it will create _one_ session per thread and delegate all method calls to it
Base = declarative_base() # get the base class for the ORM, which includes the metadata object (collection of table descriptions)

# We should limit the session's scope (lifetime) to one request. Yet, here we have a different solution.
# In order to avoid side effects (from someone changing a database object), we expunge_all() objects when we hand out objects to other classes.
# So, we can leave the session as it is, because there are no objects in it anyway.


class DHCPLease(Base):
    """Please see the Database wiki page."""
    __tablename__ = 'leases'
    id = Column(Integer, primary_key=True)
    ip_str = Column(String(20))
    slice_name = Column(String(255))
    owner_uuid = Column(String(100)) # could also be limited to 37, 42 or 46
    owner_email = Column(String(255)) # could also be limited to 254
    end_time = Column(DateTime)

    @property
    def ip(self):
        return IP.from_str(self.ip_str)
    @ip.setter
    def set_ip(self, ip):
        self.ip_str = str(ip)

    def set_end_time_with_max(self, end_time, max_duration):
        """If {end_time} is none, the current time+{max_duration} is assumed."""
        max_end_time = datetime.utcnow() + timedelta(0, max_duration)
        if end_time == None:
            end_time = max_end_time
        if (end_time > max_end_time):
            raise DHCPMaxLeaseDurationExceeded(lease.ip_str)
        self.end_time = end_time

    @property
    def available(self):
        return not bool(self.slice_name)

Base.metadata.create_all(db_engine) # create the tables if they are not there yet


def find_lease(ip_or_ip_str):
    # TODO do error handling for MultipleResultsFound, NoResultFound
    if isinstance(ip_or_ip_str, IP):
        ip_or_ip_str = str(ip_or_ip_str)
    return db_session.query(DHCPLease).filter(DHCPLease.ip_str == str(ip_or_ip_str)).one()
    # raise DHCPLeaseNotFound(ip)
