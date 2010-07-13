def create_or_update(model, filter_attrs, new_attrs={}, skip_attrs=[]):
    '''
    If an object is found matching filter attrs, then update
    the object with new_attrs else create the object with filter_attrs and
    new_attrs. new_attrs overrides filter_attrs. 
    To leave some keys from filter_attrs unused, specify them in skip_attrs
    (such as auto-created slug fields or to use default values).
    Returns tuple (object, created) where created is True if object is created.
    '''
    from django.db.utils import IntegrityError
    try:
        obj = model.objects.get(**filter_attrs)
    except model.DoesNotExist:
        # remove fields that aren't to be changed
        for k in skip_attrs:
            del filter_attrs[k]
        # remove entries that use related fields
        for k in filter_attrs.keys():
            if "__" in k:
                del filter_attrs[k]
        filter_attrs.update(new_attrs)
        try:
            obj = model.objects.create(**filter_attrs)
        except IntegrityError:
            import traceback
            traceback.print_exc()
            raise
        
        created = True
    else:
        created = False
        for k, v in new_attrs.items():
            setattr(obj, k, v)
            obj.save()
    return (obj, created)
