#!/usr/bin/python
import os
import sys
from os.path import dirname, join

PYTHON_DIR = os.getcwd()+'/../src/python/'
print PYTHON_DIR

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'vt_manager.settings.settingsLoader'

sys.path.insert(0,PYTHON_DIR)

from vt_manager.models.Ip4Range import Ip4Range
from vt_manager.models.MacRange import MacRange


class UpgradeTools:
	
	@staticmethod
	def rebasePointers():
		print "Rebasing MAC pointers"
		MacRange.rebasePointers()
		print "Rebasing Ip4 pointers"
		Ip4Range.rebasePointers()
	


def main():
	if "rebasePointers" in sys.argv: 
		UpgradeTools.rebasePointers()

if __name__ == "__main__":
	main()	
