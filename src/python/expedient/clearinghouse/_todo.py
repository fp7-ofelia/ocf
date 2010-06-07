'''
Created on May 14, 2010

@author: jnaous
'''

## XMLRPC
# TODO: Add permissions to XMLRPC calls
# DONE: Limit the scope of callable XMLRPC calls depending on the url
# TODO: Update rpc4django tests

## GAPI
# TODO: Check the security of calls to the Django GAPI, use x509 certs?
# TODO: Add tests for CH ListResources with slice_urn specified
# TODO: Add tests for CH ListResources with geni_available=False

## CH
# TODO: Go through and add length checking so that we don't have silent truncations on saving models
### Aggregate
# TODO: Add tests for adding an Aggregate to the CH
# TODO: Add Permissions for aggregates - urls, create/update/delete
### Permissions
# DONE: Add Middleware to catch PermissionDenied exceptions and redirect
# DONE: Add URLs for permissions: default and others.
# TODO: Remove all old permission stuff from CH apps
# TODO: Add pages/views for permission management
# TODO: Add tests for permission system
### Project
# TODO: Add pages/views for project management
# TODO: Add permissions for projects
# TODO: Add role management
### Resources
# TODO: Add permissions for slivers and sliversets
### Slice
# TODO: Add permissions for Slice
### Users
# TODO: Add permissions for users
### Messaging
# TODO: Add permissions for messaging
