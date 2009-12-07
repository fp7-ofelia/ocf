### $Id: debug.py 14192 2009-07-02 08:40:01Z thierry $
### $URL: http://svn.planet-lab.org/svn/sfa/tags/sfa-0.9-5/sfa/util/debug.py $

import time
import sys
import syslog

class unbuffered:
    """
    Write to /var/log/httpd/error_log. See

    http://www.modpython.org/FAQ/faqw.py?req=edit&file=faq02.003.htp
    """

    def write(self, data):
        sys.stderr.write(data)
        sys.stderr.flush()

log = unbuffered()

def profile(callable):
    """
    Prints the runtime of the specified callable. Use as a decorator, e.g.,

        @profile
        def foo(...):
            ...

    Or, equivalently,

        def foo(...):
            ...
        foo = profile(foo)

    Or inline:

        result = profile(foo)(...)
    """

    def wrapper(*args, **kwds):
        start = time.time()
        result = callable(*args, **kwds)
        end = time.time()
        args = map(str, args)
        args += ["%s = %s" % (name, str(value)) for (name, value) in kwds.items()]
        print >> log, "%s (%s): %f s" % (callable.__name__, ", ".join(args), end - start)
        return result

    return wrapper

if __name__ == "__main__":
    def sleep(seconds = 1):
        time.sleep(seconds)

    sleep = profile(sleep)

    sleep(1)
