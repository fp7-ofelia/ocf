try:
   import cpickle as pickle
except:
   import pickle

class ExtendedData:

    def __init__()
        self.extensions = list()

    def add_extension(self, name, value):
        setattr(self, name, value)
        if not name in self.extensions:
            self.extensions.append(name)

    def remove_extension(name):
        delattr(self, name)
        self.extensions.remove(name)

    def update_extension(name,value):
        self.add_extension(name, value)

    def get_extension(self, name):
        return getattr(self, name)
  
    def serialize(self):
        return loads(self)
   
    def dump(self):
        toPrint = "Extensions: "
        for extension in extensions:
            toPrint = extension + " -> " str(getattr(self,extension)) + "\n"
        print toPrint
 
    @staticmethod
    def deserialize(serilized):
        return dumps(serialized)
