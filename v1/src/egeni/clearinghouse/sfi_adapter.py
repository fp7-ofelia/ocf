from sfa.client import sfi
from django.conf import settings
from bsddb.test.test_all import path
import os
import tempfile

OPTIONS = "-d %s" % settings.SFI_CONF_DIR
EXEC = "%s/sfi.py %s" % (settings.SFI_EXEC_DIR, OPTIONS)

AUTH_HRN = "plc.openflow"
CH_HRN = "plc.openflow.seethara"

def run_cmd(cmd, args):
    '''Executes an SFI cmd with the given string argument'''
    os.system("%s %s %s" % (EXEC, cmd, args))

def put_in_tmp_file(str):
    '''dumps the contents of the string into a temp file
    and returns the file's name'''
    file, path = tempfile.mkstemp(text=True)
    file.write(str)
    file.close()
    return path

def get_slice_hrn(slice_id):
    '''Returns the human-readable name for the slice'''
    return "%s.%s" %(AUTH_HRN, slice_id)

def get_slice_name(slice_id):
    '''Returns the name as which the slice will be identified'''
    return "openflow_%s" % slice_id

def get_slice_record_string(slice_id):
    '''Returns a string that can be used as a record for the slice'''
    return '<record authority="%s" description="GEC6" hrn="%s" name="%s" type="slice" url="http://www.openflowswitch.org"><researcher>%s</researcher></record>' % (AUTH_HRN, get_slice_hrn(slice_id), get_slice_name(slice_id), CH_HRN)
 
def add_slice(slice_id):
    '''Add a slice to the PL registry'''
    path = put_in_tmp_file(get_slice_record_string(slice_id))
    run_cmd("add", path)
    os.unlink(path)
   
def remove_slice(slice_id):
    '''Remove a slice from the PL registry'''
    run_cmd("remove", get_slice_hrn(slice_id))

def reserve_slice(am_url, rspec, slice_id):
    '''Create a new slice and run it'''
    
    # TODO: Where does the url go?
    path = put_in_tmp_file(rspec)
    run_cmd("create", "%s %s" % (get_slice_hrn(slice_id), path))
    os.unlink(path)

# TODO: Finish this
