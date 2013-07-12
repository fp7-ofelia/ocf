#!/usr/bin/python

#----------------------------------------------------------------------
# Copyright (c) 2011 Raytheon BBN Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
#----------------------------------------------------------------------
"""
RSpec validation and printing utilities.
"""
import xml.etree.ElementTree as etree 
import subprocess
import tempfile
import xml.parsers.expat
import xml.dom.minidom as md
from rspec_schema import *

RSPECLINT = "rspeclint" 

def is_wellformed_xml( string, logger=None ):
    # Try to parse the XML code.
    # If it fails to parse, then it is not well-formed
    # 
    # Definition of well-formed is here:
    # http://www.w3.org/TR/2008/REC-xml-20081126/#sec-well-formed
    parser = xml.parsers.expat.ParserCreate()
    retVal = True
    try: 
        parser.Parse( string, 1 )
    except Exception, e:
        # Parsing failed, so not well formed XML
        if logger is not None:
            logger.debug("Not wellformed XML: %s", e)
        else:
            print "Not wellformed XML: ", e
        retVal= False
    return retVal

# def compare_request_manifest( request, manifest ):
#     """Compare the nodes in the request and manifest to make sure they match."""
#     req = lxml.objectify.fromstring(request)    
#     print help(req)
#     man = lxml.objectify.fromstring(manifest)
    
def has_child( xml ):
    try:
        root = etree.fromstring(xml)
    except:
        return False
    # see if there are any children
    if len(list(root)) > 0:
        return True
    else:
        return False

def get_expected_schema_info( version="GENI 3" ):
    """Returns (namespace, advertisement RSpec schema url, request RSpec schema url) for this RSpec version"""

    if version == "ProtoGENI 2":
        return (PG_2_NAMESPACE, 
                PG_2_AD_SCHEMA, 
                PG_2_REQ_SCHEMA, 
                PG_2_MAN_SCHEMA)
    elif version == "GENI 3":
        return (GENI_3_NAMESPACE, 
                GENI_3_AD_SCHEMA, 
                GENI_3_REQ_SCHEMA, 
                GENI_3_MAN_SCHEMA)


def is_rspec_of_type( xml, type=REQUEST, version="GENI 3", typeOnly=False ):
    try:
        root = etree.fromstring(xml)
    except:
        print "Failed to make an XML doc"
        return False

    actual_type = root.get('type')
    if actual_type is None or actual_type.lower() != type.lower():
        return False
    elif typeOnly:
        # only checking the type in the RSpec
        # If I get this far, then RSpec is ok and return True
        return True
    else:
        # Also check the schema
        # location can contain many items
        location = root.get( "{"+XSI+"}"+"schemaLocation" )
        ns, ad_schema, req_schema, man_schema = get_expected_schema_info( version=version )
        if type == REQUEST:
            schema = req_schema
        elif type == ADVERTISEMENT:
            schema = ad_schema
        elif type == MANIFEST:
            schema = man_schema

        # case insensitive comparison
        if schema.lower() in location.lower():
            return True
        else:
            return False

def get_comp_ids_from_rspec( xml, version="GENI 3" ):
    try:
        root = etree.fromstring(xml)
    except:
        return False

    tmp = get_expected_schema_info( version=version )
    ns, ad_schema, req_schema, man_schema  = tmp
    prefix = "{%s}"%ns
    nodes = root.findall( prefix+'node' ) #get all nodes
    # generate a list of node component_ids
    comp_id_list = []
    for node in nodes:
        node_comp_id = node.get('component_id')
        if node_comp_id is not None:
            comp_id_list = comp_id_list + [node_comp_id]
    return set(comp_id_list)


