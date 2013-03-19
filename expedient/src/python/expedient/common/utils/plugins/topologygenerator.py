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

    # Structure to save groups/islands and their assigned resources
    assigned_groups = []

    # TODO Separar en 2 clases: 1 para topo_index; otra para los enlaces (solo usar nombre, no depender de ID)
    # XXX: OBTENER LA ID DEL NODO A PARTIR DEL NOMBRE, QUE ES UNICO Y NO SE MODIFICA...
    @staticmethod
    def check_link_consistency(links, nodes, user, slice):
        """
        Checks consistency across links.
        In a link ( A - <link> - B), if any of the endpoints A or B
        do not exist, <link> is removed from the list.
        """
        consistent_links = []
        inconsistent_links = []
        inconsistent_links_message = ""
        nodes_length = len(nodes)
        try:
            for link in links:
#                print "\n\n\n\n\n\n>>>>>>>>>> initial data. #%s link: %s" % (str(index), str(link))
                source_node = dict({"id": link['source'], "res_id": None})
                target_node = dict({"id": link['target'], "res_id": None})

                # Convert Resource IDs into Topology index IDs
                try:
                   # Get back Resource ID from node's array (check first if node.index < #nodes)
#                   print "\n\nBEFORE source_node_id: %s, target_node_id: %s. node: %s\n\n" % (str(source_node['id']), str(target_node['id']), str(nodes[source_node['id']]))
                   if source_node['id'] < nodes_length:
                       source_node['res_id'] = nodes[source_node['id']]['value']
                   if target_node['id'] < nodes_length:
                       target_node['res_id'] = nodes[target_node['id']]['value']
#                   print "\n\nAFTER source_node_id: %s, target_node_id: %s\n\n" % (str(source_node['res_id']), str(target_node['res_id']))


#                   if str(link['source']) != "None" and str(link['target']) != "None":
#                       link['source'] = TopologyGenerator.get_topo_index_from_resource_id(link['source'], nodes)
#                       link['target'] = TopologyGenerator.get_topo_index_from_resource_id(link['target'], nodes)
##                       print ">>>>>>>>>>>>>>>> source: %s, target: %s" % (link['source'], link['target'])
##                   else:
##                       print "akshakjsahsjkahsjkahsjkasj ----> SOME ID IS 'NONE'"
                except Exception as e:
                    print "[WARNING] Problem retrieving Resource indices inside TopologyGenerator. Details: %s" % str(e)

#                print ">> before checking......... source: %s, target: %s" % (link['source'], link['target'])


                # Check consistency. If node A or B do not exist, remove link
#                if not(str(source_node['id']) != "None" and str(target_node['id']) != "None"):

                # Check consistency. If both nodes A and B exist, add link to structure
                if str(source_node['res_id']) != "None" and str(target_node['res_id']) != "None":
#                    print "----> OK link: %s <---"  % str(link)
                    consistent_links.append(link)
                # Otherwise, notify about this missing (and any other) to the Island Manager
                else:
                    # ORIGINAL
#                    print "-----> [BEFORE] REMOVING INDEX: %s FROM LINKS: %s" % (str(index), str(links))
#                    links.pop(index)
#                    print "-----> [AFTER] REMOVING INDEX: %s FROM LINKS: %s" % (str(index), str(links))

                    # Get data for e-mail
                    try:
                        # Choose the Resource ID which is not None
                        source_id = source_node['res_id'] or source_node['id']
                        source_node_object = Resource.objects.get(id = source_id)
                        source_node['id'] = source_id
                        source_node['name'] = source_node_object.name
                        source_node['agg_id'] = source_node_object.aggregate.pk
                        source_node['agg_name'] = source_node_object.aggregate.name
                    except:
                        source_node['name'] = ""
                        source_node['agg_id'] = ""
                        source_node['agg_name'] = ""
                    try:
                        # Choose the Resource ID which is not None
                        target_id = target_node['res_id'] or target_node['id']
                        target_node_object = Resource.objects.get(id = target_id)
                        target_node['id'] = target_id
                        target_node['name'] = target_node_object.name
                        target_node['agg_id'] = target_node_object.aggregate.pk
                        target_node['agg_name'] = target_node_object.aggregate.name
                    except:
                        target_node['name'] = ""
                        target_node['agg_id'] = ""
                        target_node['agg_name'] = ""

                    inconsistent_links.append({"source_id": source_node['id'], "source_name": source_node['name'], "source_aggregate_id": source_node['agg_id'], "source_aggregate_name": source_node['agg_name'], "target_id": target_node['id'], "target_name": target_node['name'], "target_aggregate_id": target_node['agg_id'], "target_aggregate_name": target_node['agg_name']})
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
#                print "\n\n*************************** inconsistent_links: %s *************************\n\n" % str(inconsistent_links)
                # XXX DESCOMENTAR AL SUBIR A [PRE]PRODUCCION
