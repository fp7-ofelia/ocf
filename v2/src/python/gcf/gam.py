#!/usr/bin/python

import sys

# Check python version. Requires 2.6 or greater, but less than 3.
if sys.version_info < (2, 6):
    raise Exception('Must use python 2.6 or greater.')
elif sys.version_info >= (3,):
    raise Exception('Not python 3 ready')

import xml.dom.minidom as minidom
import optparse
import geni

class CredentialVerifier(object):

    def verify(self, credential, permissions):
        return True


class Resource(object):

    def __init__(self, id, type):
        self._id = id
        self._type = type

    def toxml(self):
        template = '<resource><type>%s</type><id>%s</id></resource>'
        return template % (self._type, self._id)

    def urn(self):
        urn = 'IDN geni.net//resource//%s_%s' % (self._type, str(self._id))
        return urn

    def __eq__(self, other):
        return self._id == other._id

    def __neq__(self, other):
        return self._id != other._id

    @classmethod
    def fromdom(cls, element):
        """Create a Resource instance from a DOM representation."""
        type = element.getElementsByTagName('type')[0].firstChild.data
        id = int(element.getElementsByTagName('id')[0].firstChild.data)
        return Resource(id, type)

class Sliver(object):

    def __init__(self, urn, resources):
        self.urn = urn
        self._resources = resources

    def resources(self):
        return self._resources


class AggregateManager(object):

    def __init__(self):
        self._slivers = dict()
        self._resources = [Resource(x, 'Nothing') for x in range(10)]

    def GetVersion(self):
        return dict(geni_api=1)

    def ListResources(self, credentials, options):
        compressed = False
        if options and 'geni_compressed' in options:
            compressed  = options['geni_compressed']
        # return an empty rspec
        result = ('<rspec>' + ''.join([x.toxml() for x in self._resources])
                  + '</rspec>')
        if compressed:
            result = xmlrpclib.Binary(zlib.compress(result))
        return result

    def CreateSliver(self, slice_urn, credentials, rspec):
        print 'CreateSliver(%r)' % (slice_urn)
        if slice_urn in self._slivers:
            raise Exception('Sliver already exists.')
        rspec_dom = minidom.parseString(rspec)
        resources = list()
        for elem in rspec_dom.documentElement.childNodes:
            resource = Resource.fromdom(elem)
            if resource not in self._resources:
                raise Exception('Resource not available')
            resources.append(resource)
        sliver = Sliver(slice_urn, resources)
        # remove resources from available list
        for resource in resources:
            self._resources.remove(resource)
        self._slivers[slice_urn] = sliver
        return '<rspec>%s</rspec>' % resource.toxml()

    def DeleteSliver(self, slice_urn, credentials):
        print 'DeleteSliver(%r)' % (slice_urn)
        if slice_urn in self._slivers:
            sliver = self._slivers[slice_urn]
            # return the resources to the pool
            self._resources.extend(sliver.resources())
            del self._slivers[slice_urn]
            return True
        else:
            return False

    def SliverStatus(self, slice_urn, credentials):
        # Loop over the resources in a sliver gathering status.
        print 'SliverStatus(%r)' % (slice_urn)
        if slice_urn in self._slivers:
            sliver = self._slivers[slice_urn]
            sliver_status = None
            res_status = list()
            for res in sliver.resources():
                urn = geni.urn_to_publicid(res.urn())
                res_status.append(dict(geni_urn=urn,
                                       geni_status='ready',
                                       geni_error=''))
            return dict(geni_urn=sliver.urn,
                        # XXX need to calculate sliver status
                        geni_status='ready',
                        geni_resources=res_status)
        else:
            raise Exception('No such slice.')

    def RenewSliver(self, slice_urn, credentials, expiration_time):
        print 'RenewSliver(%r, %r)' % (slice_urn, expiration_time)
        return False

    def Shutdown(self, slice_urn, credentials):
        print 'Shutdown(%r)' % (slice_urn)
        return False


def parse_args(argv):
    parser = optparse.OptionParser()
    parser.add_option("-k", "--keyfile",
                      help="key file name", metavar="FILE")
    parser.add_option("-c", "--certfile",
                      help="certificate file name", metavar="FILE")
    parser.add_option("-r", "--rootcafile",
                      help="root ca certificate file name", metavar="FILE")
    # Could try to determine the real IP Address instead of the loopback
    # using socket.gethostbyname(socket.gethostname())
    parser.add_option("-H", "--host", default='127.0.0.1',
                      help="server ip", metavar="HOST")
    parser.add_option("-p", "--port", type=int, default=8000,
                      help="server port", metavar="PORT")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    return parser.parse_args()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    opts, args = parse_args(argv)
    ams = geni.AggregateManagerServer((opts.host, opts.port),
                                      delegate=AggregateManager(),
                                      keyfile=opts.keyfile,
                                      certfile=opts.certfile,
                                      ca_certs=opts.rootcafile)
    print 'Listening on port %d...' % (opts.port)
    ams.serve_forever()

if __name__ == "__main__":
    sys.exit(main())