def get_client_ids_from_rspec( xml, version="GENI 3" ):
    try:
        root = etree.fromstring(xml)
    except:
        return False

    tmp = get_expected_schema_info( version=version )
    ns, ad_schema, req_schema, man_schema  = tmp
    prefix = "{%s}"%ns
    nodes = root.findall( prefix+'node' ) #get all nodes
    # generate a list of node client_ids
    client_id_list = []
    for node in nodes:
        node_client_id = node.get('client_id')
        if node_client_id is not None:
            client_id_list = client_id_list + [node_client_id]
    return set(client_id_list)

def has_child_node( xml, version="GENI 3" ):
    try:
        root = etree.fromstring(xml)
    except:
        return False

    ns, ad_schema, req_schema, man_schema  = get_expected_schema_info( version=version )
    prefix = "{%s}"%ns
    nodes = root.findall( prefix+'node' ) #get all nodes
    if len(nodes) > 0:
        return True
    else:
        return False

def compare_comp_ids( xml1, xml2, version="GENI 3"):
    """Determines that the list of component IDs in two RSpecs are the same. (Useful for compare request and manifest RSpecs.) """

    comp_id1 = get_comp_ids_from_rspec( xml1, version=version )
    comp_id2 = get_comp_ids_from_rspec( xml2, version=version )
    if comp_id1 == comp_id2:
        return True
    else:
        return False

def compare_client_ids( xml1, xml2, version="GENI 3"):
    """Determines that the list of client IDs in two RSpecs are the same. (Useful for compare request and manifest RSpecs.) """

    client_id1 = get_client_ids_from_rspec( xml1, version=version )
    client_id2 = get_client_ids_from_rspec( xml2, version=version )
    if client_id1 == client_id2:
        return True
    else:
        return False

def has_child_ids( xml, check_comp_id_list, version="GENI 3" ):
    compare_comp_id_set = get_comp_ids_from_rspec( xml, version=version )

    # check_comp_id_list must be a subset of compare_comp_id_list to return True
    if set(check_comp_id_list) == compare_comp_id_set:
        return True
    else:
        return False


# def has_nodes( xml, node_name="node" ):
#     print xml
#     try:
#         root = etree.fromstring(xml)
#     except:
#         return False
#     firstnode = root.find("node")
#     print firstnode
#     if firstnode is None:
#         return False
#     else:
#         return True
# def xml_equal( xml1, xml2 ):
#     """Compare two xml documents and determine if they are the same (return: True)."""
#     # Is this guaranteed to always work?
#     obj1 = lxml.objectify.fromstring(xml1.strip())
#     newxml1 = etree.tostring(obj1)
#     obj2 = lxml.objectify.fromstring(xml2.strip())
#     newxml2 = etree.tostring(obj2)
#     return newxml1 == newxml2

def rspeclint_exists():
    """Try to run 'rspeclint' to see if we can find it."""
    # TODO: Hum....better way (or place) to do this? (wrapper? rspec_util?)
    try:
        cmd = [RSPECLINT]
        output = subprocess.call( cmd, stderr=open('/dev/null', 'w') )
    except:
        # TODO: WHAT EXCEPTION TO RAISE HERE?
        raise Exception, "Failed to locate or run '%s'" % RSPECLINT


# add some utility functions for testing various namespaces and schemas
def validate_rspec( ad, namespace=GENI_3_NAMESPACE, schema=GENI_3_REQ_SCHEMA ):
    """Run 'rspeclint' on a file.
    ad - a string containing an RSpec
    """
    # rspeclint must be run on a file
    with tempfile.NamedTemporaryFile() as f:
        f.write( ad )
        # Run rspeclint "../rspec/3" "../rspec/3/ad.xsd" <rspecfile>
        cmd = [RSPECLINT, namespace, schema, f.name]
        f.seek(0)
        output = subprocess.call( cmd, stderr=open('/dev/null', 'w') )
        # log something?
        # "Return from 'ListResources' at aggregate '%s' " \
        #     "expected to pass rspeclint " \
        #     "but did not. "
        # % (agg_name, ad[:100]))

        # if rspeclint returns 0 then it was successful
        if output == 0:
            return True
        else:
            # FIXME: Log rspeclint output?
            return False

