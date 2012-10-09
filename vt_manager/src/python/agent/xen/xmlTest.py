#!/usr/bin/python -u
import libvirt
import sys
import os
import time

if not os.access("/proc/xen", os.R_OK):
    print 'System is not running a Xen kernel'
    sys.exit(1)

#
# Try to provide default OS images paths here, of course non standard
#
osroots = [
  "/u/fc4-2.img",
  "/u/fc4.img",
  "/xen/fc4.img",
  "/home/user/XenServer/fedora.iso"
]

okay = 1

osroot = None
for root in osroots:
    if os.access(root, os.R_OK):
        osroot = root
        break

if osroot == None:
    print "Could not find a guest OS root, edit to add the path in osroots"
    sys.exit(1)

kernel=open("/proc/version").read().split()
kernelOv = kernel[2]

if kernelOv.find('hypervisor'):
    kernelU = "/boot/vmlinuz-" + kernelOv.replace('hypervisor', 'guest')
    initrdU = "/boot/initrd-" + kernelOv.replace('hypervisor', 'guest') + ".img"
elif kernelOv.find('xen0'):
    kernelU = "/boot/vmlinuz-" + kernelOv.replace('xen0', 'xenU')
    initrdU = "/boot/initrd-" + kernelOv.replace('xen0', 'xenU') + ".img"

if not os.access(kernelU, os.R_OK):
    print "Did not find the guest kernel %s" % (kernelU)
    sys.exit(1)

kernelU = "<kernel>" + kernelU + "</kernel>"

if not os.access(initrdU, os.R_OK):
    print "Did not find the guest initrd %s" % (initrdU)
    initrdU = ""
else:
    initrdU = "<initrd>" + initrdU + "</initrd>"


conn = libvirt.open(None)
if conn == None:
    print 'Failed to open connection to the hypervisor'
    sys.exit(1)

xmldesc="""<domain type='xen'>
  <name>a</name>
  <os>
    <type>linux</type>
""" + kernelU + initrdU + """
    <cmdline> root=/dev/sda1 ro selinux=0 3</cmdline>
  </os>
  <memory>131072</memory>
  <vcpu>1</vcpu>
  <devices>
    <disk type='file'>
      <source file='%s'/>
      <target dev='sda1'/>
    </disk>
    <interface type='bridge'>
      <source bridge='virbr0'/>
      <mac address='aa:00:00:00:00:12'/>
      <script path='/etc/xen/scripts/vif-bridge'/>
    </interface>
  </devices>
</domain>
""" % (osroot)

