import time

import datetime
#
from vt_manager.communication.sfa.util.faults import MissingSfaInfo, UnknownSfaType, \
    RecordNotFound, SfaNotImplemented, SliverDoesNotExist

from vt_manager.communication.sfa.util.sfalogging import logger
from vt_manager.communication.sfa.util.defaultdict import defaultdict
from vt_manager.communication.sfa.util.sfatime import utcparse, datetime_to_string, datetime_to_epoch
from vt_manager.communication.sfa.util.xrn import Xrn, hrn_to_urn, get_leaf
from vt_manager.communication.sfa.util.cache import Cache

# one would think the driver should not need to mess with the SFA db, but..
#from vt_manager.communication.sfa.storage.alchemy import dbsession
#from vt_manager.communication.sfa.storage.model import RegRecord

# used to be used in get_ticket
#from sfa.trust.sfaticket import SfaTicket

from vt_manager.communication.sfa.rspecs.version_manager import VersionManager
from vt_manager.communication.sfa.rspecs.rspec import RSpec

# the driver interface, mostly provides default behaviours
#from vt_manager.communication.sfa.managers.driver import Driver

from vt_manager.communication.sfa.VMAggregate import VMAggregate

class VTSfaDriver:

	def __init__ (self, config):
		pass


	def list_resources (self,creds, options):
		version_manager = VersionManager()
        	# get the rspec's return format from options
        	rspec_version = version_manager.get_version(options.get('geni_rspec_version'))
        	version_string = "rspec_%s" % (rspec_version)

	        aggregate = VMAggregate()
	        rspec =  aggregate.get_rspec(version=rspec_version,options=options)
		print 'list_resources Rspec instance:',rspec
       		return rspec
	

