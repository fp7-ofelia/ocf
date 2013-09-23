# License

This code in "ext" is taken from GCF 2.3.3 (see http://trac.gpolab.bbn.com/gcf/wiki/GettingGcf).

Please respect the licenses from GCF and then in turn the PlanetLab licence.

# Adjust imports in gcf code

In order to fix the imports, please adjust the `__init__.py` to comment the imports for `Clearinghouse`, `ReferenceAggregateManager, AggregateManagerServer`.

and add `ext.` to all (internal) imports in sub-packages.