.. Expedient documentation master file, created by
   sphinx-quickstart on Wed Aug 11 14:56:40 2010.

.. _home:

Welcome to Expedient's documentation!
#####################################

|Expedient|_ is a pluggable GENI_ control framework platform that strives to provide a
rich and intuitive user interface for experimenters to create and run
experiments and an easy development environment for developers to add new
types of resources and new user interfaces.

|Expedient| does not
interfere with how GENI resources work. It does not impose enforce semantics
on resources and it does not force the resources to obey a particular
API. This makes it easier for resource developers to create plugins that
add new types of resources to Expedient.

There are a few things you can do next.

.. +----------------------------+---------------------------------+-----------------------------+
.. | For Users                  | For Developers                  | For Administrators          |
.. +============================+=================================+=============================+
.. | #. :ref:`user-tutorial`    | #. :ref:`developer-tutorial`    | #. :ref:`admin-install`     |
.. | #. :ref:`user-manual`      | #. :ref:`developer-manual`      | #. :ref:`admin-tutorial`    |
.. | #. :ref:`user-agg-plugins` | #. :ref:`developer-agg-plugins` | #. :ref:`admin-manual`      |
.. | #. :ref:`user-ui-plugins`  | #. :ref:`developer-ui-plugins`  | #. :ref:`admin-agg-plugins` |
.. |                            | #. `API Documentation`_         | #. :ref:`admin-ui-plugins`  |
.. +----------------------------+---------------------------------+-----------------------------+

Contents:

.. toctree::
   :maxdepth: 2
   
   user/index
   admin/index
   developer/index

Automatically generated API can be found here: `API Documentation`_

Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |Expedient| replace:: *Expedient*
.. _Expedient: http://yuba.stanford.edu/~jnaous/expedient/
.. _GENI: http://www.geni.net/
.. _API Documentation: api/index.html
