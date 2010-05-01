from transport import PyCURLTransport, PyCURLSafeTransport

def create_or_update(model, filter_attrs, new_attrs={}):
    '''
    If an object is found matching filter attrs, then update
    the object with new_attrs else create the object with both filter_attrs and
    new_attrs. new_attrs overrides filter_attrs. Returns True if created.
    '''
    
    rows = model.objects.filter(**filter_attrs).update(**new_attrs)
    if not rows:
        filter_attrs.update(new_attrs)
        model.objects.create(**filter_attrs)
        return True
    return False