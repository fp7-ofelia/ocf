def contextSettingsInTemplate(request):
	from django.conf import settings
	from os.path import dirname, join
	from django.core.urlresolvers import reverse

	vf = open(join(dirname(__file__), '../../../../../.currentVersion'),'r')
	softwareVersion = vf.read()

	extraSettings =  {'islandName':settings.ISLAND_NAME,
					'softwareVersion':softwareVersion,
					'allowLocalRegistration':settings.ALLOW_LOCAL_REGISTRATION,
					}		
	return extraSettings 
