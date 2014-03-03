import xmlrpclib

server = xmlrpclib.Server('https://127.0.0.1:9229')

#print server.send('https://84.88.40.12:9229',1,"hfw9023jf0sdjr0fgrbjk", open('mon.xml', 'r').read())
#print server.send('https://84.88.40.12:9229',1,"prova", open('prova2.xml', 'r').read())
file = open('prova2.xml', 'r')
print server.send('https://127.0.0.1:9229',1,"prova", file.read())
file.close()

