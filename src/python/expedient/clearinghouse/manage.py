#!/usr/bin/env python
from os.path import dirname, join
import sys
sys.path.append(join(dirname(__file__), "../.."))

from django.core.management import execute_manager
import expedient.clearinghouse.settings as settings

def main():
    execute_manager(settings)

if __name__ == "__main__":
    main()
