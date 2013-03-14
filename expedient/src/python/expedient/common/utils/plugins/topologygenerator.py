"""
Loads UI data for every plugin and returns a dictionary with all the data.

@date: Feb 20, 2013
@author: CarolinaFernandez
"""

from expedient.clearinghouse.resources.models import Resource
from django.core.mail import send_mail
from pluginloader import PluginLoader
from utils import Singleton

class TopologyGenerator():

    # Allows only one instance of this class
    __metaclass__ = Singleton

    @staticmethod
    def check_link_consistency(links, nodes, user, slice):
        """
        Checks consistency across links.
        In a link ( A - <link> - B), if any of the endpoints A or B
        do not exist, <link> is removed from the list.
        """
        inconsistent_links = []
        inconsistent_links_message = ""
        try:
            for index, link in enumerate(links):
                source_link = link['source']
                target_link = link['target']

                # Convert Resource IDs into D3.js IDs
                try:
                   link['source'] = TopologyGenerator.get_d3_index_from_resource_id(link['source'], nodes)
                   link['target'] = TopologyGenerator.get_d3_index_from_resource_id(link['target'], nodes)
                except Exception as e:
                    print "[WARNING] Problem retrieving D3 IDs inside TopologyGenerator. Details: %s" % str(e)

                # Check consistency. If node A or B do not exist, remove link
                if not (link['source'] != None and link['target'] != None):
                    source_node = Resource.objects.get(id = source_link)
                    target_node = Resource.objects.get(id = target_link)
                    inconsistent_links.append({"source_id": source_link, "source_name": source_node.name, "source_aggregate_id": source_node.aggregate.pk or "", "source_aggregate_name": source_node.aggregate.name or "", "target_id": target_link, "target_name": target_node.name or "", "target_aggregate_id": target_node.aggregate.pk or "", "target_aggregate_name": target_node.aggregate.name or ""})
                    links.pop(index)
        except Exception as e:
            print "[WARNING] Problem checking link consistency inside TopologyGenerator. Details: %s" % str(e)

        # Craft message to send via e-mail
        if inconsistent_links:
            for link in inconsistent_links:
                inconsistent_links_message += "SOURCE\n"
                inconsistent_links_message += "id: %s\nname: %s\naggregate id: %s\naggregate name: %s\n" % (link['source_id'], link['source_name'], link['source_aggregate_id'], link['source_aggregate_name'])
                inconsistent_links_message += "TARGET\n"
                inconsistent_links_message += "id: %s\nname: %s\naggregate id: %s\naggregate name: %s\n\n" % (link['target_id'], link['target_name'], link['target_aggregate_id'], link['target_aggregate_name'])
            try:
                from django.conf import settings
                # XXX DESCOMENTAR AL SUBIR A [PRE]PRODUCCION
#                send_mail(settings.EMAIL_SUBJECT_PREFIX + " Inconsistent links at slice '%s': Expedient" % str(slice.name), "Hi, Island Manager\n\nThis is a warning to notify about some inconsistent links within a topology. This may be happening because a plugin or Aggregate Manager references a node not present in the Aggregate Managers chosen for this slice.\n\nProject: %s\nSlice: %s\nProblematic links:\n\n%s" % (slice.project.name, slice.name, str(inconsistent_links)), from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[user.email],)
            except Exception as e:
                print "[WARNING] Problem sending e-mail to user '%s' (email: %s) with information about link inconsistency inside TopologyGenerator. Details: %s" % (user.username, user.email, str(e))

    @staticmethod
    def compute_number_islands(plugin_ui_data):
        return 3

    @staticmethod
    def get_d3_index_from_resource_id(resource_id, nodes):
        """
        Retrieves D3.js index node from the Resource ID.
        """
        d3_index = None
        print "resource id: %s" % str(resource_id)
        for index,node in enumerate(nodes):
            print "current node: %s" % str(node['value'])
            if str(resource_id) == str(node['value']):
                # If d3_index = None, return 'None' instead
                d3_index = index
                break
        print "new node ID: %s\n\n" % str(d3_index)
        return d3_index

    @staticmethod
    def node_get_adequate_group(node, assigned_groups):
        """
        Computes each node group through its aggregate manager ID.
        """
        try:
            if assigned_groups:
                for group in assigned_groups:
                    # If some other type was assigned the same group, increment group for current type
                    if node["aggregate"] == group["aggregate"]:
                        node["group"] = group["group"]
                    else:
                        node["group"] = assigned_groups[len(assigned_groups)-1]["group"]+1
            else:
                node["group"] = 0
            new_entry = {"group": node["group"], "aggregate": node["aggregate"]}
            # List of sublists: [aggregate, group]
            if new_entry not in assigned_groups:
                assigned_groups.append(new_entry)
        except:
            pass

    @staticmethod
    def load_ui_data(slice):
        """
        Calls the method 'get_ui_data' present in each plugin and mix the data for all
        plugins in a dictionary with nodes, links and total number of islands. This data
        will be sent to the topology visor, shown in the slice view.
        """
        plugin_ui_data = dict()
        plugin_ui_data['d3_nodes'] = []
        plugin_ui_data['d3_links'] = []
        plugin_ui_data['n_islands'] = 0
        plugin_ui_data_aux = dict()

        for plugin in PluginLoader.plugin_settings:
            try:
                plugin_method = "%s_get_ui_data" % str(plugin)
                plugin_import = PluginLoader.plugin_settings.get(plugin).get("general").get("get_ui_data_class")
                # Check that plugin does have a method to get UI data
                if plugin_import:
                    #exec(plugin_import)
                    tmp = __import__(plugin_import, globals(), locals(), ['get_ui_data'], 0)
                    locals()[plugin_method] = getattr(tmp, 'get_ui_data')
                    plugin_ui_data_aux = locals()[plugin_method](slice)
                    # Not so happy to need this post-processing after the plugin's data retrieval...
                    [ plugin_ui_data['d3_nodes'].append(node) for node in plugin_ui_data_aux.get("nodes", []) ]
                    [ plugin_ui_data['d3_links'].append(link) for link in plugin_ui_data_aux.get("links", []) ]
                    plugin_ui_data['n_islands'] = plugin_ui_data['n_islands'] + plugin_ui_data_aux.get("n_islands",0)

                    # Calculate each node's group depending on its aggregate manager ID. User should
                    # not have any knowledge of island and therefore should not set the group by itself
                    assigned_groups = []
                    for node in plugin_ui_data['d3_nodes']:
                        TopologyGenerator.node_get_adequate_group(node, assigned_groups)

                plugin_ui_data = dict(plugin_ui_data_aux.items() + plugin_ui_data.items())
                print "\n\n\n\n plugin_ui_data['d3_links']: %s\n\n\n\n" % str(plugin_ui_data['d3_links'])
                # TODO
#                plugin_ui_data['n_islands'] = TopologyGenerador.compute_number_islands(plugin_ui_data)
            except Exception as e:
                print "[ERROR] Problem loading UI data inside TopologyGenerator. Details: %s" % str(e)

        # Check link consistency
        from django.contrib.auth.models import User
        user = User.objects.get(username='carolina')
        # XXX DESCOMENTAR AL SUBIR A [PRE]PRODUCCION
#        user = User.objects.filter(is_superuser=True)[0]
        TopologyGenerator.check_link_consistency(plugin_ui_data['d3_links'], plugin_ui_data['d3_nodes'], user, slice)
        print "\n\n\n\n plugin_ui_data['d3_links'] (II): %s\n\n\n\n" % str(plugin_ui_data['d3_links'])

        return plugin_ui_data

