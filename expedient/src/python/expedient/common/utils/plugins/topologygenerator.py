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

    @staticmethod
    def load_ui_data(slice):
        """
        Calls the method 'get_ui_data' present in each plugin and mix the data for all
        plugins in a dictionary with nodes, links and total number of islands. This data
        will be sent to the topology visor, shown in the slice view.
        """
        def get_node_index(id, nodes):
            r=None
            for index,node in enumerate(nodes):
                if str(id) == str(node['value']):
                    r = index
                    break
            if r:
                return r
            else:
                return 0

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
                        #node = TopologyGenerator.node_get_adequate_group(node, assigned_groups)
                        TopologyGenerator.node_get_adequate_group(node, assigned_groups)

                    # TODO: Perform check over the links between the nodes! Consistency!!
                plugin_ui_data = dict(plugin_ui_data_aux.items() + plugin_ui_data.items())
            except Exception as e:
                print "[ERROR] Problem loading UI data inside PluginLoader. Details: %s" % str(e)

        # Update links ids to the index of the node in the array to match D3 requirements

        try:
            for link in plugin_ui_data['d3_links']:
                link['target'] = get_node_index(link['target'], plugin_ui_data['d3_nodes'])
                link['source'] = get_node_index(link['source'], plugin_ui_data['d3_nodes'])
        except Exception as e:
            print e
        return plugin_ui_data

