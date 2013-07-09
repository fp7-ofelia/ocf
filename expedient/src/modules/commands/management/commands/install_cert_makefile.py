"""A command to run the tests specified in settings.TEST_APPS

Created on Aug 22, 2010

@author: jnaous
"""
import os
import pkg_resources
from django.core.management.base import NoArgsCommand

MAKEFILE = \
r"""
##
##  Makefile to keep the hash symlinks in SSLCACertificatePath up to date
##  Copyright (c) 1998-2001 Ralf S. Engelschall, All Rights Reserved. 
##

SSL_PROGRAM=

update: clean
    -@ssl_program="$(SSL_PROGRAM)"; \
    if [ ".$$ssl_program" = . ]; then \
        for dir in . `echo $$PATH | sed -e 's/:/ /g'`; do \
            for program in openssl ssleay; do \
                if [ -f "$$dir/$$program" ]; then \
                    if [ -x "$$dir/$$program" ]; then \
                        ssl_program="$$dir/$$program"; \
                        break; \
                    fi; \
                fi; \
            done; \
            if [ ".$$ssl_program" != . ]; then \
                break; \
            fi; \
        done; \
    fi; \
    if [ ".$$ssl_program" = . ]; then \
        echo "Error: neither 'openssl' nor 'ssleay' program found" 1>&2; \
        exit 1; \
    fi; \
    for file in *.crt; do \
        if [ ".`grep SKIPME $$file`" != . ]; then \
            echo dummy |\
            awk '{ printf("%-15s ... Skipped\n", file); }' \
            "file=$$file"; \
        else \
            n=0; \
            while [ 1 ]; do \
                hash="`$$ssl_program x509 -noout -hash <$$file`"; \
                if [ -r "$$hash.$$n" ]; then \
                    n=`expr $$n + 1`; \
                else \
                    echo dummy |\
                    awk '{ printf("%-15s ... %s\n", file, hash); }' \
                    "file=$$file" "hash=$$hash.$$n"; \
                    ln -s $$file $$hash.$$n; \
                    break; \
                fi; \
            done; \
        fi; \
    done

clean:
    -@rm -f [0-9a-fA-F]*.[0-9]*

"""

class Command(NoArgsCommand):
    help = "This command runs the tests that are bundled with Expedient."

    def handle_noargs(self, **options):
        from django.conf import settings
        dir = os.path.abspath(settings.XMLRPC_TRUSTED_CA_PATH)
        loc = os.path.join(dir, "Makefile")
        print "Writing the Makefile into directory %s..." % dir
        pkg_resources.ensure_directory(loc)
        f = open(loc, mode="w")
        f.write(MAKEFILE)
        f.close()
        print "Done."
