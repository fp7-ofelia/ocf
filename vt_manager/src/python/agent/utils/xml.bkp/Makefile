FLAGS=--namespacedef="http://www.fp7-ofelia.eu/CF/vt_am/rspec"
all:
	generateDS.py $(FLAGS) -o vtRspecInterface.py -s vtRspecInterfaceStub.py schema.xsd 
#	generateDS.py $(FLAGS) -o vtRspecQueryInterface.py -s vtRspecQueryInterfaceStub.py querySchema.xsd 
#	generateDS.py $(FLAGS) -o vtRspecResponseInterface.py -s vtRspecResponseInterfaceStub.py responseSchema.xsd 
silent:
	generateDS.py $(FLAGS) -o vtRspecInterface.py -s vtRspecInterfaceStub.py --silence schema.xsd 
#	generateDS.py $(FLAGS) -o vtRspecQueryInterface.py -s vtRspecQueryInterfaceStub.py --silence querySchema.xsd 
#	generateDS.py $(FLAGS) -o vtRspecResponseInterface.py -s vtRspecResponseInterfaceStub.py --silence responseSchema.xsd

#	generateDS.py $(FLAGS)-o vtRspecInterface.py -s vtRspecInterfaceStub.py --silence schema.xsd 
#	generateDS.py $(FLAGS)-o vtRspecInterface.py -s vtRspecInterfaceStub.py --silence responseSchema.xsd 
