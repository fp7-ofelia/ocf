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

def MACtoInt(mac):
    result = 0
    exp = 5
    for dbl in mac.split(':'):
        result = result + int("0x%s"%dbl,16) * (256 ** exp)
        exp = exp - 1
    return result

def InttoMAC(mac):
    result = ""
    for exp in [5,4,3,2,1,0]:
        tmp = hex(int(mac/(256 ** exp)))
        result = result + tmp.split('x')[1] + ":"
        mac = mac % (256 ** exp)
    return (result.rstrip(":"))


