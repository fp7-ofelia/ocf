include ../../../Make.vars 

EXTRA_DIST =\
	meta.xml

if PY_ENABLED
AM_CPPFLAGS += $(PYTHON_CPPFLAGS)
endif # PY_ENABLED 

pkglib_LTLIBRARIES =		\
	aggrMgr.la

aggrMgr_la_CPPFLAGS = $(AM_CPPFLAGS) -I $(top_srcdir)/src/nox -I $(top_srcdir)/src/nox/netapps/
aggrMgr_la_SOURCES = aggrMgr.cc rspec.cxx
aggrMgr_la_LDFLAGS = -module -export-dynamic

NOX_RUNTIMEFILES = meta.xml	

rspec.cxx: rspec.xsd
	xsd cxx-tree --generate-serialization rspec.xsd

all-local: nox-all-local
clean-local: nox-clean-local 
install-exec-hook: nox-install-local