def rspec_available_only( rspec, namespace=GENI_3_NAMESPACE, schema=GENI_3_REQ_SCHEMA, version="GENI 3" ):
    """ Return True if all nodes in rspec say:
     <available now="true">
    Otherwise, return False.
    rspec - a string containing an RSpec
    """
    try:
        root = etree.fromstring(rspec)
    except:
        return False
    ns, ad_schema, req_schema, man_schema  = get_expected_schema_info( version=version )
    prefix = "{%s}"%ns
    nodes = root.findall( prefix+'node' ) #get all nodes
    available=True
    for node in nodes:
        avail = node.find( prefix+"available" )
        if avail.get("now").lower() == "false":
            available = False
            return available
    return available
    
#def is_valid_rspec(): 
# Call is_rspec_string()
# Call validate_rspec()
def is_rspec_string( rspec, rspec_namespace=None, rspec_schema=None, 
                     logger=None ):
    '''Could this string be part of an XML-based rspec?
    Returns: True/False'''

    if rspec is None or not(isinstance(rspec, str)):
        return False

    # do all comparisons as lowercase
    rspec = rspec.lower()

    # (1) Check if rspec is a well-formed XML document
    if not is_wellformed_xml( rspec, logger ):
        return False
    
    # (2) Check if rspec is a valid XML document
    #   (a) a snippet of XML starting with <rspec>, or
    #   (b) a snippet of XML starting with <resv_rspec>
    if (('<rspec' in rspec) or
        ('<resv_rspec' in rspec)): 
        return True

    # (3) Validate rspec against schema
    if rspec_namespace and rspec_schema:
        if validate_rspec(rspec, 
                          namespace=rspec_namespace, 
                          schema=rspec_schema ):
            return True
        else:
            return False
    return False


def getPrettyRSpec(rspec):
    '''Produce a pretty print string for an XML RSpec'''
    prettyrspec = rspec
    try:
        newl = ''
        if '\n' not in rspec:
            newl = '\n'
        prettyrspec = md.parseString(rspec).toprettyxml(indent=' '*2, newl=newl)
    except:
        pass
    # set rspec to be UTF-8
    if isinstance(prettyrspec, unicode):
        prettyrspec = prettyrspec.encode('utf-8')
    return prettyrspec

if __name__ == "__main__":
    request_str = """<?xml version='1.0'?>
<!--Comment-->
<rspec type="request" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/request.xsd"></rspec>"""
    manifest_str = """<?xml version='1.0'?>
<!--Comment-->
<rspec type="manifest" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/manifest.xsd"></rspec>"""

    xml_str = """<?xml version='1.0'?>
<!--Comment-->
<rspec><node component_id='a'><sliver_type/><available </node><node component_id='b'><sliver_type/></node><node component_id='d'><!--no sliver_type--></node></rspec>"""

    xml_str2 = """<?xml version='1.0'?>
<!--Comment-->
<rspec><node component_id='a'><sliver_type/></node><node component_id='b'><sliver_type/></node></rspec>"""
    xml_str3 = """<?xml version='1.0'?>
<!--Comment-->
<rspec><node component_id='a'><sliver_type/></node><node component_id='d'><sliver_type/></node></rspec>"""

    xml_str4 = """<?xml version='1.0'?>
<!--Comment-->
<rspec><node component_id='b'><sliver_type/></node></rspec>"""
    xml_str5 = """<rspec><node component_id='b'><sliver_type/></node></rspec>"""



    rspec_comment_str = """
<!--Comment-->
<rspec></rspec>"""

    rspec_str = """
<rspec></rspec>"""

    resvrspec_comment_str = """
<!--Comment-->
<resv_rspec></resv_rspec>"""
    resvrspec_str = """
<resv_rspec></resv_rspec>"""

    none_str = None
    number = 12345
    xml_notrspec_str = """<?xml version='1.0'?>
<!--Comment-->
<foo></foo>"""
    malformed_str = """<?xml version='1.0'?>
<!--Comment-->
<rspec></rspecasdf>"""
    earlycomment_str = """<!--Comment-->
<?xml version='1.0'?>
<rspec></rspec>"""
    def test( test_str ):
        print test_str
        if is_rspec_string( test_str ):
            print "is_rspec_str() is TRUE"
        else:
            print "is_rspec_str() is FALSE"                

