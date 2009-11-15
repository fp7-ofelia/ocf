#! /usr/bin/env python

# sfi -- slice-based facility interface

import sys
import os, os.path
import tempfile
import traceback
from types import StringTypes, ListType
from optparse import OptionParser

from sfa.trust.certificate import Keypair, Certificate
from sfa.trust.credential import Credential

from sfa.util.geniclient import GeniClient
from sfa.util.record import *
from sfa.util.rspec import Rspec
from sfa.util.xmlrpcprotocol import ServerException
from sfa.util.config import Config

class Sfi:
    
    slicemgr = None
    registry = None
    user = None
    authority = None
    options = None
    
    #
    # Establish Connection to SliceMgr and Registry Servers
    #
    def set_servers(self):
       config_file = self.options.sfi_dir + os.sep + "sfi_config"
       try:
          config = Config (config_file)
       except:
          print "Failed to read configuration file",config_file
          print "Make sure to remove the export clauses and to add quotes"
          if not self.options.verbose:
             print "Re-run with -v for more details"
          else:
             traceback.print_exc()
          sys.exit(1)
    
       errors=0
       # Set SliceMgr URL
       if (self.options.sm is not None):
          sm_url = self.options.sm
       elif hasattr(config,"SFI_SM"):
          sm_url = config.SFI_SM
       else:
          print "You need to set e.g. SFI_SM='http://your.slicemanager.url:12347/' in %s"%config_file
          errors +=1 
    
       # Set Registry URL
       if (self.options.registry is not None):
          reg_url = self.options.registry
       elif hasattr(config,"SFI_REGISTRY"):
          reg_url = config.SFI_REGISTRY
       else:
          print "You need to set e.g. SFI_REGISTRY='http://your.registry.url:12345/' in %s"%config_file
          errors +=1 
    
       # Set user HRN
       if (self.options.user is not None):
          self.user = self.options.user
       elif hasattr(config,"SFI_USER"):
          self.user = config.SFI_USER
       else:
          print "You need to set e.g. SFI_USER='plc.princeton.username' in %s"%config_file
          errors +=1 
    
       # Set authority HRN
       if (self.options.auth is not None):
          self.authority = self.options.auth
       elif hasattr(config,"SFI_AUTH"):
          self.authority = config.SFI_AUTH
       else:
          print "You need to set e.g. SFI_AUTH='plc.princeton' in %s"%config_file
          errors +=1 
    
       if errors:
          sys.exit(1)
    
       if self.options.verbose :
          print "Contacting Slice Manager at:", sm_url
          print "Contacting Registry at:", reg_url
    
       # Get key and certificate
       key_file = self.get_key_file()
       cert_file = self.get_cert_file(key_file)
       self.key_file = key_file
       self.cert_file = cert_file 
       # Establish connection to server(s)
       self.slicemgr = GeniClient(sm_url, key_file, cert_file, self.options.protocol)
       self.registry = GeniClient(reg_url, key_file, cert_file, self.options.protocol)
       return
    
    #
    # Get various credential and spec files
    #
    # Establishes limiting conventions
    #   - conflates MAs and SAs
    #   - assumes last token in slice name is unique
    #
    # Bootstraps credentials
    #   - bootstrap user credential from self-signed certificate
    #   - bootstrap authority credential from user credential
    #   - bootstrap slice credential from user credential
    #
    
    def get_leaf(self,name):
       parts = name.split(".")
       return parts[-1]
    
    def get_key_file(self):
       file = os.path.join(self.options.sfi_dir, self.get_leaf(self.user) + ".pkey")
       if (os.path.isfile(file)):
          return file
       else:
          print "Key file", file, "does not exist"
          sys.exit(-1)
       return
    
    def get_cert_file(self,key_file):
    
       file = os.path.join(self.options.sfi_dir, self.get_leaf(self.user) + ".cert")
       if (os.path.isfile(file)):
          return file
       else:
          k = Keypair(filename = key_file)
          cert = Certificate(subject=self.user)
          cert.set_pubkey(k)
          cert.set_issuer(k, self.user)
          cert.sign()
          if self.options.verbose :
             print "Writing self-signed certificate to", file
          cert.save_to_file(file)
          return file
    
    def get_user_cred(self):
       file = os.path.join(self.options.sfi_dir, self.get_leaf(self.user) + ".cred")
       if (os.path.isfile(file)):
          user_cred = Credential(filename=file)
          return user_cred
       else:
          # bootstrap user credential
          user_cred = self.registry.get_credential(None, "user", self.user)
          if user_cred:
             user_cred.save_to_file(file, save_parents=True)
             if self.options.verbose:
                print "Writing user credential to", file
             return user_cred
          else:
             print "Failed to get user credential"
             sys.exit(-1)
    
    def get_auth_cred(self):
    
       if not self.authority:
          print "no authority specified. Use -a or set SF_AUTH"
          sys.exit(-1)
    
       file = os.path.join(self.options.sfi_dir, self.get_leaf("authority") +".cred")
       if (os.path.isfile(file)):
          auth_cred = Credential(filename=file)
          return auth_cred
       else:
          # bootstrap authority credential from user credential
          user_cred = self.get_user_cred()
          auth_cred = self.registry.get_credential(user_cred, "authority", self.authority)
          if auth_cred:
             auth_cred.save_to_file(file, save_parents=True)
             if self.options.verbose:
                print "Writing authority credential to", file
             return auth_cred
          else:
             print "Failed to get authority credential"
             sys.exit(-1)
    
    def get_slice_cred(self,name):
       file = os.path.join(self.options.sfi_dir, "slice_" + self.get_leaf(name) + ".cred")
       if (os.path.isfile(file)):
          slice_cred = Credential(filename=file)
          return slice_cred
       else:
          # bootstrap slice credential from user credential
          user_cred = self.get_user_cred()
          slice_cred = self.registry.get_credential(user_cred, "slice", name)
          if slice_cred:
             slice_cred.save_to_file(file, save_parents=True)
             if self.options.verbose:
                print "Writing slice credential to", file
             return slice_cred
          else:
             print "Failed to get slice credential"
             sys.exit(-1)
    
    def delegate_cred(self,cred, hrn, type = 'authority'):
        # the gid and hrn of the object we are delegating
        object_gid = cred.get_gid_object()
        object_hrn = object_gid.get_hrn()
        cred.set_delegate(True)
        if not cred.get_delegate():
            raise Exception, "Error: Object credential %(object_hrn)s does not have delegate bit set" % locals()
           
    
        records = self.registry.resolve(cred, hrn)
        records = self.filter_records(type, records)
        
        if not records:
            raise Exception, "Error: Didn't find a %(type)s record for %(hrn)s" % locals()
    
        # the gid of the user who will be delegated too
        delegee_gid = records[0].get_gid_object()
        delegee_hrn = delegee_gid.get_hrn()
        
        # the key and hrn of the user who will be delegating
        user_key = Keypair(filename = self.get_key_file())
        user_hrn = cred.get_gid_caller().get_hrn()
    
        dcred = Credential(subject=object_hrn + " delegated to " + delegee_hrn)
        dcred.set_gid_caller(delegee_gid)
        dcred.set_gid_object(object_gid)
        dcred.set_privileges(cred.get_privileges())
        dcred.set_delegate(True)
        dcred.set_pubkey(object_gid.get_pubkey())
        dcred.set_issuer(user_key, user_hrn)
        dcred.set_parent(cred)
        dcred.encode()
        dcred.sign()
    
        return dcred
    
    def get_rspec_file(self,rspec):
       if (os.path.isabs(rspec)):
          file = rspec
       else:
          file = os.path.join(self.options.sfi_dir, rspec)
       if (os.path.isfile(file)):
          return file
       else:
          print "No such rspec file", rspec
          sys.exit(1)
    
    def get_record_file(self,record):
       if (os.path.isabs(record)):
          file = record
       else:
          file = os.path.join(self.options.sfi_dir, record)
       if (os.path.isfile(file)):
          return file
       else:
          print "No such registry record file", record
          sys.exit(1)
    
    def load_publickey_string(self,fn):
       f = file(fn,"r")
       key_string = f.read()
    
       # if the filename is a private key file, then extract the public key
       if "PRIVATE KEY" in key_string:
           outfn = tempfile.mktemp()
           cmd = "openssl rsa -in " + fn + " -pubout -outform PEM -out " + outfn
           os.system(cmd)
           f = file(outfn, "r")
           key_string = f.read()
           os.remove(outfn)
    
       return key_string
    #
    # Generate sub-command parser
    #
    def create_cmd_parser(self,command, additional_cmdargs = None):
       cmdargs = {"list": "name",
                  "show": "name",
                  "remove": "name",
                  "add": "record",
                  "update": "record",
                  "aggregates": "[name]",
                  "registries": "[name]",   
                  "slices": "",
                  "resources": "[name]",
                  "create": "name rspec",
                  "delete": "name",
                  "reset": "name",
                  "start": "name",
                  "stop": "name",
                  "delegate": "name"
                 }
    
       if additional_cmdargs:
          cmdargs.update(additional_cmdargs)
    
       if command not in cmdargs:
          print "Invalid command\n"
          print "Commands: ",
          for key in cmdargs.keys():
              print key+",",
          print ""
          sys.exit(2)
    
       parser = OptionParser(usage="sfi [sfi_options] %s [options] %s" \
          % (command, cmdargs[command]))

       if command in ("resources"):
           parser.add_option("-f", "--format", dest="format",type="choice",
                             help="display format ([xml]|dns|ip)",default="xml",
                             choices=("xml","dns","ip"))
           parser.add_option("-a", "--aggregate", dest="aggregate",
                             default=None, help="aggregate hrn")  
    
       if command in ("create"):
           parser.add_option("-a", "--aggregate", dest="aggregate",default=None,
                             help="aggregate hrn") 
 
       if command in ("list", "show", "remove"):
          parser.add_option("-t", "--type", dest="type",type="choice",
                            help="type filter ([all]|user|slice|sa|ma|node|aggregate)",
                            choices=("all","user","slice","sa","ma","node","aggregate"),
                            default="all")

       if command in ("resources", "show", "list"):
          parser.add_option("-o", "--output", dest="file",
                            help="output XML to file", metavar="FILE", default=None)

       if command in ("show", "list"):
           parser.add_option("-f", "--format", dest="format", type="choice", 
                             help="display format ([text]|xml)",default="text", 
                             choices=("text","xml")) 

       if command in ("delegate"):
          parser.add_option("-u", "--user",
                            action="store_true", dest="delegate_user", default=False,
                            help="delegate user credential")
          parser.add_option("-s", "--slice", dest="delegate_slice",
                            help="delegate slice credential", metavar="HRN", default=None)
       return parser
    
    def create_parser(self):

       # Generate command line parser
       parser = OptionParser(usage="sfi [options] command [command_options] [command_args]",
                             description="Commands: list,show,remove,add,update,nodes,slices,resources,create,delete,start,stop,reset")
       parser.add_option("-r", "--registry", dest="registry",
                         help="root registry", metavar="URL", default=None)
       parser.add_option("-s", "--slicemgr", dest="sm",
                         help="slice manager", metavar="URL", default=None)
       default_sfi_dir=os.path.expanduser("~/.sfi/")
       parser.add_option("-d", "--dir", dest="sfi_dir",
                         help="config & working directory - default is " + default_sfi_dir,
                         metavar="PATH", default = default_sfi_dir)
       parser.add_option("-u", "--user", dest="user",
                         help="user name", metavar="HRN", default=None)
       parser.add_option("-a", "--auth", dest="auth",
                         help="authority name", metavar="HRN", default=None)
       parser.add_option("-v", "--verbose",
                         action="store_true", dest="verbose", default=False,
                         help="verbose mode")
       parser.add_option("-p", "--protocol",
                         dest="protocol", default="xmlrpc",
                         help="RPC protocol (xmlrpc or soap)")
       parser.disable_interspersed_args()
    
       return parser
    
    def dispatch(self,command, cmd_opts, cmd_args):
       getattr(self,command)(cmd_opts, cmd_args)
    
    #
    # Following functions implement the commands
    #
    # Registry-related commands
    #
    
    # list entires in named authority registry
    def list(self,opts, args):
       user_cred = self.get_user_cred()
       try:
          list = self.registry.list(user_cred, args[0])
       except IndexError:
          raise Exception, "Not enough parameters for the 'list' command"
          
       # filter on person, slice, site, node, etc.  
       # THis really should be in the self.filter_records funct def comment...
       list = self.filter_records(opts.type, list)
       for record in list:
           print "%s (%s)" % (record['hrn'], record['type'])     
       if opts.file:
           self.save_records_to_file(opts.file, list)
       return
    
    # show named registry record
    def show(self,opts, args):
       user_cred = self.get_user_cred()
       records = self.registry.resolve(user_cred, args[0])
       records = self.filter_records(opts.type, records)
       if not records:
          print "No record of type", opts.type
       for record in records:
           if record['type'] in ['user']:
               record = UserRecord(dict = record)
           elif record['type'] in ['slice']:
               record = SliceRecord(dict = record)
           elif record['type'] in ['node']:
               record = NodeRecord(dict = record)
           elif record['type'] in ['authority', 'ma', 'sa']:
               record = AuthorityRecord(dict = record)
           else:
               record = GeniRecord(dict = record)
           if (opts.format=="text"): 
               record.dump()  
           else: 
               print record.save_to_string() 
       
       if opts.file:
           self.save_records_to_file(opts.file, records)
       return
    
    def delegate(self,opts, args):
       user_cred = self.get_user_cred()
       if opts.delegate_user:
           object_cred = user_cred
       elif opts.delegate_slice:
           object_cred = self.get_slice_cred(opts.delegate_slice)
       else:
           print "Must specify either --user or --slice <hrn>"
           return
    
       # the gid and hrn of the object we are delegating
       object_gid = object_cred.get_gid_object()
       object_hrn = object_gid.get_hrn()
    
       if not object_cred.get_delegate():
           print "Error: Object credential", object_hrn, "does not have delegate bit set"
           return
    
       records = self.registry.resolve(user_cred, args[0])
       records = self.filter_records("user", records)
    
       if not records:
           print "Error: Didn't find a user record for", args[0]
           return
    
       # the gid of the user who will be delegated too
       delegee_gid = records[0].get_gid_object()
       delegee_hrn = delegee_gid.get_hrn()
    
       # the key and hrn of the user who will be delegating
       user_key = Keypair(filename = self.get_key_file())
       user_hrn = user_cred.get_gid_caller().get_hrn()
    
       dcred = Credential(subject=object_hrn + " delegated to " + delegee_hrn)
       dcred.set_gid_caller(delegee_gid)
       dcred.set_gid_object(object_gid)
       dcred.set_privileges(object_cred.get_privileges())
       dcred.set_delegate(True)
       dcred.set_pubkey(object_gid.get_pubkey())
       dcred.set_issuer(user_key, user_hrn)
       dcred.set_parent(object_cred)
       dcred.encode()
       dcred.sign()
    
       if opts.delegate_user:
           dest_fn = os.path.join(self.options.sfi_dir, self.get_leaf(delegee_hrn) + "_" 
                                  + self.get_leaf(object_hrn) + ".cred")
       elif opts.delegate_slice:
           dest_fn = os.path_join(self.options.sfi_dir, self.get_leaf(delegee_hrn) + "_slice_" 
                                  + self.get_leaf(object_hrn) + ".cred")
    
       dcred.save_to_file(dest_fn, save_parents = True)
    
       print "delegated credential for", object_hrn, "to", delegee_hrn, "and wrote to", dest_fn
    
    # removed named registry record
    #   - have to first retrieve the record to be removed
    def remove(self,opts, args):
       auth_cred = self.get_auth_cred()
       type = opts.type 
       if type in ['all']:
           type = '*'                   
       return self.registry.remove(auth_cred, type, args[0])
    
    # add named registry record
    def add(self,opts, args):
       auth_cred = self.get_auth_cred()
       rec_file = self.get_record_file(args[0])
       record = self.load_record_from_file(rec_file)
    
       return self.registry.register(auth_cred, record)
    
    # update named registry entry
    def update(self,opts, args):
       user_cred = self.get_user_cred()
       rec_file = self.get_record_file(args[0])
       record = self.load_record_from_file(rec_file)
       if record.get_type() == "user":
           if record.get_name() == user_cred.get_gid_object().get_hrn():
              cred = user_cred
           else:
              cred = self.get_auth_cred()
       elif record.get_type() in ["slice"]:
           try:
               cred = self.get_slice_cred(record.get_name())
           except ServerException, e:
               # XXX smbaker -- once we have better error return codes, update this
               # to do something better than a string compare
               if "Permission error" in e.args[0]:
                   cred = self.get_auth_cred()
               else:
                   raise
       elif record.get_type() in ["authority"]:
           cred = self.get_auth_cred()
       elif record.get_type() == 'node':
            cred = self.get_auth_cred()
       else:
           raise "unknown record type" + record.get_type()
       return self.registry.update(cred, record)
   
    
    def aggregates(self, opts, args):
        user_cred = self.get_user_cred()
        hrn = None
        if args: 
            hrn = args[0]
        
        result = self.registry.get_aggregates(user_cred, hrn)
        self.display_list(result)
        return 

    def registries(self, opts, args):
        user_cred = self.get_user_cred()
        hrn = None
        if args:
            hrn = args[0]
        
        result = self.registry.get_registries(user_cred, hrn)
        self.display_list(result)
        return
 
    #
    # Slice-related commands
    #
    
    # list available nodes -- use 'resources' w/ no argument instead

    # list instantiated slices
    def slices(self,opts, args):
       user_cred = self.get_user_cred()
       results = self.slicemgr.get_slices(user_cred)
       self.display_list(results)
       return
    
    # show rspec for named slice
    def resources(self,opts, args):
       user_cred = self.get_user_cred()
       server = self.slicemgr
       if opts.aggregate:
            aggregates = self.registry.get_aggregates(user_cred, opts.aggregate)
            if not aggregates:
                raise Exception, "No such aggregate %s" % opts.aggregate
            aggregate = aggregates[0]
            url = "http://%s:%s" % (aggregate['addr'], aggregate['port'])     
            server = GeniClient(url, self.key_file, self.cert_file, self.options.protocol)
       if args:
            slice_cred = self.get_slice_cred(args[0])
            result = server.get_resources(slice_cred, args[0])
       else:
            result = server.get_resources(user_cred)
       format = opts.format
       
       self.display_rspec(result, format)
       if (opts.file is not None):
          self.save_rspec_to_file(result, opts.file)
       return
    
    # created named slice with given rspec
    def create(self,opts, args):
       slice_hrn = args[0]
       user_cred = self.get_user_cred()
       slice_cred = self.get_slice_cred(slice_hrn)
       rspec_file = self.get_rspec_file(args[1])
       rspec=open(rspec_file).read()
       server = self.slicemgr
       if opts.aggregate:
           aggregates = self.registry.get_aggregates(user_cred, opts.aggregate)
           if not aggregates:
               raise Exception, "No such aggregate %s" % opts.aggregate
           aggregate = aggregates[0]
           url = "http://%s:%s" % (aggregate['addr'], aggregate['port'])
           server = GeniClient(url, self.key_file, self.cert_file, self.options.protocol)
       return server.create_slice(slice_cred, slice_hrn, rspec)
    
    # delete named slice
    def delete(self,opts, args):
       slice_hrn = args[0]
       slice_cred = self.get_slice_cred(slice_hrn)
       
       return self.slicemgr.delete_slice(slice_cred, slice_hrn)
    
    # start named slice
    def start(self,opts, args):
       slice_hrn = args[0]
       slice_cred = self.get_slice_cred(args[0])
       return self.slicemgr.start_slice(slice_cred, slice_hrn)
    
    # stop named slice
    def stop(self,opts, args):
       slice_hrn = args[0]
       slice_cred = self.get_slice_cred(args[0])
       return self.slicemgr.stop_slice(slice_cred, slice_hrn)
    
    # reset named slice
    def reset(self,opts, args):
       slice_hrn = args[0]
       slice_cred = self.get_slice_cred(args[0])
       return self.slicemgr.reset_slice(slice_cred, slice_hrn)
    
    #
    #
    # Display, Save, and Filter RSpecs and Records
    #   - to be replace by EMF-generated routines
    #
    #
    
    def display_rspec(self,rspec, format = 'rspec'):
        if format in ['dns']:
            spec = Rspec()
            spec.parseString(rspec)
            hostnames = []
            nodespecs = spec.getDictsByTagName('NodeSpec')
            for nodespec in nodespecs:
                if nodespec.has_key('name') and nodespec['name']:
                    if isinstance(nodespec['name'], ListType):
                        hostnames.extend(nodespec['name'])
                    elif isinstance(nodespec['name'], StringTypes):
                        hostnames.append(nodespec['name'])
            result = hostnames
        elif format in ['ip']:
            spec = Rspec()
            spec.parseString(rspec)
            ips = []
            ifspecs = spec.getDictsByTagName('IfSpec')
            for ifspec in ifspecs:
                if ifspec.has_key('addr') and ifspec['addr']:
                    ips.append(ifspec['addr'])
            result = ips 
        else:     
            result = rspec
    
        print result
        return
    
    def display_list(self,results):
        for result in results:
            print result
    
    def save_rspec_to_file(self,rspec, filename):
       if not filename.startswith(os.sep):
           filename = self.options.sfi_dir + filename
       if not filename.endswith(".rspec"):
           filename = filename + ".rspec"
    
       f = open(filename, 'w')
       f.write(rspec)
       f.close()
       return
    
    def display_records(self,recordList, dump = False):
       ''' Print all fields in the record'''
       for record in recordList:
          self.display_record(record, dump)
    
    def display_record(self,record, dump = False):
       if dump:
           record.dump()
       else:
           info = record.getdict()
           print "%s (%s)" % (info['hrn'], info['type'])
       return
    
    def filter_records(self,type, records):
       filtered_records = []
       for record in records:
           if (record.get_type() == type) or (type == "all"):
               filtered_records.append(record)
       return filtered_records
    
    def save_records_to_file(self,filename, recordList):
       index = 0
       for record in recordList:
           if index>0:
               self.save_record_to_file(filename + "." + str(index), record)
           else:
               self.save_record_to_file(filename, record)
           index = index + 1
    
    def save_record_to_file(self,filename, record):
       if not filename.startswith(os.sep):
           filename = self.options.sfi_dir + filename
       str = record.save_to_string()
       file(filename, "w").write(str)
       return
    
    def load_record_from_file(self,filename):
       str = file(filename, "r").read()
       record = GeniRecord(string=str)
       return record
    
    #
    # Main: parse arguments and dispatch to command
    #
    def main(self):
    
       parser = self.create_parser()
       (options, args) = parser.parse_args()
       self.options = options
    
       if len(args) <= 0:
            print "No command given. Use -h for help."
            return -1
    
       command = args[0]
       (cmd_opts, cmd_args) = self.create_cmd_parser(command).parse_args(args[1:])
       if self.options.verbose :
          print "Registry %s, sm %s, dir %s, user %s, auth %s" % (options.registry,
                                                                   options.sm,
                                                                   options.sfi_dir,
                                                                   options.user,
                                                                   options.auth)
          print "Command %s" %command
          if command in ("resources"):
             print "resources cmd_opts %s" %cmd_opts.format
          elif command in ("list","show","remove"):
             print "cmd_opts.type %s" %cmd_opts.type
          print "cmd_args %s" %cmd_args
    
       self.set_servers()
    
       try:
          self.dispatch(command, cmd_opts, cmd_args)
       except KeyError:
          raise 
          print "Command not found:", command
          sys.exit(1)
    
       return
    
if __name__=="__main__":
   Sfi().main()
