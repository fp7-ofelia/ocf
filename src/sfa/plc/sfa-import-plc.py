#!/usr/bin/python
#
### $Id: sfa-import-plc.py 15357 2009-10-16 21:27:47Z tmack $
### $URL: http://svn.planet-lab.org/svn/sfa/trunk/sfa/plc/sfa-import-plc.py $
#
##
# Import PLC records into the Geni database. It is indended that this tool be
# run once to create Geni records that reflect the current state of the
# planetlab database.
#
# The import tool assumes that the existing PLC hierarchy should all be part
# of "planetlab.us" (see the root_auth and level1_auth variables below).
#
# Public keys are extracted from the users' SSH keys automatically and used to
# create GIDs. This is relatively experimental as a custom tool had to be
# written to perform conversion from SSH to OpenSSL format. It only supports
# RSA keys at this time, not DSA keys.
##

import getopt
import sys
import tempfile

from sfa.util.record import *
from sfa.util.genitable import GeniTable
from sfa.util.misc import *
from sfa.util.config import Config
from sfa.util.report import trace, error
from sfa.trust.certificate import convert_public_key, Keypair
from sfa.trust.trustedroot import *
from sfa.trust.hierarchy import *
from sfa.plc.api import *
from sfa.util.geniclient import *
from sfa.trust.gid import create_uuid
from sfa.plc.sfaImport import *



def process_options():
   global hrn

   (options, args) = getopt.getopt(sys.argv[1:], '', [])
   for opt in options:
       name = opt[0]
       val = opt[1]


def load_keys(filename):
    keys = {}
    tmp_dict = {}
    try:
        execfile(filename, tmp_dict)
        if 'keys' in tmp_dict:
            keys = tmp_dict['keys']
        return keys
    except:
        return keys

def save_keys(filename, keys):
    f = open(filename, 'w')
    f.write("keys = %s" % str(keys))
    f.close()

