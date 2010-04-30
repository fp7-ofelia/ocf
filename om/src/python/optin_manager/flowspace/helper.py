
def IntToDottedIP( intip ):
        octet = ''
        for exp in [3,2,1,0]:
                octet = octet + str(intip / ( 256 ** exp )) + "."
                intip = intip % ( 256 ** exp )
        return(octet.rstrip('.'))
 
def DottedIPToInt( dotted_ip ):
        exp = 3
        intip = 0
        for quad in dotted_ip.split('.'):
                intip = intip + (int(quad) * (256 ** exp))
                exp = exp - 1
        return(intip)

def IPRangeToString(intip1, intip2):
    frm = IntToDottedIP(intip1) + "-"
    total = frm + IntToDottedIP(intip2)
    return total