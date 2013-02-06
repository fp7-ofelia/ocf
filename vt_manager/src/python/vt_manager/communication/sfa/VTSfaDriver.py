import time

import datetime
#
from sfa.util.faults import MissingSfaInfo, UnknownSfaType, \
    RecordNotFound, SfaNotImplemented, SliverDoesNotExist

from sfa.util.sfalogging import logger
from sfa.util.defaultdict import defaultdict
from sfa.util.sfatime import utcparse, datetime_to_string, datetime_to_epoch
from sfa.util.xrn import Xrn, hrn_to_urn, get_leaf
from sfa.util.cache import Cache

# one would think the driver should not need to mess with the SFA db, but..
from sfa.storage.alchemy import dbsession
from sfa.storage.model import RegRecord

# used to be used in get_ticket
#from sfa.trust.sfaticket import SfaTicket

from sfa.rspecs.version_manager import VersionManager
from sfa.rspecs.rspec import RSpec

# the driver interface, mostly provides default behaviours
from sfa.managers.driver import Driver

from VMAggregate import VMAggregate

class VTSfaDriver:

	def __init__ (self, config):
		pass


	def list_resources (creds, options):
		version_manager = VersionManager()
        	# get the rspec's return format from options
        	rspec_version = version_manager.get_version(options.get('geni_rspec_version'))
        	version_string = "rspec_%s" % (rspec_version)

	        aggregate = VMAggregate(self)
	        rspec =  aggregate.get_rspec(version=rspec_version,options=options)
       		return rspec
	

