import xmlrpclib

server = xmlrpclib.Server('https://84.88.40.12:9229')

print server.send('https://84.88.40.12:9229',1,"hfw9023jf0sdjr0fgrbjk", open('mon.xml', 'r').read())

