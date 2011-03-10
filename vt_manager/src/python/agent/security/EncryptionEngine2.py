import rsa
import os 
from M2Crypto import RSA
#from OXA import PRIVATE_KEY

AGENT_PRIVATEKEY_PEM="certs/agent.key"
AM_CERTS_PEM = (
	(1,"certs/agent.crt"),
	(2,"certs/agent.crt"),
)

#AGENT_PRIVATE_KEY = crypto.load_privatekey(crypto.FILETYPE_PEM,open(AGENT_PRIVATEKEY_PEM,'r').read())

class EncryptionEngine:

	@staticmethod
	def __getAMPublicKey(amId):
		for tuple in AM_CERTS_PEM:
			if tuple[0] == amId :
				#return open(tuple[1], 'r').read()
				return tuple[1]
	
	@staticmethod
	def __applyEncryption(amId,inputString):
		print EncryptionEngine.__getAMPublicKey(amId)
		amRsa = RSA.load_pub_key(EncryptionEngine.__getAMPublicKey(amId))	

		#Check amId
		#amPublicKey = EncryptionEngine.__getAMPublicKey(amId)

		#Encrypt using agent private key
		intermediateStep = public_encrypt('your message', RSA.pkcs1_oaep_padding)
 		return intermediateStep
		
		#Apply Am public key
		return rsa.encrypt(intermediateStep,amPublicKey)
	
	@staticmethod
	def decryptMessageFromAm(amId,inputString):
		return EncryptionEngine.__applyEncryption(amId,inputString) 
			
	@staticmethod
	def encryptMessageToAm(amId,inputString):
		return EncryptionEngine.__applyEncryption(amId,inputString)

print EncryptionEngine.encryptMessageToAm(1,"hola") 
