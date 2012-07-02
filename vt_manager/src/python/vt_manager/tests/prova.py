

class ClassA():
	puta=None
	@staticmethod
	def printputa():
		print A.puta
class ClassB(ClassA):
	a = ClassA()
	super(ClassA,a).puta="prova"
		
	

ClassB.printputa()
