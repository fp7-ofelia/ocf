DIRS = ../db ../src
README = README
INSTALL = install.sh
FILES = Makefile $(README) $(INSTALL) CHANGES
VERSION = 0.0.3-alpha1

NAME = expedient

EGENI_ROOT = $(shell cd .. && pwd)
SED_EGENI_ROOT = $(subst /,\/,$(shell cd .. && pwd))

APACHE_CONF_FILES = \
src/config/expedient/clearinghouse/apache/vhost-clearinghouse.conf \
src/config/openflow/optin_manager/apache/vhost-optinmgr.conf

PROJECTS = expedient/clearinghouse openflow/optin_manager

TARGET = $(NAME)-$(VERSION)

dist: $(TARGET).tar.gz
	
$(TARGET).tar.gz: $(FILES)
	rm -rf $(TARGET) $@
	mkdir $(TARGET)
	for d in $(DIRS); do \
		cp -R $$d $(TARGET); \
	done
	for f in $(FILES); do \
		cp $$f $(TARGET); \
	done
	for p in $(PROJECTS); do \
		mv $(TARGET)/src/python/$$p/deployment_settings.py $(TARGET)/src/python/$$p/settings.py; \
	done
	sed -i '{s/VERSION=.*/VERSION=$(VERSION)/}' $(TARGET)/$(INSTALL)
	sed -i '{s/x\.y\.z/$(VERSION)/}' $(TARGET)/$(README)
	for f in $(APACHE_CONF_FILES); do \
		sed -i '{s/$(SED_EGENI_ROOT)/\/srv\/www\/expedient/}' $(TARGET)/$$f; \
	done
	tar -zcf $@ $(TARGET)
	rm -rf $(TARGET)

install:
	./install.sh

.PHONY: dist install
