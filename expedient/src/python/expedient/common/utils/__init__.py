from django.db import transaction
def create_or_update(model, filter_attrs, new_attrs={}, skip_attrs=[], using=None):
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
        create_attrs = filter_attrs.copy()
        # remove fields that aren't to be changed
        for k in skip_attrs:
            del create_attrs[k]
        # remove entries that use related fields
        for k in create_attrs.keys():
            if "__" in k:
                del create_attrs[k]
        create_attrs.update(new_attrs)
        try:
            obj = model(**create_attrs)
            sid = transaction.savepoint(using=using)
            obj.save(force_insert=True, using=using)
            transaction.savepoint_commit(sid, using=using)
            return (obj, True)
        except IntegrityError, e:
            transaction.savepoint_rollback(sid, using=using)
            try:
                obj = model.objects.get(**filter_attrs)
                return (obj, False)
            except model.DoesNotExist:
                raise e
        
    else:
        for k, v in new_attrs.items():
            setattr(obj, k, v)
            obj.save()
        return (obj, False)
