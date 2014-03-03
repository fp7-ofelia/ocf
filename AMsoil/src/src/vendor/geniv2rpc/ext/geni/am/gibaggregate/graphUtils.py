#----------------------------------------------------------------------
# Copyright (c) 2012 Raytheon BBN Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
#----------------------------------------------------------------------


class GraphNode(object) :
    """ This is the base class for all the objects that correspond to 
        nodes in a graph that correspond to the experimenter specified
        topology.  Examples of these objects include VMNodes (hosts),
        NICs and links.

        This commmon base class allows the functions in the graphUtils
        module to handle all these objects in a uniform manner.
    """
    def getNeighbors(self) :
        pass

    def getNodeName(self) :
        pass


def findShortestPath(startNode, endNode, pathSoFar =[]) :
    """ Find the shortest path between the specified GraphNode objects 
        that form the nodes of a graph.
    """
    # Add this node to the path explored so far
    pathSoFar = pathSoFar + [startNode]

    if startNode == endNode :
        # Found path to the endNode!
        return pathSoFar

    # Path from here to the endNode.  We currently don't have such a path
    pathFromHere =  None

    # See if we can get to the endNode through one of our neighbors
    neighbors = startNode.getNeighbors() 
    for i in range(len(neighbors)) :
        if neighbors[i] not in pathSoFar :
            pathThruNeighbor = findShortestPath(neighbors[i], endNode, \
                                                    pathSoFar)
            if pathThruNeighbor != None :
                if (pathFromHere == None) or (len(pathThruNeighbor) < \
                                                  len(pathFromHere)) :
                    # Found a new or shorter path to the endNode 
                    pathFromHere = pathThruNeighbor

    return pathFromHere
