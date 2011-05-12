#!/usr/bin/env python

#
# Generated Tue Feb  1 09:41:08 2011 by generateDS.py version 2.3b.
#

import sys

import ??? as supermod

etree_ = None
Verbose_import_ = False
(   XMLParser_import_none, XMLParser_import_lxml,
    XMLParser_import_elementtree
    ) = range(3)
XMLParser_import_library = None
try:
    # lxml
    from lxml import etree as etree_
    XMLParser_import_library = XMLParser_import_lxml
    if Verbose_import_:
        print("running with lxml.etree")
except ImportError:
    try:
        # cElementTree from Python 2.5+
        import xml.etree.cElementTree as etree_
        XMLParser_import_library = XMLParser_import_elementtree
        if Verbose_import_:
            print("running with cElementTree on Python 2.5+")
    except ImportError:
        try:
            # ElementTree from Python 2.5+
            import xml.etree.ElementTree as etree_
            XMLParser_import_library = XMLParser_import_elementtree
            if Verbose_import_:
                print("running with ElementTree on Python 2.5+")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree_
                XMLParser_import_library = XMLParser_import_elementtree
                if Verbose_import_:
                    print("running with cElementTree")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree_
                    XMLParser_import_library = XMLParser_import_elementtree
                    if Verbose_import_:
                        print("running with ElementTree")
                except ImportError:
                    raise ImportError("Failed to import ElementTree from any known place")

def parsexml_(*args, **kwargs):
    if (XMLParser_import_library == XMLParser_import_lxml and
        'parser' not in kwargs):
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        kwargs['parser'] = etree_.ETCompatXMLParser()
    doc = etree_.parse(*args, **kwargs)
    return doc

#
# Globals
#

ExternalEncoding = 'ascii'

#
# Data representation classes
#

class rspecSub(supermod.rspec):
    def __init__(self, provisioning=None):
        super(rspecSub, self).__init__(provisioning, )
supermod.rspec.subclass = rspecSub
# end class rspecSub


class provisioning_typeSub(supermod.provisioning_type):
    def __init__(self, action=None):
        super(provisioning_typeSub, self).__init__(action, )
supermod.provisioning_type.subclass = provisioning_typeSub
# end class provisioning_typeSub


class action_typeSub(supermod.action_type):
    def __init__(self, type_=None, id=None, virtual_machine=None):
        super(action_typeSub, self).__init__(type_, id, virtual_machine, )
supermod.action_type.subclass = action_typeSub
# end class action_typeSub


class virtual_machine_typeSub(supermod.virtual_machine_type):
    def __init__(self, name=None, uuid=None, project_id=None, slice_id=None, operating_system_type=None, operating_system_version=None, operating_system_distribution=None, virtualization_type=None, xen_configuration=None):
        super(virtual_machine_typeSub, self).__init__(name, uuid, project_id, slice_id, operating_system_type, operating_system_version, operating_system_distribution, virtualization_type, xen_configuration, )
supermod.virtual_machine_type.subclass = virtual_machine_typeSub
# end class virtual_machine_typeSub


class xen_configurationSub(supermod.xen_configuration):
    def __init__(self, hd_setup_type=None, hd_origin_path=None, virtualization_setup_type=None, memory_mb=None, interfaces=None):
        super(xen_configurationSub, self).__init__(hd_setup_type, hd_origin_path, virtualization_setup_type, memory_mb, interfaces, )
supermod.xen_configuration.subclass = xen_configurationSub
# end class xen_configurationSub


class interfaces_typeSub(supermod.interfaces_type):
    def __init__(self, interface=None):
        super(interfaces_typeSub, self).__init__(interface, )
supermod.interfaces_type.subclass = interfaces_typeSub
# end class interfaces_typeSub


class interface_typeSub(supermod.interface_type):
    def __init__(self, ismgmt=None, name=None, mac=None, ip=None, mask=None, gw=None, dns1=None, dns2=None):
        super(interface_typeSub, self).__init__(ismgmt, name, mac, ip, mask, gw, dns1, dns2, )
supermod.interface_type.subclass = interface_typeSub
# end class interface_typeSub



def get_root_tag(node):
    tag = supermod.Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = None
    if hasattr(supermod, tag):
        rootClass = getattr(supermod, tag)
    return tag, rootClass


def parse(inFilename):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'rspec'
        rootClass = supermod.rspec
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('<?xml version="1.0" ?>\n')
##     rootObj.export(sys.stdout, 0, name_=rootTag,
##         namespacedef_='http://www.fp7-ofelia.eu/CF/vt_am/rspec')
    doc = None
    return rootObj


def parseString(inString):
    from StringIO import StringIO
    doc = parsexml_(StringIO(inString))
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'rspec'
        rootClass = supermod.rspec
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('<?xml version="1.0" ?>\n')
##     rootObj.export(sys.stdout, 0, name_=rootTag,
##         namespacedef_='http://www.fp7-ofelia.eu/CF/vt_am/rspec')
    return rootObj


def parseLiteral(inFilename):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'rspec'
        rootClass = supermod.rspec
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('#from ??? import *\n\n')
##     sys.stdout.write('import ??? as model_\n\n')
##     sys.stdout.write('rootObj = model_.rspec(\n')
##     rootObj.exportLiteral(sys.stdout, 0, name_="rspec")
##     sys.stdout.write(')\n')
    return rootObj


USAGE_TEXT = """
Usage: python ???.py <infilename>
"""

def usage():
    print USAGE_TEXT
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    infilename = args[0]
    root = parse(infilename)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()


