'''
Created on May 14, 2010

@author: jnaous
'''

## XMLRPC
# DONE: Limit the scope of callable XMLRPC calls depending on the url
# DONE: Update rpc4django tests

## GAPI
# TODO: Add permissions to calls
# TODO: Check the security of calls to the Django GAPI, use x509 certs?
# TODO: Add tests for CH ListResources with slice_urn specified
# TODO: Add tests for CH ListResources with geni_available=False
# TODO: Change to stateful
# TODO: Change rspec to allow remote opt-in 

## CH
# TODO: Go through and add length checking so that we don't have silent truncations on saving models
### Aggregate
# TODO: Add tests for adding an Aggregate to the CH
# TODO: Add Permissions for aggregates - urls, create/update/delete
### Permissions
# DONE: Add Middleware to catch PermissionDenied exceptions and redirect
# DONE: Add URLs for permissions: default and others.
# DONE: Remove all old permission stuff from CH apps
# DONE: Add pages/views for permission management
# DONE: Add tests for permission system
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

## Openflow
# TODO: Add remote opt-in API in OM
# TODO: Add remote opt-in API in CH

## Documentation
# TODO: Add info on doing flush and syncdb
# TODO: Add info on changing the secret key
