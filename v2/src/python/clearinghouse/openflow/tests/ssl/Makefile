APACHE_CERTS_DIR=/etc/apache2/ssl.crt
APACHE_KEYS_DIR=/etc/apache2/ssl.key
APACHE_RC=/etc/init.d/apache2
GCF_DIR=../../../../gcf
EXP_NAME=experimenter
CA_NAME=ca
CH_NAME=ch
AM_NAME=server
CERT=crt
KEY=key

SERVER_CERT=$(AM_NAME).$(CERT)
SERVER_KEY=$(AM_NAME).$(KEY)
CA_CERT=$(CA_NAME).$(CERT)

all: ca ch am exp apache

ca: $(CA_NAME).$(CERT) $(CA_NAME).$(KEY)
ch: $(CH_NAME).$(CERT) $(CH_NAME).$(KEY)
am: $(AM_NAME).$(CERT) $(AM_NAME).$(KEY)
exp: $(EXP_NAME).$(CERT) $(EXP_NAME).$(KEY)

apache:
	sudo $(MAKE) apachesymlinks

apachesudo: $(APACHE_CERTS_DIR)/$(SERVER_CERT) $(APACHE_KEYS_DIR)/$(SERVER_KEY) $(APACHE_CERTS_DIR)/$(CA_CERT)
	
apachesymlinks: apachesudo
	sudo $(MAKE) -C $(APACHE_CERTS_DIR)
	sudo $(APACHE_RC) restart
	
$(APACHE_CERTS_DIR)/$(SERVER_CERT): $(SERVER_CERT)
	sudo cp $< $(APACHE_CERTS_DIR)

$(APACHE_CERTS_DIR)/$(CA_CERT): $(CA_CERT)
	sudo cp $< $(APACHE_CERTS_DIR)

$(APACHE_KEYS_DIR)/$(SERVER_KEY): $(SERVER_KEY)
	sudo cp $< $(APACHE_KEYS_DIR)

$(EXP_NAME).%: $(GCF_DIR)/init-ca.py $(CA_NAME).$(CERT)
	python $(GCF_DIR)/init-ca.py --exp

$(CH_NAME).%: $(GCF_DIR)/init-ca.py $(CA_NAME).$(CERT)
	python $(GCF_DIR)/init-ca.py --ch
	
$(AM_NAME).%: $(GCF_DIR)/init-ca.py $(CA_NAME).$(CERT)
	python $(GCF_DIR)/init-ca.py --am

$(CA_NAME).%: $(GCF_DIR)/init-ca.py
	python $(GCF_DIR)/init-ca.py --ca
	
clean:
	rm -rf $(CA_NAME).$(CERT) $(CA_NAME).$(KEY)
	rm -rf $(CH_NAME).$(CERT) $(CH_NAME).$(KEY)
	rm -rf $(AM_NAME).$(CERT) $(AM_NAME).$(KEY)
	rm -rf $(EXP_NAME).$(CERT) $(EXP_NAME).$(KEY)

cleanapache:
	sudo rm -rf $(APACHE_CERTS_DIR)/$(SERVER_CERT) $(APACHE_CERTS_DIR)/$(CA_CERT) $(APACHE_KEYS_DIR)/$(SERVER_KEY)

.PHONY: ca ch am exp apache apachesudo apachesymlinks clean cleanapache