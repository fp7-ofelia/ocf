#!/usr/bin/env python
from os.path import dirname, join
import os
import sys
from django.core.management import execute_manager
import settings

def main():
    execute_manager(settings)

if __name__ == "__main__":
    main()
