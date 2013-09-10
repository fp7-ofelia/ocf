from sfa.util.faults import RecordNotFound, AccountNotEnabled, PermissionError, MissingAuthority, \
    UnknownSfaType, ExistingRecord, NonExistingRecord
from sfa.util.sfatime import utcparse, datetime_to_epoch
from sfa.util.prefixTree import prefixTree
from sfa.util.xrn import Xrn, get_authority, hrn_to_urn, urn_to_hrn
from sfa.util.version import version_core
from sfa.util.sfalogging import logger

from sfa.trust.gid import GID
from sfa.trust.credential import Credential
from sfa.trust.certificate import Certificate, Keypair, convert_public_key
from sfa.trust.gid import create_uuid

from sfa.storage.model import make_record, RegRecord, RegAuthority, RegUser, RegSlice, RegKey, \
    augment_with_sfa_builtins



class RegistryManager:

    def __init__ (self, config): 
        pass

    # The GENI GetVersion call
    def GetVersion(self, api, options):
        peers = dict ( [ (hrn,interface.get_url()) for (hrn,interface) in api.registries.iteritems()
                       if hrn != api.hrn])
        xrn=Xrn(api.hrn)
        return version_core({'interface':'registry',
                             'sfa': 2,
                             'geni_api': 2,
                             'hrn':xrn.get_hrn(),
                             'urn':xrn.get_urn(),
                             'peers':peers})

    def GetCredential(self, api, xrn, type, caller_xrn=None):
        # convert xrn to hrn     
        if type:
            hrn = urn_to_hrn(xrn)[0]
        else:
            hrn, type = urn_to_hrn(xrn)

        # Is this a root or sub authority
        auth_hrn = api.auth.get_authority(hrn)
        if not auth_hrn or hrn == api.config.SFA_INTERFACE_HRN:
            auth_hrn = hrn
        auth_info = api.auth.get_auth_info(auth_hrn)
        # get record info
        record=dbsession.query(RegRecord).filter_by(type=type,hrn=hrn).first()
        if not record:
            raise RecordNotFound("hrn=%s, type=%s"%(hrn,type))

        # get the callers gid
        # if caller_xrn is not specified assume the caller is the record
        # object itself.
        if not caller_xrn:
            caller_hrn = hrn
            caller_gid = record.get_gid_object()
        else:
            caller_hrn, caller_type = urn_to_hrn(caller_xrn)
            if caller_type:
                caller_record = dbsession.query(RegRecord).filter_by(hrn=caller_hrn,type=caller_type).first()
            else:
                caller_record = dbsession.query(RegRecord).filter_by(hrn=caller_hrn).first()
            if not caller_record:
                raise RecordNotFound("Unable to associated caller (hrn=%s, type=%s) with credential for (hrn: %s, type: %s)"%(caller_hrn, caller_type, hrn, type))
            caller_gid = GID(string=caller_record.gid)i

        object_hrn = record.get_gid_object().get_hrn()
        # call the builtin authorization/credential generation engine
        rights = api.auth.determine_user_rights(caller_hrn, record)
        # make sure caller has rights to this object
        if rights.is_empty():
            raise PermissionError("%s has no rights to %s (%s)" % \
                                  (caller_hrn, object_hrn, xrn))
        object_gid = GID(string=record.gid)
        new_cred = Credential(subject = object_gid.get_subject())
        new_cred.set_gid_caller(caller_gid)
        new_cred.set_gid_object(object_gid)
        new_cred.set_issuer_keys(auth_info.get_privkey_filename(), auth_info.get_gid_filename())
        #new_cred.set_pubkey(object_gid.get_pubkey())
        new_cred.set_privileges(rights)
        new_cred.get_privileges().delegate_all_privileges(True)
        if hasattr(record,'expires'):
            date = utcparse(record.expires)
            expires = datetime_to_epoch(date)
            new_cred.set_expiration(int(expires))
        auth_kind = "authority,ma,sa"
        # Parent not necessary, verify with certs
        #new_cred.set_parent(api.auth.hierarchy.get_auth_cred(auth_hrn, kind=auth_kind))
        new_cred.encode()
        new_cred.sign()

        return new_cred.save_to_string(save_parents=True)

    def GetSelfCredential(certificate, xnr, type):
        if type:
            hrn = urn_to_hrn(xrn)[0]
        else:
            hrn, type = urn_to_hrn(xrn)

        origin_hrn = Certificate(string=cert).get_subject()
        ### authenticate the gid
        # import here so we can load this module at build-time for sfa2wsdl
        #from sfa.storage.alchemy import dbsession
        from sfa.storage.model import RegRecord

        # xxx-local - the current code runs Resolve, which would forward to 
        # another registry if needed
        # I wonder if this is truly the intention, or shouldn't we instead 
        # only look in the local db ?
        records = self.api.manager.Resolve(self.api, xrn, type, details=False)
        if not records:
            raise RecordNotFound(hrn)

        record_obj = RegRecord (dict=records[0])
        # xxx-local the local-only version would read 
        #record_obj = dbsession.query(RegRecord).filter_by(hrn=hrn).first()
        #if not record_obj: raise RecordNotFound(hrn)
        gid = record_obj.get_gid_object()
        gid_str = gid.save_to_string(save_parents=True)
        self.api.auth.authenticateGid(gid_str, [cert, type, hrn])
        # authenticate the certificate against the gid in the db
        certificate = Certificate(string=cert)
        if not certificate.is_pubkey(gid.get_pubkey()):
            for (obj,name) in [ (certificate,"CERT"), (gid,"GID"), ]:
                if hasattr (obj,'filename'):
            raise ConnectionKeyGIDMismatch(gid.get_subject())

        return self.api.manager.GetCredential(self.api, xrn, type)

    def Resolve(self, api, xrns, type=None, details=False):

        if not isinstance(xrns, types.ListType):
            # try to infer type if not set and we get a single input
            if not type:
                type = Xrn(xrns).get_type()
            xrns = [xrns]
        hrns = [urn_to_hrn(xrn)[0] for xrn in xrns]

        # load all known registry names into a prefix tree and attempt to find
        # the longest matching prefix
        # create a dict where key is a registry hrn and its value is a list
        # of hrns at that registry (determined by the known prefix tree).  
        xrn_dict = {}
        registries = api.registries
        tree = prefixTree()
        registry_hrns = registries.keys()
        tree.load(registry_hrns)
        for xrn in xrns:
            registry_hrn = tree.best_match(urn_to_hrn(xrn)[0])
            if registry_hrn not in xrn_dict:
                xrn_dict[registry_hrn] = []
            xrn_dict[registry_hrn].append(xrn)

        records = []
        for registry_hrn in xrn_dict:
            # skip the hrn without a registry hrn
            # XX should we let the user know the authority is unknown?       
            if not registry_hrn:
                continue

            # if the best match (longest matching hrn) is not the local registry,
            # forward the request
            xrns = xrn_dict[registry_hrn]
            if registry_hrn != api.hrn:
                credential = api.getCredential()
                interface = api.registries[registry_hrn]
                server_proxy = api.server_proxy(interface, credential)
                # should propagate the details flag but that's not supported in the xmlrpc interface yet
                #peer_records = server_proxy.Resolve(xrns, credential,type, details=details)
                peer_records = server_proxy.Resolve(xrns, credential)
                # pass foreign records as-is
                # previous code used to read
                # records.extend([SfaRecord(dict=record).as_dict() for record in peer_records])
                # not sure why the records coming through xmlrpc had to be processed at all
                records.extend(peer_records)

        # try resolving the remaining unfound records at the local registry
        local_hrns = list ( set(hrns).difference([record['hrn'] for record in records]) )
        # 
        local_records = dbsession.query(RegRecord).filter(RegRecord.hrn.in_(local_hrns))
        if type:
            local_records = local_records.filter_by(type=type)
        local_records=local_records.all()

        for local_record in local_records:
            augment_with_sfa_builtins (local_record)

        logger.info("Resolve, (details=%s,type=%s) local_records=%s "%(details,type,local_records))
        local_dicts = [ record.__dict__ for record in local_records ]

        if details:
            # in details mode we get as much info as we can, which involves contacting the 
            # testbed for getting implementation details about the record
            self.driver.augment_records_with_testbed_info(local_dicts)
            # also we fill the 'url' field for known authorities
            # used to be in the driver code, sounds like a poorman thing though
            def solve_neighbour_url (record):
                if not record.type.startswith('authority'): return
                hrn=record.hrn
                for neighbour_dict in [ api.aggregates, api.registries ]:
                    if hrn in neighbour_dict:
                        record.url=neighbour_dict[hrn].get_url()
                        return
            for record in local_records: 
                solve_neighbour_url (record)

        # convert local record objects to dicts for xmlrpc
        # xxx somehow here calling dict(record) issues a weird error
        # however record.todict() seems to work fine
        # records.extend( [ dict(record) for record in local_records ] )
        records.extend( [ record.todict(exclude_types=[InstrumentedList]) for record in local_records ] )

        if not records:
            raise RecordNotFound(str(hrns))

        return records

