#----------------------------------------------------------------------
# Copyright (c) 2010 Raytheon BBN Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
#----------------------------------------------------------------------

class Framework_Base():
    """
    Framework_Base is an abstract class that identifies the minimal set of functions
    that must be implemented in order to add a control framework to omni.  
    
    Instructions for adding a new framework:
    
    Create "framework_X" in the frameworks directory, where X is your control framework.
    
    Create a Framework class in the file that inherits "Framework_Base" and fill out each of the functions.
    
    Edit the sample "omni_config" file and add a section for your framework, giving the section
    the same name as X used in framework_X.  For instance, 'sfa' or 'gcf'.  Your framework's section
    of the omni config *MUST* have a cert and key entry, which omni will use when talking to 
    the GENI Aggregate managers.
    
    """
    def get_user_cred(self):
        """
        Returns a user credential from the control framework as a string.
        """
        raise NotImplementedError('get_user_cred')
    
    def get_slice_cred(self, urn):
        """
        Retrieve a slice with the given urn and returns the signed credential as a string.
        """
        raise NotImplementedError('get_slice_cred')
    
    def create_slice(self, urn):    
        """
        If the slice already exists in the framework, it returns that.  Otherwise it creates the slice
        and returns the new slice as a string.
        """
        raise NotImplementedError('create_slice')

    def delete_slice(self, urn):
        """
        Removes the slice from the control framework.
        """
        raise NotImplementedError('delete_slice')

    def list_aggregates(self):
        """
        Get a list of available GENI Aggregates from the control framework.
        Returns: a dictionary where keys are urns and values are aggregate urls
        """
        raise NotImplementedError('list_aggregates')

    def slice_name_to_urn(self, name):
        """Convert a slice name to a slice urn."""
        # Default implementation just converts to generic URN.
        raise NotImplementedError('slice_name_to_urn')

    def renew_slice(self, urn, requested_expiration):
        """Renew a slice.

        urn is framework urn, already converted via slice_name_to_urn.
        requested_expiration is a datetime object.

        Returns the expiration date as a datetime. If there is an error,
        print it and return None.
        """
        raise NotImplementedError('renew_slice')