def main():
    process_options()
    config = Config()
    if not config.SFA_REGISTRY_ENABLED:
        sys.exit(0)
    root_auth = config.SFA_REGISTRY_ROOT_AUTH
    level1_auth = config.SFA_REGISTRY_LEVEL1_AUTH
    keys_filename = config.config_path + os.sep + 'person_keys.py' 
    sfaImporter = sfaImport()
    shell = sfaImporter.shell
    plc_auth = sfaImporter.plc_auth 
    AuthHierarchy = sfaImporter.AuthHierarchy
    TrustedRoots = sfaImporter.TrustedRoots
    table = GeniTable()
    if not table.exists():
        table.create()

    if not level1_auth or level1_auth in ['']:
        level1_auth = None
    
    print "Import: creating top level authorities"
    if not level1_auth:
        sfaImporter.create_top_level_auth_records(root_auth)
        import_auth = root_auth
    else:
        if not AuthHierarchy.auth_exists(level1_auth):
            AuthHierarchy.create_auth(level1_auth)
        sfaImporter.create_top_level_auth_records(level1_auth)
        import_auth = level1_auth

    print "Import: adding", import_auth, "to trusted list"
    authority = AuthHierarchy.get_auth_info(import_auth)
    TrustedRoots.add_gid(authority.get_gid_object())

    if ".vini" in import_auth and import_auth.endswith('vini'):
        # create a fake internet2 site first
        i2site = {'name': 'Internet2', 'abbreviated_name': 'I2',
                    'login_base': 'internet2', 'site_id': -1}
        sfaImporter.import_site(import_auth, i2site)
   
    # create dict of all existing sfa records
    existing_records = {}
    existing_hrns = []
    key_ids = []
    person_keys = {} 
    results = table.find()
    for result in results:
        existing_records[(result['hrn'], result['type'])] = result
        existing_hrns.append(result['hrn']) 
            
    # Get all plc sites
    sites = shell.GetSites(plc_auth, {'peer_id': None})
    sites_dict = {}
    for site in sites:
        sites_dict[site['login_base']] = site 
    
    # Get all plc users
    persons = shell.GetPersons(plc_auth, {'peer_id': None}, ['person_id', 'email', 'key_ids', 'site_ids'])
    persons_dict = {}
    for person in persons:
        persons_dict[person['person_id']] = person
        key_ids.extend(person['key_ids'])

    # Get all public keys
    keys = shell.GetKeys(plc_auth, {'peer_id': None, 'key_id': key_ids})
    keys_dict = {}
    for key in keys:
        keys_dict[key['key_id']] = key['key']

    # create a dict of person keys keyed on key_id 
    old_person_keys = load_keys(keys_filename)
    for person in persons:
        pubkeys = []
        for key_id in person['key_ids']:
            pubkeys.append(keys_dict[key_id])
        person_keys[person['person_id']] = pubkeys

    # Get all plc nodes  
    nodes = shell.GetNodes(plc_auth, {'peer_id': None}, ['node_id', 'hostname', 'site_id'])
    nodes_dict = {}
    for node in nodes:
        nodes_dict[node['node_id']] = node

    # Get all plc slices
    slices = shell.GetSlices(plc_auth, {'peer_id': None}, ['slice_id', 'name'])
    slices_dict = {}
    for slice in slices:
        slices_dict[slice['slice_id']] = slice

    # start importing 
    for site in sites:
        site_hrn = import_auth + "." + site['login_base']
        # import if hrn is not in list of existing hrns or if the hrn exists
        # but its not a site record
        if site_hrn not in existing_hrns or \
           (site_hrn, 'authority') not in existing_records:
            site_hrn = sfaImporter.import_site(import_auth, site)
             
        # import node records
        for node_id in site['node_ids']:
            if node_id not in nodes_dict:
                continue 
            node = nodes_dict[node_id]
            hrn =  hostname_to_hrn(import_auth, site['login_base'], node['hostname'])
            if hrn not in existing_hrns or \
               (hrn, 'node') not in existing_records:
                sfaImporter.import_node(site_hrn, node)

        # import slices
        for slice_id in site['slice_ids']:
            if slice_id not in slices_dict:
                continue 
            slice = slices_dict[slice_id]
            hrn = slicename_to_hrn(import_auth, slice['name'])
            if hrn not in existing_hrns or \
               (hrn, 'slice') not in existing_records:
                sfaImporter.import_slice(site_hrn, slice)      

        # import persons
        for person_id in site['person_ids']:
            if person_id not in persons_dict:
                continue 
            person = persons_dict[person_id]
            hrn = email_to_hrn(site_hrn, person['email'])
            old_keys = []
            new_keys = []
            if person_id in old_person_keys:
                old_keys = old_person_keys[person_id]
            if person_id in person_keys:
                new_keys = person_keys[person_id]
            update_record = False
            for key in new_keys:
                if key not in old_keys:
                    update_record = True 

            if hrn not in existing_hrns or \
               (hrn, 'user') not in existing_records or update_record:
                sfaImporter.import_person(site_hrn, person)

    # remove stale records    
    for (record_hrn, type) in existing_records.keys():
        record = existing_records[(record_hrn, type)]
        # if this is the interface name dont do anything
        if record_hrn == import_auth or record['peer_authority']:
            continue
        # dont delete vini's internet2 placeholdder record
        # normally this would be deleted becuase it does not have a plc record 
        if ".vini" in import_auth and import_auth.endswith('vini') and \
           record_hrn.endswith("internet2"):     
            continue

        found = False
        
        if type == 'authority':    
            for site in sites:
                site_hrn = import_auth + "." + site['login_base']
                if site_hrn == record_hrn and site['site_id'] == record['pointer']:
                    found = True
                    break

        elif type == 'user':
            login_base = get_leaf(get_authority(record_hrn))
            username = get_leaf(record_hrn)
            if login_base in sites_dict:
                site = sites_dict[login_base]
                for person in persons:
                    tmp_username = person['email'].split("@")[0]
                    alt_username = person['email'].split("@")[0].replace(".", "_")
                    if username in [tmp_username, alt_username] and \
                       site['site_id'] in person['site_ids'] and \
                       person['person_id'] == record['pointer']:
                        found = True
                        break
        
        elif type == 'slice':
            slicename = hrn_to_pl_slicename(record_hrn)
            for slice in slices:
                if slicename == slice['name'] and \
                   slice['slice_id'] == record['pointer']:
                    found = True
                    break    
 
        elif type == 'node':
            login_base = get_leaf(get_authority(record_hrn))
            nodename = get_leaf(record_hrn)
            if login_base in sites_dict:
                site = sites_dict[login_base]
                for node in nodes:
                    tmp_nodename = node['hostname'].split(".")[0]
                    if tmp_nodename == nodename and \
                       node['site_id'] == site['site_id'] and \
                       node['node_id'] == record['pointer']:
                        found = True
                        break  
        else:
            continue 
        
        if not found:
            trace("Import: Removing %s %s" % (type,  record_hrn))
            record_object = existing_records[(record_hrn, type)]
            sfaImporter.delete_record(record_hrn, type) 
                                   
    # save pub keys
    trace('saving current pub keys')
    save_keys(keys_filename, person_keys)                
        
if __name__ == "__main__":
    main()
