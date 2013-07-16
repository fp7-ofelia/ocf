'''@author: SergioVidiella'''


'''Virtualization Technology settings'''
VIRT_TECH_TYPE_XEN = "xen"

VIRT_TECH_CHOICES = (
    (VIRT_TECH_TYPE_XEN, 'XEN'),
)


'''OS Distribution settings'''
OS_DIST_TYPE_DEBIAN = "Debian"
OS_DIST_TYPE_UBUNTU = "Ubuntu"
OS_DIST_TYPE_REDHAT = "RedHat"

OS_DIST_CHOICES = (
    (OS_DIST_TYPE_DEBIAN, 'Debian'),
    (OS_DIST_TYPE_UBUNTU, 'Ubuntu'),
    (OS_DIST_TYPE_REDHAT, 'RedHat'),
)


'''OS Version settings'''
OS_VERSION_TYPE_50 = "5.0"
OS_VERSION_TYPE_60 = "6.0"

OS_VERSION_CHOICES = (
    (OS_VERSION_TYPE_50, '5.0'),
    (OS_VERSION_TYPE_60, '6.0'),
)


'''OS Type settings'''
OS_TYPE_TYPE_GNULINUX = "GNU/Linux"
OS_TYPE_TYPE_WINDOWS = "Windows"

OS_TYPE_CHOICES = (
    (OS_TYPE_TYPE_GNULINUX, 'GNU/Linux'),
    (OS_TYPE_TYPE_WINDOWS, 'Windows'),
)


'''HD Setup Type settings'''
HD_SETUP_TYPE_FILE_IMAGE = "file-image"
HD_SETUP_TYPE_LV = "logical-volume-image"

HD_SETUP_TYPE_CHOICES = (
    (HD_SETUP_TYPE_FILE_IMAGE, 'File image'),
    (HD_SETUP_TYPE_LV, 'Logical Volume Image'),
)


'''Virtualization Type settings'''
VIRTUALIZATION_SETUP_TYPE_PARAVIRTUALIZATION= "paravirtualization"
VIRTUALIZATION_SETUP_TYPE_HAV = "hardware-assisted-virtualization"

VIRTUALIZATION_SETUP_TYPE_CHOICES = (
    (VIRTUALIZATION_SETUP_TYPE_PARAVIRTUALIZATION, 'Paravirtualization'),
    (VIRTUALIZATION_SETUP_TYPE_HAV, 'Hardware-assisted virtualization'),
)