#                send_mail(settings.EMAIL_SUBJECT_PREFIX + " Inconsistent links at slice '%s': Expedient" % str(slice.name), "Hi, Island Manager\n\nThis is a warning to notify about some inconsistent links within a topology. This may be happening because a plugin or Aggregate Manager references a node not present in the Aggregate Managers chosen for this slice.\n\nProject: %s\nSlice: %s\nProblematic links:\n\n%s" % (slice.project.name, slice.name, str(inconsistent_links)), from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[user.email],)
            except Exception as e:
                print "[WARNING] Problem sending e-mail to user '%s' (email: %s) with information about link inconsistency inside TopologyGenerator. Details: %s" % (user.username, user.email, str(e))
        return consistent_links

#    # ======================== OLD
#
#    # TODO Separar en 2 clases: 1 para topo_index; otra para los enlaces (solo usar nombre, no depender de ID)
#    # XXX: OBTENER LA ID DEL NODO A PARTIR DEL NOMBRE, QUE ES UNICO Y NO SE MODIFICA...
#    @staticmethod
#    def check_link_consistency_old(links, nodes, user, slice):
#        """
#        Checks consistency across links.
#        In a link ( A - <link> - B), if any of the endpoints A or B
#        do not exist, <link> is removed from the list.
#        """
#        consistent_links = []
#        inconsistent_links = []
#        inconsistent_links_message = ""
#        try:
#            for link in links:
##                print "\n\n\n\n\n\n>>>>>>>>>> initial data. #%s link: %s" % (str(index), str(link))
#                source_node = dict({"id": link['source']})
#                target_node = dict({"id": link['target']})
#
#                # Convert Resource IDs into Topology index IDs
#                try:
#                   if str(link['source']) != "None" and str(link['target']) != "None":
#                       link['source'] = TopologyGenerator.get_topo_index_from_resource_id(link['source'], nodes)
#                       link['target'] = TopologyGenerator.get_topo_index_from_resource_id(link['target'], nodes)
##                       print ">>>>>>>>>>>>>>>> source: %s, target: %s" % (link['source'], link['target'])
##                   else:
##                       print "akshakjsahsjkahsjkahsjkasj ----> SOME ID IS 'NONE'"
#                except Exception as e:
#                    print "[WARNING] Problem retrieving Topology indices inside TopologyGenerator. Details: %s" % str(e)
#
##                print ">> before checking......... source: %s, target: %s" % (link['source'], link['target'])
#                # Check consistency. If node A or B do not exist, remove link
#                if not(str(link['source']) != "None" and str(link['target']) != "None"):
#                    # ORIGINAL
##                    print "-----> [BEFORE] REMOVING INDEX: %s FROM LINKS: %s" % (str(index), str(links))
##                    links.pop(index)
##                    print "-----> [AFTER] REMOVING INDEX: %s FROM LINKS: %s" % (str(index), str(links))
#
#                    # Get data for e-mail
#                    try:
#                        source_node_object = Resource.objects.get(id = source_node['id'])
#                        source_node['name'] = source_node_object.name
#                        source_node['agg_id'] = source_node_object.aggregate.pk
#                        source_node['agg_name'] = source_node_object.aggregate.name
#                    except:
#                        source_node['name'] = ""
#                        source_node['agg_id'] = ""
#                        source_node['agg_name'] = ""
#                    try:
#                        target_node_object = Resource.objects.get(id = target_node['id'])
#                        target_node['name'] = target_node_object.name
#                        target_node['agg_id'] = target_node_object.aggregate.pk
#                        target_node['agg_name'] = target_node_object.aggregate.name
#                    except:
#                        target_node['name'] = ""
#                        target_node['agg_id'] = ""
#                        target_node['agg_name'] = ""
#
#                    inconsistent_links.append({"source_id": source_node['id'], "source_name": source_node['name'], "source_aggregate_id": source_node['agg_id'], "source_aggregate_name": source_node['agg_name'], "target_id": target_node['id'], "target_name": target_node['name'], "target_aggregate_id": target_node['agg_id'], "target_aggregate_name": target_node['agg_name']})
#                else:
#                    consistent_links.append(link)
#        except Exception as e:
#            print "[WARNING] Problem checking link consistency inside TopologyGenerator. Details: %s" % str(e)
#
#        # Craft message to send via e-mail
#        if inconsistent_links:
#            for link in inconsistent_links:
#                inconsistent_links_message += "SOURCE\n"
#                inconsistent_links_message += "id: %s\nname: %s\naggregate id: %s\naggregate name: %s\n" % (link['source_id'], link['source_name'], link['source_aggregate_id'], link['source_aggregate_name'])
#                inconsistent_links_message += "TARGET\n"
#                inconsistent_links_message += "id: %s\nname: %s\naggregate id: %s\naggregate name: %s\n\n" % (link['target_id'], link['target_name'], link['target_aggregate_id'], link['target_aggregate_name'])
#
#            try:
#                from django.conf import settings
#                # XXX DESCOMENTAR AL SUBIR A [PRE]PRODUCCION
##                send_mail(settings.EMAIL_SUBJECT_PREFIX + " Inconsistent links at slice '%s': Expedient" % str(slice.name), "Hi, Island Manager\n\nThis is a warning to notify about some inconsistent links within a topology. This may be happening because a plugin or Aggregate Manager references a node not present in the Aggregate Managers chosen for this slice.\n\nProject: %s\nSlice: %s\nProblematic links:\n\n%s" % (slice.project.name, slice.name, str(inconsistent_links)), from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[user.email],)
#            except Exception as e:
#                print "[WARNING] Problem sending e-mail to user '%s' (email: %s) with information about link inconsistency inside TopologyGenerator. Details: %s" % (user.username, user.email, str(e))
#        return consistent_links

    @staticmethod
    def compute_number_islands(nodes):
        n_islands = 1
        try:
