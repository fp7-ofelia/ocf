from vt_manager.models.VTServer import VTServer


class VTShell:

        def __init__(self):
                pass

	def GetNodes(self):
		
		servers = VTServer.objects.all()

