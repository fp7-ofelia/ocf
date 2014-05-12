def handleFault(fault, value):
    try:
        raise fault(value)
    except fault as e:
        e.__showMessage__()


class ExceptionMAC(Exception):
    def __init__(self, value):
         self.value = value
    def __str__(self):
        return repr(self.value)

    def __showMessage__(self):
        print self.__class__.__name__ + " : " + self.result[self.value]

    result = { 'WRONG_CHAR' : "The MAC addres has some irregular character", \
                'WRONG_LENGTH':  "The MAC address has a wrong length", \
                'WRONG_PART' : "The MAC addres is not properly defined",\
                'WRONG_XEN' : "Tha MAC addres must start with 00:16:3e"\
            }


class ExceptionIp(Exception):
    def __init__(self, value):
         self.value = value
    def __str__(self):
        return repr(self.value)

    def __showMessage__(self):
        print self.__class__.__name__ + ": Wrong IP\n"


class ExceptionMemory(Exception):
    def __init__(self, value):
         self.value = value
    def __str__(self):
        return repr(self.value)

    def __showMessage__(self):
        print self.__class__.__name__ + ": Max Memory is 4GB\n"


class ExceptionState(Exception):
    def __init__(self, value):
         self.value = value
    def __str__(self):
        return repr(self.value)

    def __showMessage__(self):
        print self.__class__.__name__ + ": %s is unknown. Possible values are CREATION for VM creaton info and LAST for last state" % self.value

