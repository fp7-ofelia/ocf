import logging
'''
	@author: msune

	Ofelia XEN Agent settings file (Static settings) 
'''
##General Parameters

'''Base folder where vms and logs will be store.
All the rest of folder must be inside this folder'''
OXA_PATH="/opt/ofelia/oxa/"


'''Log folder. Must exist!'''
OXA_LOG="/opt/ofelia/oxa/log/"

#Log level. Should be: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
#Default warning
LOG_LEVEL="WARNING"

'''XMLRPC over HTTPS server parameters'''
#XMLRPC_SERVER_LISTEN_HOST='127.0.0.1' # You should not use '' here, unless you have a real FQDN.
XMLRPC_SERVER_LISTEN_HOST='0.0.0.0' # You should not use '' here, unless you have a real FQDN.
XMLRPC_SERVER_LISTEN_PORT=9229

XMLRPC_SERVER_KEYFILE='security/certs/agent.key'    # Replace with your PEM formatted key file
XMLRPC_SERVER_CERTFILE='security/certs/agent.crt'  # Replace with your PEM formatted certificate file

#HDs
OXA_DEFAULT_SWAP_SIZE_MB=512

##FileHD driver settings
'''Enable/disable file-type Hdmanager Cache FS'''
OXA_FILEHD_USE_CACHE=True

'''Cache folder to store VMs (if cache mechanism is used)'''
OXA_FILEHD_CACHE_VMS="/opt/ofelia/oxa/cache/vms/"

'''Remote folder to store VMs'''
OXA_FILEHD_REMOTE_VMS="/opt/ofelia/oxa/remote/vms/"

'''Cache folder for templates (if cache is enabled)'''
OXA_FILEHD_CACHE_TEMPLATES="/opt/ofelia/oxa/cache/templates/"

'''Remote folder for templates'''
OXA_FILEHD_REMOTE_TEMPLATES="/opt/ofelia/oxa/remote/templates/"

'''Use sparse disks while cloning'''
OXA_FILEHD_CREATE_SPARSE_DISK=False

'''Nice priority for Copy&untar operations'''
OXA_FILEHD_NICE_PRIORITY=15

'''IONice copy&untar operations class'''
OXA_FILEHD_IONICE_CLASS=2
'''IONice copy&untar operations priority'''
OXA_FILEHD_IONICE_PRIORITY=5
'''/bin/dd block size(bs) for copy operations'''
OXA_FILEHD_DD_BS_KB=32

##Ofelia Debian VM configurator parameters
'''Kernel and initrd that will be used by machines'''
OXA_XEN_SERVER_KERNEL="/boot/vmlinuz-2.6.32-5-xen-amd64"
OXA_XEN_SERVER_INITRD="/boot/initrd.img-2.6.32-5-xen-amd64"

'''Debian-family usual file locations'''
OXA_DEBIAN_INTERFACES_FILE_LOCATION = "/etc/network/interfaces"
OXA_DEBIAN_UDEV_FILE_LOCATION = "/etc/udev/rules.d/70-persistent-net.rules"
OXA_DEBIAN_HOSTNAME_FILE_LOCATION="/etc/hostname"
OXA_DEBIAN_SECURITY_ACCESS_FILE_LOCATION="/etc/security/access.conf"

'''RedHat-family usual file locations'''
OXA_REDHAT_INTERFACES_FILE_LOCATION = "/etc/sysconfig/network-scripts/"
OXA_REDHAT_UDEV_FILE_LOCATION = "/etc/udev/rules.d/70-persistent-net.rules"
OXA_REDHAT_HOSTNAME_FILE_LOCATION="/etc/hostname"


