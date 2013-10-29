# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

from sqlalchemy import Table, Column, MetaData
from sqlalchemy import Integer, String
from sqlalchemy import create_engine, select

class FSDB(object):
  def __init__ (self):
    self.engine = create_engine('sqlite:///:memory:', echo=True)
    self.md = MetaData()
    self.tables = []

    self.tables.append(Table('dpports', self.md, 
        Column('dpid', String(23)),
        Column('in_port', String(10))))

    self.tables.append(Table('dlsrc', self.md,
        Column('dl_src', String(23))))

    self.tables.append(Table('dldst', self.md,
        Column('dl_dst', String(23))))

    self.dltype = Table('dltype', self.md,
        Column('dl_type', String(6)))

    self.vlanid = Table('vlanid', self.md,
        Column('dl_vlan', String(6)))

    self.nwsrc = Table('nwsrc', self.md,
        Column('nw_src', String(18)))

    self.nwdst = Table('nwdst', self.md,
        Column('nw_dst', String(18)))

    self.nwproto = Table('nwproto', self.md,
        Column('nw_proto', String(3)))

    self.nwtos = Table('nwtos', self.md,
        Column('nw_tos', String(3)))

    self.tpsrc = Table('tpsrc', self.md,
        Column('tp_src', String(5)))

    self.tpdst = Table('tpdst', self.md,
        Column('tp_dst', String(5)))

