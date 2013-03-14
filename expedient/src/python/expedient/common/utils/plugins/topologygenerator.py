"""
Loads UI data for every plugin and returns a dictionary with all the data.

@date: Feb 20, 2013
@author: CarolinaFernandez
"""

from pluginloader import PluginLoader
from utils import Singleton

class TopologyGenerator():

    # Allows only one instance of this class
    __metaclass__ = Singleton

#    # Keeps track of every resource and its corresponding AM
#    am_resources = []

#    ### COMMON METHODS: BEGIN
#    @staticmethod
#    def craft_resource_id(resource_id, aggregate_id):
#        try:
#            return "%s-%s" % (str(aggregate_id), str(resource_id))
#        except:
#            return resource_id
#
#    @staticmethod
#    def get_aggregate_id(resource_id):
#        aggregate_id = 0
#        try:
#            aggregate_id = resource_id[:resource_id.index("-")] or 0
#        except:
#            pass
#        return aggregate_id
#
#    @staticmethod
#    def get_resource_id(resource_id):
#        try:
#            resource_id = resource_id[resource_id.index("-")+1:] or resource_id
#        except:
#            pass
#        return resource_id
#    ### COMMON METHODS: END

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
        #return [node, assigned_groups]
#        return node

#    @staticmethod
#    def resource_set_adequate_id(node, assigned_groups):
#        resource_id = node['value']
#        try:
#            resource_id = node['value']
#            aggregate_id = node['aggregate']
#            if aggregate_id not in [resources.get('a') for resources in TopologyGenerator.am_resources]:
#                TopologyGenerator.am_resources.append({"aggregate": aggregate_id, "resources": []})
#            TopologyGenerator.am_resources[aggregate_id]
#            node['value'] = TopologyGenerator.craft_resource_id(resource_id, aggregate_id)
#        except Exceptions as e:
#            pass
#        return resource_id

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

#        def get_d3_index_from_resource_id(resource_id):
#            """
#            Retrieves D3.js index node from the Resource ID.
#            """
##            print "Looking for resource_id: %s" % resource_id
#            d3_index = None
##            print "Looking into nodes..."
#            for index,node in enumerate(plugin_ui_data['d3_nodes']):
##                print "%s" % node['value']
#                if str(resource_id) == str(node['value']):
#                    # If d3_index = None, return 'None' instead
#                    d3_index = index
##                    print ">> found index: %s" % str(index)
#                    break
##            if not d3_index:
##                print "************** not found => None"
##            print "\n\n"
#            return d3_index

        def get_node_index(id, nodes):
            r=None
            for index,node in enumerate(nodes):
                if str(id) == str(node['value']):
                    r = index
                    break
#            if r:
#                return r
#            else:
#                return 0
            return r

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
                        #node = TopologyGenerator.node_get_adequate_group(node, assigned_groups)
                        TopologyGenerator.node_get_adequate_group(node, assigned_groups)
                        # Set proper ID ('agg<aggregate.pk>_<resource.id>') for each resource
#                        node['value'] = TopologyGenerator.resource_set_adequate_id(node['value'], assigned_groups)

                # TODO: Perform check over the links between the nodes! Consistency!!
                plugin_ui_data = dict(plugin_ui_data_aux.items() + plugin_ui_data.items())
            except Exception as e:
                print "[ERROR] Problem loading UI data inside PluginLoader. Details: %s" % str(e)

        # Update links ids to the index of the node in the array to match D3 requirements
#        for link in plugin_ui_data['d3_links']:
#            print link
#        for node in plugin_ui_data['d3_nodes']:
#            print node['name']

        # Convert Resource IDs into D3.js IDs
        try:
            for index, link in enumerate(plugin_ui_data['d3_links']):
                link['source'] = get_node_index(link['source'], plugin_ui_data['d3_nodes'])
                link['target'] = get_node_index(link['target'], plugin_ui_data['d3_nodes'])
                # When some ending point does not exist, remove the link so D3 does not draw it
#                print "\n\n **************** source: %s, target: %s" % (str(link['source']), str(link['target']))
#                print "\n\n\n\n\n********!!!!!!!!!! old plugin_ui_data['links']: %s\n\n" % str(plugin_ui_data['d3_links'])

                if not (link['source'] != None and link['target'] != None):
                    plugin_ui_data['d3_links'].pop(index)
#                    print "\n\n************** deleting link!!! new plugin_ui_data['links']: %s\n\n\n\n\n" % str(plugin_ui_data['d3_links'])
        except Exception as e:
            print "[WARNING] Problem retrieving D3 IDs inside PluginLoader. Details: %s" % str(e)
        return plugin_ui_data

