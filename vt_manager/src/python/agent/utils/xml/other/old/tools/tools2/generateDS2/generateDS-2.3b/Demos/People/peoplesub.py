#!/usr/bin/env python

#
# Generated Mon Feb  8 11:50:50 2010 by generateDS.py version 1.20e.
#

import sys
from string import lower as str_lower
from xml.dom import minidom

import peoplesup as supermod

#
# Globals
#

ExternalEncoding = 'ascii'

#
# Data representation classes
#

class peopleSub(supermod.people):
    def __init__(self, comments=None, person=None, programmer=None, python_programmer=None, java_programmer=None):
        supermod.people.__init__(self, comments, person, programmer, python_programmer, java_programmer)
supermod.people.subclass = peopleSub
# end class peopleSub


class commentsSub(supermod.comments):
    def __init__(self, emp=None, valueOf_='', mixedclass_=None, content_=None):
        supermod.comments.__init__(self, valueOf_, mixedclass_, content_)
supermod.comments.subclass = commentsSub
# end class commentsSub


class personSub(supermod.person):
    def __init__(self, vegetable=None, fruit=None, ratio=None, id=None, value=None, name=None, interest=None, category=None, agent=None, promoter=None, description=None):
        supermod.person.__init__(self, vegetable, fruit, ratio, id, value, name, interest, category, agent, promoter, description)
supermod.person.subclass = personSub
# end class personSub


class programmerSub(supermod.programmer):
    def __init__(self, vegetable=None, fruit=None, ratio=None, id=None, value=None, name=None, interest=None, category=None, agent=None, promoter=None, description=None, language=None, area=None, attrnegint=None, attrposint=None, attrnonnegint=None, attrnonposint=None, email=None, elposint=None, elnonposint=None, elnegint=None, elnonnegint=None, eldate=None, eltoken=None, elshort=None, ellong=None, elparam=None, elarraytypes=None):
        supermod.programmer.__init__(self, vegetable, fruit, ratio, id, value, name, interest, category, agent, promoter, description, language, area, attrnegint, attrposint, attrnonnegint, attrnonposint, email, elposint, elnonposint, elnegint, elnonnegint, eldate, eltoken, elshort, ellong, elparam, elarraytypes)
supermod.programmer.subclass = programmerSub
# end class programmerSub


class paramSub(supermod.param):
    def __init__(self, semantic=None, name=None, flow=None, sid=None, type_=None, id=None, valueOf_=''):
        supermod.param.__init__(self, semantic, name, flow, sid, type_, id, valueOf_)
supermod.param.subclass = paramSub
# end class paramSub


class python_programmerSub(supermod.python_programmer):
    def __init__(self, vegetable=None, fruit=None, ratio=None, id=None, value=None, name=None, interest=None, category=None, agent=None, promoter=None, description=None, language=None, area=None, attrnegint=None, attrposint=None, attrnonnegint=None, attrnonposint=None, email=None, elposint=None, elnonposint=None, elnegint=None, elnonnegint=None, eldate=None, eltoken=None, elshort=None, ellong=None, elparam=None, elarraytypes=None, nick_name=None, favorite_editor=None):
        supermod.python_programmer.__init__(self, vegetable, fruit, ratio, id, value, name, interest, category, agent, promoter, description, language, area, attrnegint, attrposint, attrnonnegint, attrnonposint, email, elposint, elnonposint, elnegint, elnonnegint, eldate, eltoken, elshort, ellong, elparam, elarraytypes, nick_name, favorite_editor)
supermod.python_programmer.subclass = python_programmerSub
# end class python_programmerSub


class java_programmerSub(supermod.java_programmer):
    def __init__(self, vegetable=None, fruit=None, ratio=None, id=None, value=None, name=None, interest=None, category=None, agent=None, promoter=None, description=None, language=None, area=None, attrnegint=None, attrposint=None, attrnonnegint=None, attrnonposint=None, email=None, elposint=None, elnonposint=None, elnegint=None, elnonnegint=None, eldate=None, eltoken=None, elshort=None, ellong=None, elparam=None, elarraytypes=None, status=None, nick_name=None, favorite_editor=None):
        supermod.java_programmer.__init__(self, vegetable, fruit, ratio, id, value, name, interest, category, agent, promoter, description, language, area, attrnegint, attrposint, attrnonnegint, attrnonposint, email, elposint, elnonposint, elnegint, elnonnegint, eldate, eltoken, elshort, ellong, elparam, elarraytypes, status, nick_name, favorite_editor)
supermod.java_programmer.subclass = java_programmerSub
# end class java_programmerSub


class agentSub(supermod.agent):
    def __init__(self, firstname=None, lastname=None, priority=None, info=None):
        supermod.agent.__init__(self, firstname, lastname, priority, info)
supermod.agent.subclass = agentSub
# end class agentSub


class special_agentSub(supermod.special_agent):
    def __init__(self, firstname=None, lastname=None, priority=None, info=None):
        supermod.special_agent.__init__(self, firstname, lastname, priority, info)
supermod.special_agent.subclass = special_agentSub
# end class special_agentSub


class boosterSub(supermod.booster):
    def __init__(self, member_id=None, firstname=None, lastname=None, other_name=None, classxx=None, other_value=None, type_=None, client_handler=None):
        supermod.booster.__init__(self, member_id, firstname, lastname, other_name, classxx, other_value, type_, client_handler)
supermod.booster.subclass = boosterSub
# end class boosterSub


class client_handlerSub(supermod.client_handler):
    def __init__(self, fullname=None, refid=None):
        supermod.client_handler.__init__(self, fullname, refid)
supermod.client_handler.subclass = client_handlerSub
# end class client_handlerSub


class infoSub(supermod.info):
    def __init__(self, rating=None, type_=None, name=None, valueOf_=''):
        supermod.info.__init__(self, rating, type_, name, valueOf_)
supermod.info.subclass = infoSub
# end class infoSub



def parse(inFilename):
    doc = minidom.parse(inFilename)
    rootNode = doc.documentElement
    rootObj = supermod.people.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" ?>\n')
    rootObj.export(sys.stdout, 0, name_="people",
        namespacedef_='xmlns:pl="http://kuhlman.com/people.xsd"')
    doc = None
    return rootObj


def parseString(inString):
    doc = minidom.parseString(inString)
    rootNode = doc.documentElement
    rootObj = supermod.people.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" ?>\n')
    rootObj.export(sys.stdout, 0, name_="people",
        namespacedef_='xmlns:pl="http://kuhlman.com/people.xsd"')
    return rootObj


def parseLiteral(inFilename):
    doc = minidom.parse(inFilename)
    rootNode = doc.documentElement
    rootObj = supermod.people.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('#from peoplesup import *\n\n')
    sys.stdout.write('import peoplesup as model_\n\n')
    sys.stdout.write('rootObj = model_.people(\n')
    rootObj.exportLiteral(sys.stdout, 0, name_="people")
    sys.stdout.write(')\n')
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


