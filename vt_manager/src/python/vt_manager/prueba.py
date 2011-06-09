class A:
	@staticmethod
	def __metodo():
		print "hola"
	@staticmethod
	def publico():
		A.__metodo()

class B(A):
	def __init__(self):
		self.A.__init__()

	@staticmethod
	def metodob():
		B.__metodo()
		print "chau"

A.publico()
B.metodob()
