#!/usr/bin/env python
from os.path import dirname, join
import sys
sys.path.append(join(dirname(__file__), ".."))

from django.core.management import execute_manager
#import vt_manager.settings as settings
import vt_manager.settings.settingsLoader as settingsLoader


def main():
    execute_manager(settingsLoader)

if __name__ == "__main__":
    execute_manager(settingsLoader)
