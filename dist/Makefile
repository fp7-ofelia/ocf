DIRS = db src
README = README
INSTALL = install.sh
FILES = Makefile $(README) $(INSTALL) CHANGES INSTALL

NAME = expedient

EGENI_ROOT = $(shell cd .. && pwd)
SED_EGENI_ROOT = $(subst /,\/,$(shell cd .. && pwd))

APACHE_CONF_FILES = \
src/config/expedient/clearinghouse/apache/vhost-clearinghouse.conf \
src/config/openflow/optin_manager/apache/vhost-optinmgr.conf

PROJECTS = expedient/clearinghouse openflow/optin_manager

$(NAME)-%.tar.gz: $(FILES)
	@echo "*** Checking out the version from the working repo"
	@rm -rf $(NAME)-$*
	@rm -rf $(NAME)-$*-temp
	@git clone ../ $(NAME)-$*
	@cd $(NAME)-$*; git checkout master; git checkout $*
	@rm -rf $(NAME)-$*/.git
	@rm -rf $(NAME)-$*/.gitignore
	@mv $(NAME)-$* $(NAME)-$*-temp
	@mkdir $(NAME)-$*
	@echo "*** Adding wanted dirs"
	@for d in $(DIRS); do \
		cp -R $(NAME)-$*-temp/$$d $(NAME)-$*; \
	done
	@echo "*** Moving files into target directory's root"
	@for f in $(FILES); do \
		cp $(NAME)-$*-temp/dist/$$f $(NAME)-$*; \
	done
	@rm -rf $(NAME)-$*-temp
	@echo "*** Replacing settings with clean deployment settings"
	@for p in $(PROJECTS); do \
		mv $(NAME)-$*/src/python/$$p/deployment_settings_clean.py \
		$(NAME)-$*/src/python/$$p/deployment_settings.py; \
	done
	@echo "*** Updating the version in files"
	@sed -i '{s/VERSION=.*/VERSION=$*/}' $(NAME)-$*/$(INSTALL)
	@sed -i '{s/x\.y\.z/$*/}' $(NAME)-$*/$(README)
	@echo "*** Cleaning the apache vhost configuration files"
	@for f in $(APACHE_CONF_FILES); do \
		sed -i '{s/\(Use SimpleSSLWSGIVHost\) \(.*\) \(.*\) \(.*\)/\1 \2 \3 \/srv\/www\/expedient/}' $(NAME)-$*/$$f; \
	done
	@echo "*** Packaging and removing temporary dir"
	@tar -zcf $@ $(NAME)-$*
	@rm -rf $(NAME)-$*

install:
	@./install.sh
	@./install_clean.sh
update:
	@./install.sh

.PHONY: dist install test update
