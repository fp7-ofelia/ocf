from excepts.NotImplementedException import NotImplementedException

'''
Abstract StoppableResource
'''

class StoppableResource(Resource):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def stop():
        raise NotImplementedException("Not implemented") 

 