#            print "********************** assigned_groups: %s ****" % str(TopologyGenerator.assigned_groups)
#            n_islands = len(TopologyGenerator.assigned_groups) or 1
            # Or either create a list of unique elements and get its length
            n_islands = len(list(set([ n.get("group", 1) for n in nodes ])))
        except Exception as e:
            # Island numbering starts at 0; therefore add 1 to the obtained max value
            n_islands = max([ n.get("group", 1) for n in nodes ])+1 or 1
            print "[WARNING] Number of islands may have not been obtained at TopologyGenerator. Details: %s" % str(e)
        return n_islands

    @staticmethod
    def get_topo_index_from_resource_id(resource_id, nodes):
        """
        Retrieves topology index from the Resource ID.
        """
#        d3_index = None
        d3_index = resource_id
#        print "resource id: %s" % str(resource_id)
        for index,node in enumerate(nodes):
#            print "current node: %s" % str(node['value'])
            if str(resource_id) == str(node['value']):
                # If d3_index = None, return 'None' instead
                d3_index = index
                break
#        print "new node ID: %s\n\n" % str(d3_index)
        return d3_index

    @staticmethod
    def get_island_for_nodes(nodes):
        """
        Computes each node island/group through its aggregate manager ID and location.
        """
        from expedient.clearinghouse.aggregate.models import Aggregate
        try:
            for node in nodes:
                am = Aggregate.objects.get(id = node["aggregate"])
                # Group already exists
