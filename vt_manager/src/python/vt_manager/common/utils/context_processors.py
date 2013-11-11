def contextSettingsInTemplate(request):
	from django.conf import settings
	from os.path import dirname, join

	#vf = open('../../../../../.currentVersion','r')
	vf = open(join(dirname(__file__), '../../../../../.currentVersion'),'r')
	softwareVersion = vf.read().strip()
	vf.close()

	extraSettings =  {'islandName':settings.ISLAND_NAME,
					'softwareVersion':softwareVersion,
					}		
	return extraSettings 
