#!/usr/bin/python

from foam.sfa.rspecs.pg_rspec_converter import PGRSpecConverter
from foam.sfa.rspecs.sfa_rspec_converter import SfaRSpecConverter
from foam.sfa.rspecs.rspec import RSpec
from foam.sfa.rspecs.version_manager import VersionManager

class RSpecConverter:

    @staticmethod
    def to_sfa_rspec(in_rspec, content_type=None):
        rspec = RSpec(in_rspec)
        version_manager = VersionManager()
        sfa_version = version_manager._get_version('sfa', '1')
        pg_version = version_manager._get_version('protogeni', '2')
        if rspec.version.type.lower() == sfa_version.type.lower(): 
          return in_rspec
        elif rspec.version.type.lower() == pg_version.type.lower(): 
            return PGRSpecConverter.to_sfa_rspec(in_rspec, content_type)
        else:
            return in_rspec 

    @staticmethod 
    def to_pg_rspec(in_rspec, content_type=None):
        rspec = RSpec(in_rspec)
        version_manager = VersionManager()
        sfa_version = version_manager._get_version('sfa', '1')
        pg_version = version_manager._get_version('protogeni', '2')

        if rspec.version.type.lower() == pg_version.type.lower(): 
            return in_rspec
        elif rspec.version.type.lower() == sfa_version.type.lower(): 
            return SfaRSpecConverter.to_pg_rspec(in_rspec, content_type)
        else:
            return in_rspec 


if __name__ == '__main__':
    pg_rspec = 'test/protogeni.rspec'
    sfa_rspec = 'test/nodes.rspec'  

    print "converting pg rspec to sfa rspec"
    print RSpecConverter.to_sfa_rspec(pg_rspec)
    
    print "converting sfa rspec to pg rspec"
    print RSpecConverter.to_pg_rspec(sfa_rspec)                   
