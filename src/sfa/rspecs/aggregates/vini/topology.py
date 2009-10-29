#!/usr/bin/python

# $Id: topology.py 14181 2009-07-01 19:46:07Z acb $
# $URL: https://svn.planet-lab.org/svn/NodeManager-topo/trunk/topology.py $

#
# Links in the physical topology, gleaned from looking at the Internet2
# and NLR topology maps.  Link (a, b) connects sites with IDs a and b.
#
PhysicalLinks = [(2, 12),  # I2 Princeton - New York 
         (4, 5),   # NLR Chicago - Houston
         (4, 6),   # NLR Chicago - Atlanta
         (4, 7),   # NLR Chicago - Seattle
         (4, 9),   # NLR Chicago - New York
         (4, 10),  # NLR Chicago - Wash DC
         (5, 6),   # NLR Houston - Atlanta
         (5, 8),   # NLR Houston - Los Angeles
         (6, 10),  # NLR Atlanta - Wash DC
         (6, 14),  # NLR Atlanta - Ga Tech
         (7, 8),   # NLR Seattle - Los Angeles
         (9, 10),  # NLR New York - Wash DC
         (11, 13), # I2 Chicago - Wash DC
         (11, 15), # I2 Chicago - Atlanta
         (11, 16), # I2 Chicago - CESNET
         (11, 17), # I2 Chicago - Kansas City
         (12, 13), # I2 New York - Wash DC
         (13, 15), # I2 Wash DC - Atlanta
         (14, 15), # Ga Tech - I2 Atlanta
         (15, 19), # I2 Atlanta - Houston
         (17, 19), # I2 Kansas City - Houston
         (17, 22), # I2 Kansas City - Salt Lake City
         (17, 24), # I2 Kansas City - UMKC
         (19, 20), # I2 Houston - Los Angeles
         (20, 21), # I2 Los Angeles - Seattle
         (20, 22), # I2 Los Angeles - Salt Lake City
         (21, 22)] # I2 Seattle - Salt Lake City


