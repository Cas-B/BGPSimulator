import heapq


def makeCopy(originalList):
    if originalList is None:
        return None

    newList = []

    for path in originalList:
        newList.append(path)

    return newList


def makeSmartCopy(originalList, maxItems):
    if originalList is None:
        return None

    newList = []

    for index in range(min(maxItems, len(originalList))):
        newList.append(originalList[index])

    return newList


"""
Class for BGP nodes.
A BGP node represents an autonomous system (AS) and is identified by its
AS number (ASN).  A BGP node can make use of an export-/import policy
and local preferences in order to route traffic. It supports valley-free
routing and keeps track of the economical relationship it has with its
neighbours.

Class variables:
    (a) ASN: integer - It is the autonomous system number.
    (b) isDetector: boolean - It states whether this ASN is connected
                              to a route collector or not.
    (c) exportPolicy: dictionary - The export policy defined for
                                   outbound traffic.
    (d) importPolicy: dictionary - The import policy defind for
                                   inbound traffic.
    (e) neighbours: dictionary - Tuples, ordered by ASN of the neighbours,
                                 indicating the economical relationships
                                 (c2p,p2p,p2c) and local preference for the
                                 neighbour.
    """
class BGPNode:

    """
    Constructor for object of class BGPNode.
    Creates the class variables from the given arguments.
    """
    def __init__(self, ASN, exportPolicy, importPolicy, neighbours):
        "Initialise class variables"
        self.ID = ASN
        self.exportPolicy = exportPolicy
        self.importPolicy = importPolicy
        self.neighbours = neighbours

        self.connectedToRouteCollector = False
        self.routesUsingValleyFree = False
        self.groupedNeighbours = None

        "Initialise Routing Information Base (RIB)"
        "Path: Array - [path, local preference, pathlength, ASN source]"
        self.adjRIBIn = []
        self.backupAdjRIBIn = []

        self.locRIB = None
        self.backupLocRIB = None

        "Initialise groupedNeighbours for faster outbound traffic"
        self.groupNeighbours()

    """
    Groups the neighbours, according to outbound traffic policy.

    Two groups are taken into account, either send traffic to all
    neighbours or send traffic to my customers only.
    """
    def groupNeighbours(self):
        "'0': C2P, '1': P2P, '2': P2C, '3': Everything"
        self.groupedNeighbours = {0: [], 1: [], 2: [], 3: []}

        for asn in self.neighbours:
            self.groupedNeighbours[3].append(asn)

            if self.neighbours[asn][0] == 2:
                self.groupedNeighbours[2].append(asn)

    """
    Resets the BGP node's entire RIB and backup.
    """
    def reset(self):
        self.adjRIBIn = []
        self.backupAdjRIBIn = []

        self.locRIB = None
        self.backupLocRIB = None

    """
    Resets the BGP node's Adj-RIB-In and Loc-RIB from the backup.
    """
    def resetFromBackup(self):
        self.adjRIBIn = makeCopy(self.backupAdjRIBIn)
        self.locRIB = makeCopy(self.backupLocRIB)

    """
    Indicates whether the BGP node is receiving valid BGP messages
    or BGP messages belonging to a hijack.

    When switching to BGP messages belonging to a hijack, the current
    Adj-RIB-In, only the 10 best routes, and Loc-RIB is stored.
    When switching back to valid BGP messages, the stored Adj-RIB-In
    and Loc-RIB are put back and those of the hijack are erased.

    Input argument:
        (a) continueWithHijack: boolean - Indicating whether the next
                                          messages will be part of a
                                          hijack or not.
    """
    def setRIB(self, continueWithHijack):
        if continueWithHijack:
            self.backupAdjRIBIn = makeSmartCopy(self.adjRIBIn, 10)
            self.backupLocRIB = makeCopy(self.locRIB)
        else:
            self.adjRIBIn = makeCopy(self.backupAdjRIBIn)
            self.backupAdjRIBIn = []

            self.locRIB = makeCopy(self.backupLocRIB)
            self.backupLocRIB = None

    """
    Sets whether this BGP node routes outbound traffic, according to
    the valley-free principle.

    Input argument:
        (a) usesValleyFree: boolean - Indicating whether the valley-free
                                      principle is used or not.
    """
    def setTrafficPrinciple(self, usesValleyFree):
        self.routesUsingValleyFree = usesValleyFree

    """
    Sets whether this BGP node is a detector node or not.

    Input argument:
        (a) isDetector: boolean - Indicating whether the node is a
                                  detector or not.
    """
    def setDetector(self, isDetector):
        self.connectedToRouteCollector = isDetector

    """
    Detects whether the BGP node already appeared in a list of ASNs.

    Input argument:
        (a) parts: array - AS path.
    """
    def isLoop(self, parts):
        if self.ID in parts:
            return True
        return False

    """
    Sets a path in the BGP node's Loc-RIB.

    Input argument:
        (a) path: string - AS path.
        (b) routeParts: array - AS path.
    """
    def setSelectedPath(self, path, routeParts):
        self.locRIB = [path, self.neighbours[routeParts[-1]][1], len(routeParts), int(routeParts[-1])]

    """
    Removes all routes received from 'ASN' from the Adj-RIB-In.

    Every ASN should only be able to put one route in another BGP node's
    Adj-RIB-In, thus the search function looks for a single route.

    Input argument:
        (a) path: string - The source ASN of the path to be removed.
    """
    def removeOldPath(self, ASN):
        indexFound = -1

        for index in range(len(self.adjRIBIn)):
            if int(ASN) == int(self.adjRIBIn[index][2]):
                indexFound = index

        if indexFound != -1:
            del self.adjRIBIn[indexFound]

    """
    Selects the best route from all routes in the Adj-RIB-In.

    When the selected route does not come from the same ASN as the new
    route comes from, this path is added to the Adj-RIB-In.
    The new route 'path' is add to the Adj-RIB-In, the best route is
    selected among those in the Adj-Rib-In and the best route is removed
    from the Adj-RIB-In.

    Input argument:
        (a) path: string - AS path.
        (b) parts: array - AS path.
    """
    def selectBestRoute(self, path, parts):
        if int(parts[-1]) != self.locRIB[3]:
            heapq.heappush(self.adjRIBIn, (-self.locRIB[1], self.locRIB[2], int(self.locRIB[3]), self.locRIB[0]))

        bestPath = heapq.heappushpop(self.adjRIBIn, (-self.neighbours[parts[-1]][1], len(parts), int(parts[-1]), path))
        return [bestPath[3], -bestPath[0], bestPath[1], bestPath[2]]

    """
    Updates the selected path.

    When the path does not contain the BGP node's own identifier and is
    the best path from all paths in the Adj-RIB-In, it is the new selected path.

    Input argument:
        (a) path: string - Received AS path.
    """
    def updateSelectedPath(self, path):
        parts = path.split(",")

        "Loop prevention"
        if self.isLoop(parts):
            return False

        "Default acceptance of the first route the BGP node receives"
        if self.locRIB is None:
            self.setSelectedPath(path, parts)
            return True

        "Choosing new best route, removing old routes from the sending ASN still in the Adj-RIB-In"
        self.removeOldPath(parts[-1])
        bestPath = self.selectBestRoute(path, parts)

        self.locRIB = bestPath
        return True

    """
    Returns a tuple representing the selected path from the Loc-RIB completed
    by adding the BGP node's own ASN and all neighbours this path should be shared with.
    """
    def preparePublishRequest(self):
        if self.locRIB is None:
            return self.preparePublishOrigin()
        return self.preparePublishTransit()

    """
    Returns a tuple with the BGP node's identifier as the selected path and all neighbours to share it with.
    """
    def preparePublishOrigin(self):
        return (self.ID, self.groupedNeighbours[3])

    """
    Returns a tuple with the selected route from the Loc-RIB, including the BGP node's
    own ASN, and the selected group of neighbours, according to the valley-free rule.
    """
    def preparePublishTransit(self):
        route = self.locRIB[0] + "," + self.ID

        "Use export policy when defined"
        if self.exportPolicy is not None and self.locRIB[3] in self.exportPolicy:
            return(route, self.exportPolicy[self.locRIB[3]])

        "Share with all neighbours"
        if not self.routesUsingValleyFree:
            return (route, self.groupedNeighbours[3])

        "Use the valley-free principle"
        if self.neighbours[str(self.locRIB[3])][0] == 2:
            return (route, self.groupedNeighbours[3])

        return (route, self.groupedNeighbours[2])

    "Getters"
    def getSelectedRoute(self):
        if self.locRIB is None:
            return None
        return self.locRIB[0]

    def getSelectedRoutePreference(self):
        if self.locRIB is None:
            return None
        return self.locRIB[1]

    def getSelectedRouteLength(self):
        if self.locRIB is None:
            return None
        return self.locRIB[2]

    def getSelectedRouteSource(self):
        if self.locRIB is None:
            return None
        return self.locRIB[3]

    def getAlternativeRoutes(self):
        return self.adjRIBIn

    def isDetector(self):
        return self.connectedToRouteCollector