#        print is_wellformed_xml( test_str )

    print "===== For the following strings is_rspec_str() should be TRUE ====="
    test( xml_str )
    test( rspec_comment_str)
    test( rspec_str)
    test( resvrspec_comment_str )
    test( resvrspec_str )


    print "===== For the following strings is_rspec_str() should be FALSE ====="
    test( none_str )
    test( number )
    test( xml_notrspec_str )
    test( malformed_str )
    test( earlycomment_str )

    # print "===== XML Equality test ======"
    # print xml_equal(xml_str, xml_notrspec_str)
    # print xml_equal(xml_str, xml_str)

    # print "===== XML Comparison test ======"
    # print compare_request_manifest(xml_str, xml_notrspec_str)
    # print compare_request_manifest(xml_str, xml_str)

    # print "===== RSpec has nodes? ======"
    # print has_nodes(xml_str)
    # print has_nodes(rspec_str)
    # print has_nodes(xml_notrspec_str)
    # print has_nodes(malformed_str)

    print "===== RSpec has child? ======"
    print has_child(xml_str)
    print has_child(rspec_str)
    print has_child(xml_notrspec_str)
    print has_child(malformed_str)


    print "===== RSpec has child with ID? ======"
    print has_child_ids(xml_str, 'a')
    print has_child_ids(xml_str, 'b')
    print has_child_ids(xml_str, 'c')
    print has_child_ids(xml_str, 'd')
    print has_child_ids(xml_str, ('a','b'))
    print has_child_ids(xml_str, ['a','b'])
    print has_child_ids(xml_str, ['a','b','d'])
    print has_child_ids(xml_str, ['a','c'])
    print has_child_ids(xml_str, ['a','d'])

    print "===== Comp IDs in two Rspecs match ======"
    print "Compare 2 identical RSpecs [Expected result: True]"
    print compare_comp_ids( xml_str, xml_str )
    print "Compare RSpec with extra unused node to one without  [Expected result: True]"
    print compare_comp_ids( xml_str, xml_str2 )
    print "Compare RSpecs with one node in common and another node different  [Expected result: False]"
    print compare_comp_ids( xml_str, xml_str3 )
    print "Compare RSpecs with one a subset of the other  [Expected result: False]"
    print compare_comp_ids( xml_str, xml_str4 )

    print "Compare RSpecs that are the same except for the <?xml..> at the top  [Expected result: True]"
    print compare_comp_ids( xml_str4, xml_str5 )

    print "===== Rspec Type ======"
    print is_rspec_of_type( request_str, 'request' )
    print is_rspec_of_type( manifest_str, 'manifest' )
    print is_rspec_of_type( request_str, 'request', 'GENI 3')
    print is_rspec_of_type( manifest_str, 'manifest', 'GENI 3' )
    print is_rspec_of_type( request_str, 'request', 'ProtoGENI 2')
    print is_rspec_of_type( manifest_str, 'manifest', 'ProtoGENI 2' )
    print is_rspec_of_type( request_str, 'foo' )
    print is_rspec_of_type( manifest_str, 'bar' )

    print "===== Has Child Nodes ====="
    print has_child_node( request_str )
    print has_child_node( manifest_str )
    print has_child_node( xml_str )
    print has_child_node( xml_str2 )
    print has_child_node( xml_str3 )
    print has_child_node( xml_str4 )
    print has_child_node( xml_str5 )
