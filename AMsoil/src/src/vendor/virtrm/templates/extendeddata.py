try:
   import cpickle as pickle
except:
   import pickle

class ExtendedData:

    def __init__(self, track=True):
        self.extensions = list()
        self.extension_track = track

    def get_extension_track(self):
        return self.extension_track
        
    def set_extension_track(self, boolean):
        self.extension_track = boolean 

    def add_extension(self, name, value):
        setattr(self, name, value)
        if not name in self.extensions:
            self.append_extension_list(name)

    def remove_extension(self, name):
        delattr(self, name)
        self.remove_extension_list(name)

    def update_extension(self,name,value):
        self.add_extension(name, value)

    def get_extension(self, name):
        return getattr(self, name)
 
    def dump(self):
        if self.get_extension_track:
            toPrint=""
            self.extensions.sort()
            for extension in self.extensions:
                toPrint = extension + " : " + str(getattr(self,extension)) + "\n"
            return toPrint

        else:
            print "The Extension track is deactivated" 
     
    def append_extension_list(self, name):
        if self.get_extension_track():
            self.extensions.append(name)

    def remove_extension_list(self, name):
        if self.get_extension_track():
            self.extensions.remove(name)
 
    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(serialized):
        return pickle.loads(serialized)
