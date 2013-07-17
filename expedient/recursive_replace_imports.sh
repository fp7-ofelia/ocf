#!/bin/bash

###
# XXX USE MANUALLY; LINE BY LINE
#

# Finds every file under /opt/ofelia/expedient with old dependencies and replaces these

find /opt/ofelia/expedient/ -type f | xargs perl -pi -e 's/expedient\.clearinghouse/modules/g'
find /opt/ofelia/expedient/ -type f | xargs perl -pi -e 's/expedient\.common/common/g'
find /opt/ofelia/expedient/ -type f | xargs perl -pi -e 's/expedient_geni/geni_legacy\.expedient_geni/g'

# May be not necessary if every module inside 'geni_legacy' is added to system paths
find /opt/ofelia/expedient/src/geni_legacy/ -type f | xargs perl -pi -e 's/from geni\.util/from geni_legacy\.geni\.util/g'
find /opt/ofelia/expedient/src/geni_legacy/ -type f | xargs perl -pi -e 's/import geni\.util/import geni_legacy\.geni\.util/g'
find /opt/ofelia/expedient/src/geni_legacy/ -type f | xargs perl -pi -e 's/import sfa\./import geni_legacy\.sfa\./g'
find /opt/ofelia/expedient/src/geni_legacy/ -type f | xargs perl -pi -e 's/from sfa\./from geni_legacy\.sfa\./g'
# Fix duplicated imports
#find /opt/ofelia/expedient/ -type f | xargs perl -pi -e 's/geni_legacy\.geni_legacy\.expedient_geni/geni_legacy\.expedient_geni/g'


# Fix imports from settings
find /opt/ofelia/expedient/ -type f | xargs perl -pi -e 's/modules\.settings/settings/g'

# Fix imports from localsettings (might be not necessary if 'modules' is added to system paths)
find /opt/ofelia/expedient/ -type f | xargs perl -pi -e 's/from localsettings/from modules\.localsettings/g'
find /opt/ofelia/expedient/ -type f | xargs perl -pi -e 's/import localsettings/from modules import localsettings/g'

# Undo the last import change and set it as in original Expedient
#find /opt/ofelia/expedient/ -type f | xargs perl -pi -e 's/from modules\.localsettings/from localsettings/g'
#find /opt/ofelia/expedient/ -type f | xargs perl -pi -e 's/from modules import localsettings/import localsettings/g'

