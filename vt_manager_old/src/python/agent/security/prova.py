import M2Crypto as m2c
import textwrap
key = m2c.RSA.load_key('certs/agent.key', lambda prompt: 'mypassword')

# encrypt something:
data = 'testing 123'
encrypted = key.public_encrypt(data, m2c.RSA.pkcs1_padding)
print "Encrypted data:"
print "\n".join(textwrap.wrap(' '.join(['%02x' % ord(b) for b in encrypted ])))

# and now decrypt it:
decrypted = key.private_decrypt(encrypted, m2c.RSA.pkcs1_padding)
print "Decrypted data:"
print decrypted
print data == decrypted
