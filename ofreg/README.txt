INSTALLATION:
- get the code
  # cd /opt
  # git clone ssh://[user]@alpha.fp7-ofelia.eu/home/ofelia/ofelia-git
  # mv ofelia-git ofreg
  # cd ofreg
  # git checkout ofreg

- configure ofreg
  # cd /opt/ofreg/ofreg
  # cp localsettings.py-example localsettings.py
  - edit localsettings.py
  # ./manage.py syncdb
  # chown www-data:www-data -R db

- install python, django, django-evolution (see manual of expedient)
- install python-ldap
  # apt-get install python-ldap

- install webserver and wsgi (see manual of expedient)

- create ssl certificates
  # cd /opt/ofreg/ofreg/deploy/ssl
  # ./make_key.sh

- configure host
  # cd /opt/ofreg/ofreg/deploy
  # ln -s /opt/ofreg/ofreg/deploy/apache-ofreg.conf /etc/apache2/sites-available/ofreg.conf
  # a2ensite ofreg.conf


REQUIREMENTS:
python
django
python-ldap (http://www.python-ldap.org/doc/html/installing.html , on mac install `sudo port install py26-ldap`)
django-evolution




STUFF:
port forwarding (access via 127.0.0.1:19389):
ssh root@130.149.58.29 -L 19389:10.216.4.2:389

admin dn:
cn=admin,dc=fp7-ofelia,dc=eu
pass (ofelia reverse): ailefo

ip from didier: 10.216.4.2
prefix: 10.216.16.0

ubuntu1# ldapsearch -x -Z -h 10.216.4.2 -b ou=users,dc=fp7-ofelia,dc=eu