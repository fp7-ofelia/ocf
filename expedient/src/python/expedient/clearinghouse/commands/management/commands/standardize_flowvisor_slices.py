from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.sites.models import Site
#from django.conf.settings import SITE_DOMAIN as CORRECT_SITE_DOMAIN
from expedient.clearinghouse.defaultsettings.site import SITE_DOMAIN as SITE_DOMAIN_DEFAULT
#from expedient.clearinghouse.localsettings import SITE_DOMAIN as SITE_DOMAIN_CUSTOM
from expedient.clearinghouse.slice.models import Slice
from expedient.common.utils.mail import send_mail
try:
    import cpickle as pickle
except:
    import pickle
import os
import subprocess

class Command(BaseCommand):
    args = "stop | start"
    help = "Standardizes those FlowVisor slice names that have a different suffix."

    def handle(self, *args, **options):
        """
        Stops and then starts conflictive slices (with non-standard name) at
        Flowvisor.
        Used in conjunction **and before** the script with the same name at opt-in.
        
        Flow:
            1. Expedient: manage.py standardize_flowvisor_slices stop
            2. Expedient: manage.py standardize_flowvisor_slices start
            3. Opt-in: manage.py standardize_flowvisor_slices
        """
        try:
            if args[0] == "stop":
                self.stdout.write("%s\n" % self.stop_slices())
            elif args[0] == "start":
                self.stdout.write("%s\n" % self.start_slices())
            else:
                raise Exception
        except:
            self.stdout.write("\n\033[94m%s\n>  Arguments: %s\033[0m\n" % (self.help, self.args))

    def stop_slices(self):
        """
        First step: stop conflictive (non-standard) slices at FlowVisor.
        """
        ids = get_conflictive_slices_ids()
        errors = []
        slices = []
        slice_id = ""
        for iden in ids:
            slices.append(Slice.objects.get(id=iden))
        for slice in slices:
            # We get only OpenFlow aggregates to delete their slices at FV
            aggs = slice.aggregates.filter(leaf_name="OpenFlowAggregate")
            for agg in aggs:
                try:
                    slice_id = str(SITE_DOMAIN_DEFAULT) + "_" + str(slice.id)
                    print "Stopping ", slice_id, " at aggregate: ", str(agg)
                    agg.as_leaf_class().client.proxy.delete_slice(slice_id)
                    # Stopping slice at Expedient
                    slice.started = False
                    slice.save()
                except Exception as e:
                    message = """Could not fix the naming for slice with the following details:
name:\t\t %s
FlowVisor name:\t\t %s

The cause of the error is: %s. Please try to fix it manually""" % (slice.name, slice_id, e)
                    send_mail("OCF: error while standardizing Flowvisor slices", message, "OFELIA-noreply@fp7-ofelia.eu", [settings.ROOT_EMAIL])
                    errors.append(message)
        if errors:
            return "\033[93mFailure while stopping non-standard slices at FlowVisor: %s\033[0m" % str(errors)
        else:
            return "\033[92mSuccessfully stopped non-standard slices at FlowVisor\033[0m"

    def start_slices(self):
        """
        Second step: start previously conflictive (non-standard) slices at FlowVisor.
        """
        errors = []
        slices = []
        slice_ids = []
        # If 'conflictive_slice_ids' file exists, do the following.
        # Otherwise warn and skip.
        try:
            f = open("conflictive_slice_ids","r")
            ids = pickle.load(f)
            f.close()
            os.remove("conflictive_slice_ids")
            for iden in ids:
                slices.append(Slice.objects.get(id=iden))
            for slice in slices:
                aggs = slice.aggregates.filter(leaf_name="OpenFlowAggregate")
                slice_id = str(settings.SITE_DOMAIN) + "_" + str(iden)
                slice_ids.append(slice_id)
                for agg in aggs:
                    try:
                        agg.as_leaf_class().client.proxy.create_slice(slice_id, slice.project.name,slice.project.description,slice.name, slice.description, slice.openflowsliceinfo.controller_url, slice.owner.email, slice.openflowsliceinfo.password, agg.as_leaf_class()._get_slivers(slice))
                        # Starting slice at Expedient
                        slice.started = True
                        slice.save()
                    except Exception as e:
                        message = """Could not fix the naming for slice with the following details: name:\t\t %s
FlowVisor name:\t\t %s

The cause of the error is: %s. Please try to fix it manually""" % (slice.name, slice_id, e)
                        send_mail("OCF: error while standardizing Flowvisor slices", message, "OFELIA-noreply@fp7-ofelia.eu", [settings.ROOT_EMAIL])
                        errors.append(message)
            if errors:
                return "\033[93mFailure while starting previously non-standard slices at FlowVisor: %s\033[0m" % str(errors)
            else:
                f = open("slice_ids_to_grant_fs","w")
                pickle.dump(slice_ids, f)
                f.close()
                return "\033[92mSuccessfully started previously non-standard slices at FlowVisor\033[0m"
        except Exception as e:
            return "\033[93mCould not access file with slice IDs. Skipping...\033[0m"

def get_conflictive_slices_ids():

    def get_id(slice_id):
        i = len(slice_id) - 1 # Counting 0 index
        slice_id
        buffer = []
        while (i) > 0:
            try:
               int(slice_id[i])
               buffer.insert(0,str(slice_id[i]))
            except:
               break
            i -= 1
        return "".join(buffer)

    def write_in_file(ids):
        f = open("conflictive_slice_ids","w")
        #ids_data = "CONFLICTIVE_SLICES = ["
        #for identifier in ids:
        #    ids_data += "%s, " % str(identifier)
        #ids_data += "]"
        #f.write(ids_data)
        pickle.dump(ids,f)
        f.close()

    cmd = ['fvctl', '--passwd-file=/root/.fvpass']
    cmd.append('listSlices')
    p = subprocess.Popen(cmd, shell = False, stdin=subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    slices, err = p.communicate()

    if not err:
        # Adapt obtained result to a list of flowrules
        slices = slices.split("\n")
#        print slices
        ids = list()
#        current_site_domain = Site.objects.get_current().domain
        current_site_domain = SITE_DOMAIN_DEFAULT
        current_site_domain = current_site_domain.replace(".", "_").replace(":", "_").replace("=", "_").replace(" ", "_").replace("'","_")
#        print current_site_domain
#        if not SITE_DOMAIN_DEFAULT == SITE_DOMAIN_CUSTOM:
        if not SITE_DOMAIN_DEFAULT == settings.SITE_DOMAIN:
            for slice in slices:
#               if not str(slice) in str(current_site_domain):
#               if str(current_site_domain) not in str(slice):
                if str(current_site_domain) in str(slice):
                    id = get_id(slice)
                    if id:
                        ids.append(id)
    else:
        print "Error: %s" % str(err)
    write_in_file(ids)
    return ids

