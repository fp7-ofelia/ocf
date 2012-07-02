#!/usr/bin/env python
from os.path import dirname, join
import sys
sys.path.append(join(dirname(__file__), "../.."))
sys.path.append(join(dirname(__file__), "../../../../../expedient/src/python"))


from django.core.management import execute_manager
import openflow.optin_manager.settings as settings


def main():
    execute_manager(settings)

if __name__ == "__main__":
    execute_manager(settings)
