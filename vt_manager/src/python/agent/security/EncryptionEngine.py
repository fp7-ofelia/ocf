from OpenSSL import * 
import os 

#from OXA import PRIVATE_KEY

AGENT_PRIVATEKEY_PEM="certs/agent.key"
AM_CERTS = (
	(1,"certs/agent.crt"),
	(2,"certs/agent.crt"),
)

AGENT_PRIVATE_KEY = crypto.load_privatekey(crypto.FILETYPE_PEM,open(AGENT_PRIVATEKEY_PEM,'r').read())

class EncryptionEngine:

	@staticmethod
	def __getAMPublicKey(amId):
		for tuple in AM_CERTS:
			if tuple[0] == amId :
				return crypto.load_certificate(crypto.FILETYPE_PEM,open(tuple[1], 'r').read())
	
	@staticmethod
	def __applyEncryption(amId,inputString):
		
		#Check amId
		amPublicKey = EncryptionEngine.__getAMPublicKey(amId)

		#Encrypt using agent private key
		intermediateStep = crypto.x509.sign(AGENT_PRIVATE_KEY,inputString,"sha1")	
		
		#Apply Am public key
		return crypto.x509.sign(amPublicKey,intermediateStep,"sha1")	
	
	@staticmethod
	def decryptMessageFromAm(amId,inputString):
		return EncryptionEngine.__applyEncryption(amId,inputString) 
			
	@staticmethod
	def encryptMessageToAm(amId,inputString):
		return EncryptionEngine.__applyEncryption(amId,inputString)

print crypto.__dict__.keys()
print EncryptionEngine.encryptMessageToAm(1,"hola") 
