

all:
	@echo "Creating certificates"
	@echo "------------------------"
	@echo ""
	@echo ""
	@echo "Generating private Key (1024 bits)..."
	@openssl genrsa -passout pass:donotcare -des3 -out agent.key 1024
	@echo ""
	@echo "Generating request..."
	@openssl req -passin pass:donotcare -new -key agent.key -out agent.csr
	@echo ""
	@echo "Removing passphrase of the key..."
	@cp agent.key agent.key.org
	@openssl rsa -passin pass:donotcare -in agent.key.org -out agent.key
	@echo ""
	@echo "Self-signing the certificate..."
	@openssl x509 -req -days 3650 -in agent.csr -signkey agent.key -out agent.crt
	@echo "Cleaning the house..."
	@rm -rf agent.key.org agent.csr
