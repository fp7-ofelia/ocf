class IP(object):
    """
    Value class. Deals with IPv4 IPs.
    This implementation is just an example and is hence neither fully fledged nor efficient.
    """
    def __init__(self, bytes):
        """Receives a list of ints which needs to be 4 long."""
        if len(bytes) != 4: raise ValueError("The given IP does not have 4 bytes")
        self.bytes = bytes[:]

    @classmethod
    def from_str(self, ip_str):
        """Return an IP instance parsed from the given string"""
        bytes = ip_str.split(".")
        if len(bytes) != 4: raise ValueError("The given IP does not have 4 bytes or is not seperated by '.'")
        bytes = [int(b) for b in bytes]
        return IP(bytes)

    def upto(self, to_ip):
        """Returns a list of IPs starting from the instance's IP upto the given IP.
        Example: IP(192,168,1,10).upto(IP(192,168,1,12)) => [IP(192,168,1,10), IP(192,168,1,11), IP(192,168,1,12)]"""
        result = []
        current_ip = self
        while current_ip <= to_ip:
            result.append(current_ip)
            current_ip = current_ip.next_ip()
        return result
        
    def next_ip(self):
        """Returns the subsequent IP to this object's IP."""
        result = IP(self.bytes)
        carry = True
        for i in range(3, -1, -1):
            if carry:
                result.bytes[i]+=1
                if result.bytes[i] > 255:
                    result.bytes[i]= 1 # this not quite right
                    # carry stays True
                else:
                    carry=False
        return result
    
    def __eq__(self, other):
        if type(other) != IP: raise ValueError("This class only supports comparing with other IPs.")
        return self.bytes == other.bytes

    def __le__(self, other):
        if type(other) != IP: raise ValueError("This class only supports comparing with other IPs.")
        for i in range(0,4):
            if self.bytes[i] < other.bytes[i]:
                return True
            if self.bytes[i] > other.bytes[i]:
                return False
            # only keep moving to the next byte if the current byte is the same
        return True

    def __str__(self):
        return ".".join([str(b) for b in self.bytes])

