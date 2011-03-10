#!/usr/bin/env python
from os.path import dirname, join
import sys
sys.path.insert(0, join(dirname(__file__), "../.."))

import expedient.clearinghouse.settings as settings
from django.core.management import execute_manager

def main():
    execute_manager(settings)

if __name__ == "__main__":
    main()
