class Backend:
    def __init__(self,instance=None,**kwargs):
        self.instance = instance
    def __getattr__(self,name):
        def func(*args, **kwds):
            return getattr(self.instance,name)(*args, **kwds)
        return func    

           
