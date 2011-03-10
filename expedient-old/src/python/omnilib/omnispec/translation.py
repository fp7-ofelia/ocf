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
""" Translate between RSpecs and OmniSpecs

    OmniSpecs are generalized RSpecs, capable of representing
    RSpecs from many types of aggregates.  OmniSpecs contain
    the data necessary to be translated back into a native RSpec.
"""


mod_name = 'omnilib.omnispec'


def rspec_to_omnispec(urn, rspec):        
    '''Translate the given RSpec from the given AM URN to an OSpec and
    return it, or throw an Exception if we cannot'''

    trans_mod = __import__(mod_name,fromlist=[mod_name])
    translators = trans_mod.all
    
    mod = None
    for translator in translators:
        mod = __import__(mod_name + '.' + translator, fromlist=[mod_name])
        if mod.can_translate(rspec):
            break
        else:
            mod = None
    
    if mod:
        return mod.rspec_to_omnispec(urn, rspec)
    
    raise Exception('Unknown RSpec Type from AM %s. Cant translate RSpec:\n%s' % (urn, rspec))
    
    

def omnispec_to_rspec(omnispec, filter_allocated):
    mod = __import__(mod_name + '.' + omnispec.get_type(), fromlist=[mod_name])
    return mod.omnispec_to_rspec(omnispec, filter_allocated)

