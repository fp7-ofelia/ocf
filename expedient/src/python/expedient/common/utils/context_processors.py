def contextSettingsInTemplate(request):
	from django.conf import settings
	from os.path import dirname, join
	from django.core.urlresolvers import reverse
	from django.contrib.auth.models import AnonymousUser

	vf = open(join(dirname(__file__), '../../../../../.currentVersion'),'r')
	softwareVersion = vf.read()

	if not isinstance(request.user,AnonymousUser) and request.user.password == '!':
		ldapUser = True
	else:
		ldapUser = False

	extraSettings =  {'islandName':settings.ISLAND_NAME,
					'softwareVersion':softwareVersion,
					'allowLocalRegistration':settings.ALLOW_LOCAL_REGISTRATION,
					'ldapUser':ldapUser,
					'ofregURL':settings.OFREG_URL
					}		
	return extraSettings 