#                print "am.location: %s, assigned_groups: %s" % (str(am.location), str(TopologyGenerator.assigned_groups))
                try:
                    current_locations = [ group[str(i)] for i,group in enumerate(TopologyGenerator.assigned_groups) ]
                    if am.location in current_locations:
#                        print ">> setting node to group"
                        node["group"] = int(TopologyGenerator.assigned_groups[current_locations.index(am.location)].keys()[0])
                    else:
                        # New group is added
                        node["group"] = int(TopologyGenerator.assigned_groups[-1].keys()[0])+1
#                        print ">> adding new group: %s" % str(node["group"])
                except Exception as e:
#                    print ">> exception in node island: %s" % str(e)
                    if not node.get("group"):
                        node["group"] = 0
#                    print ">> node['group'] = %s" % str(node["group"])
                new_entry = {str(node["group"]): am.location}
#                print ">> new_entry = %s" % str(new_entry)
                # List of sublists: [aggregate, group]
                if new_entry not in TopologyGenerator.assigned_groups:
#                    print "increasing TopologyGenerator.assigned_groups..."
                    TopologyGenerator.assigned_groups.append(new_entry)
        except Exception as e:
            print "[WARNING] Could not obtain adequate groups for islands in TopologyGenerator. Details: %s" % str(e)

#        for node in nodes:
#            print "+++++ node['group']: %s" % str(node['group'])

        return nodes

# ================ OLD =================
#    @staticmethod
#    def node_get_adequate_group(node):
#        """
#        Computes each node group through its aggregate manager ID.
#        """
#
#        try:
#            if TopologyGenerator.assigned_groups:
#                for group in TopologyGenerator.assigned_groups:
#                    # If some other type was assigned the same group, increment group for current type
#                    if node["aggregate"] == group["aggregate"]:
#                        node["group"] = group["group"]
#                    else:
#                        node["group"] = TpologyGenerator.assigned_groups[-1]["group"]+1
#            else:
#                node["group"] = 0
#            new_entry = {"group": node["group"], "aggregate": node["aggregate"]}
#            # List of sublists: [aggregate, group]
#            if new_entry not in TopologyGenerator.assigned_groups:
#                TopologyGenerator.assigned_groups.append(new_entry)
#        except:
#            pass

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

        # =================== LEO's COMMIT ======================
#        def get_node_index(id, nodes):
#            r=None
#            for index,node in enumerate(nodes):
#                if str(id) == str(node['value']):
#                    r = index
#                    break
##            if r:
##                return r
##            else:
##                return 0
#            return r

        # Iterate over each plugin to get its nodes and links
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
#                    plugin_ui_data['n_islands'] = plugin_ui_data['n_islands'] + plugin_ui_data_aux.get("n_islands",0)

                    # Calculate each node's group depending on its aggregate manager ID. User should
                    # not have any knowledge of island and therefore should not set the group by itself
#                    assigned_groups = []
#                    for node in plugin_ui_data['d3_nodes']:
#                        TopologyGenerator.node_get_island(node)

                plugin_ui_data = dict(plugin_ui_data_aux.items() + plugin_ui_data.items())
#                print "\n\n\n\n plugin_ui_data['d3_links']: %s\n\n\n\n" % str(plugin_ui_data['d3_links'])

#                # TODO
#                plugin_ui_data['n_islands'] = TopologyGenerator.compute_number_islands(plugin_ui_data)
#                print "\n\n\n\n plugin_ui_data['n_islands']: %s\n\n\n\n" % str(plugin_ui_data['n_islands'])



#                print "\n\n\n\n plugin_ui_data['d3_nodes']: %s\n\n\n\n" % str(plugin_ui_data['d3_nodes'])
#                print "\n\n\n\n plugin_ui_data['d3_links']: %s\n\n\n\n" % str(plugin_ui_data['d3_links'])
            except Exception as e:
                print "[ERROR] Problem loading UI data inside TopologyGenerator. Details: %s" % str(e)

        # Update links ids to the index of the node in the array to match D3 requirements
#        for link in plugin_ui_data['d3_links']:
#            print link
#        for node in plugin_ui_data['d3_nodes']:
#            print node['name']





