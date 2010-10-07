'''
Created on Oct 6, 2010

@author: jnaous
'''

def home(request, slice_id):
    """Show buttons to download and upload rspecs."""
    
    if request.method == "POST":
        form = # TODO: Also show the slice URN
        