

all:
	@echo "Creating certificates"
	@echo "------------------------"
	@echo ""
	@echo ""
	@echo "Generating private Key (1024 bits)..."
	@openssl genrsa -passout pass:donotcare -des3 -out sr_am.key 1024
	@echo ""
	@echo "Generating request..."
	@openssl req -passin pass:donotcare -new -key sr_am.key -out sr_am.csr
	@echo ""
	@echo "Removing passphrase of the key..."
	@cp sr_am.key sr_am.key.org
	@openssl rsa -passin pass:donotcare -in sr_am.key.org -out sr_am.key
	@echo ""
	@echo "Self-signing the certificate..."
	@openssl x509 -req -days 3650 -in sr_am.csr -signkey sr_am.key -out sr_am.crt
	@echo "Cleaning the house..."
	@rm -rf sr_am.key.org sr_am.csr