#        # ========== LEO's COMMIT ==========
#        # Convert Resource IDs into D3.js IDs
#        try:
#            for index, link in enumerate(plugin_ui_data['d3_links']):
#                link['source'] = get_node_index(link['source'], plugin_ui_data['d3_nodes'])
#                link['target'] = get_node_index(link['target'], plugin_ui_data['d3_nodes'])
#                # When some ending point does not exist, remove the link so D3 does not draw it
#                #print "\n\n **************** source: %s, target: %s" % (str(link['source']), str(link['target']))
#                #print "\n\n\n\n\n********!!!!!!!!!! old plugin_ui_data['links']: %s\n\n" % str(plugin_ui_data['d3_links'])
#
#                if not (link['source'] != None and link['target'] != None):
#                    plugin_ui_data['d3_links'].pop(index)
#                    #print "\n\n************** deleting link!!! new plugin_ui_data['links']: %s\n\n\n\n\n" % str(plugin_ui_data['d3_links'])
#        except Exception as e:
#            print "[WARNING] Problem retrieving D3 IDs inside PluginLoader. Details: %s" % str(e)
#        # ========== LEO's COMMIT ==========




        # ========== GET_NODE_INDEX INSIDE OTHER METHOD TO TAKE CARE OF LINKS ===========
        for link in plugin_ui_data['d3_links']:
##            print "\n\n\n\n\n\n>>>>>>>>>> initial data. #%s link: %s" % (str(index), str(link))
#            source_node = dict({"id": link['source']})
#            target_node = dict({"id": link['target']})

            # Convert Resource IDs into Topology index IDs
            try:
               if str(link['source']) != "None" and str(link['target']) != "None":

#                   print "BEFORE link source: %s, link target: %s" % (link['source'], link['target'])
                   link['source'] = TopologyGenerator.get_topo_index_from_resource_id(link['source'], plugin_ui_data['d3_nodes'])
                   link['target'] = TopologyGenerator.get_topo_index_from_resource_id(link['target'], plugin_ui_data['d3_nodes'])
#                   print "AFTER link source: %s, link target: %s" % (link['source'], link['target'])

#                   print ">>>>>>>>>>>>>>>> source: %s, target: %s" % (link['source'], link['target'])
#               else:
#                   print "akshakjsahsjkahsjkahsjkasj ----> SOME ID IS 'NONE'"
            except Exception as e:
                print "[WARNING] Problem retrieving Topology indices inside TopologyGenerator. Details: %s" % str(e)

        # Check link consistency
        from django.contrib.auth.models import User
        user = User.objects.get(username='expedient')
        # XXX DESCOMENTAR AL SUBIR A [PRE]PRODUCCION
#        user = User.objects.filter(is_superuser=True)[0]
        plugin_ui_data['d3_links'] = TopologyGenerator.check_link_consistency(plugin_ui_data['d3_links'], plugin_ui_data['d3_nodes'], user, slice)
#        print "\n\n\n\n plugin_ui_data['d3_links'] (II): %s\n\n\n\n" % str(plugin_ui_data['d3_links'])
        # ========== GET_NODE_INDEX INSIDE OTHER METHOD TO TAKE CARE OF LINKS ===========

        # Calculate each node's group depending on its aggregate manager ID. User should
        # not have any knowledge of island and therefore should not set the group by itself 
#        print "***************************************************************"
        plugin_ui_data['d3_nodes'] = TopologyGenerator.get_island_for_nodes(plugin_ui_data['d3_nodes'])
#        plugin_ui_data['n_islands'] = TopologyGenerator.compute_number_islands()

#        print "****************** GETING No. ISLANDS!!!!!!!!!!!!!!!!!!! ************************"
        plugin_ui_data['n_islands'] = TopologyGenerator.compute_number_islands(plugin_ui_data['d3_nodes'])
#        print "************** [AFTER] n_islands: %s **********************************" % str(plugin_ui_data['n_islands'])

#        print "************** [AFTER] TopologyGenerator.assigned_groups: %s **********************************" % str(TopologyGenerator.assigned_groups)

        return plugin_ui_data

