"""
Keeps the dummy AM server running.

@date: Jun 12, 2013
@author: CarolinaFernandez
"""

from communications.XmlRpcServer import XmlRpcServer

def main():
    #Engage XMLRPC
    XmlRpcServer.createInstanceAndEngage(None)

#Calling main
if __name__ == "__main__":
    main()

