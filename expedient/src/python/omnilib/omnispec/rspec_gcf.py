#----------------------------------------------------------------------
# Copyright (c) 2010 Raytheon BBN Technologies
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
from omnilib.omnispec.omnispec import OmniSpec, OmniResource
import xml.etree.ElementTree as ET

def can_translate(rspec):
    return rspec.startswith('<rspec type="GCF"')

def rspec_to_omnispec(urn, rspec):
    # URN is that of the AM
    ospec = OmniSpec("rspec_gcf", urn)
    doc = ET.fromstring(rspec)

    for res in doc.findall('resource'):        
        type = res.find('type').text
        id = res.find('id').text
        rurn = res.find('urn').text
        available = res.find('available').text
        available = available.lower() == 'true'

        r = OmniResource(id, 'node ' + id, type)
        r.set_allocated(not available)
        ospec.add_resource(rurn, r)
    return ospec

def omnispec_to_rspec(omnispec, filter_allocated):
    # Convert it to XML
    root = ET.Element('rspec')
    for _, r in omnispec.get_resources().items():
        if filter_allocated and not r.get_allocate():
            continue

        res = ET.SubElement(root, 'resource')
        ET.SubElement(res, 'type').text = r.get_type()
        ET.SubElement(res, 'id').text = r.get_name()
        ET.SubElement(res, 'available').text = str(not r.get_allocated())

    return ET.tostring(root)
