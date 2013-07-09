import abc

class abstractstatic(staticmethod):
    __slots__ = ()
    def __init__(self, function):
        super(abstractstatic, self).__init__(function)
        function.__isabstractmethod__ = True
    __isabstractmethod__ = True

class PluginInterface(object):
    __metaclass__ = abc.ABCMeta

    @abstractstatic
    def get_ui_data(slice):
        """
        Hook method. Use this very same name so Expedient can get the resources for every plugin.
        """
        ui_context = dict()
        try:
            ui_context['nodes'] = get_nodes(slice)
            ui_context['links'] = get_links(slice)
        except Exception as e:
            print "[ERROR] Problem loading UI data for plugin 'vt_plugin'. Details: %s" % str(e)
        return ui_context

    @abstractstatic
    def get_links(slice):
        return []
#        return [{"source": 1, "target": 2, "value": "rsc_1-2"}]

    @abstractstatic
    def get_nodes(slice):
        return []
#        return [{"value": 280, "description": "lorelei"}]

