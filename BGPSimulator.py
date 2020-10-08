from collections import deque
from GraphGenerator import GraphGenerator

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


"""
Class for simulating a BGP process.

A graph instance is created that can be used to simulate the spreading of BGP messages.

Input arguments:
	(a) locationRelations: string - Location of the CAIDA relationships on this machine.
	(b) locationDelegatedFiles: string - Location of the RIR delegated files on this machine.
"""
class BGPSimulator:

	"""
	Constructor for object of class BGPSimulator.
	Creates the class variable 'graph' from the given arguments.
	"""
	def __init__(self, locationRelations, locationDelegatedFiles):
		graph_generator = GraphGenerator(locationRelations, locationDelegatedFiles)
		graph_generator.constructGraph()
		self.graph = graph_generator.getGraph()

		self.caughtByDector = dict()
		self.isInHijackMode = False
		self.queue = deque()
		self.usedBGPNodes = dict()

	"""
	Resets the graph to the instance at time of initialisation.

	If the simulator is in hijack mode, the BGPNodes are reset from their backup to
	allow for a new hijack simulation. For a full reset, first put the simulator out 
	of hijack mode.
	"""
	def reset(self):
		if self.isInHijackMode:
			for BGPNodeNumber in self.usedBGPNodes:
				self.graph[BGPNodeNumber].resetFromBackup()
		else:
			for BGPNodeNumber in self.usedBGPNodes:
				self.graph[BGPNodeNumber].reset()

		self.caughtByDector.clear()
		self.queue = deque()
		self.usedBGPNodes.clear()

	"""
	Sets all nodes in the graph to use the Valley-Free principle or not.

	Input argument:
		(a) useValleyFree: boolean - Indication whether the Valley-Free principle is used or not.
	"""
	def setValleyFree(self, useValleyFree):
		for bgpnode in self.graph:
			bgpnode.setTrafficPrinciple(useValleyFree)

	"""
	Sets all nodes in the graph to use receive hijack messages.

	Input argument:
		(a) continueWithHijack: boolean - Indication whether hijack messages are sent.
	"""
	def setToHijack(self, continueWithHijack):
		self.isInHijackMode = True

		for bgpnode in self.graph:
			bgpnode.setRIB(continueWithHijack)

	"""
	Simulates the BGP communication process after a message has been passed to the protocol.

	It is your own responsibility to reset the graph before running a new simulation.
	"""
	def simulate(self, sourceASN):
		"Setup"
		self.usedBGPNodes[sourceASN] = 1
		self.addQueItemsFromASN(sourceASN)

		"Run simulation"
		while 0 != len(self.queue):
			"Message passing"
			asn, path = self.queue.popleft()

			self.needsToBeReset[asn] = 1
			isUpdated = self.graph[asn].updateSelectedPath(path)
			
			if isUpdated:
				self.addQueItemsFromASN(asn)

			"Hijack detection"
			if self.graph[asn].isDetector():
				self.caughtByDector[asn] = 1
				break

	def addQueItemsFromASN(self, asn):
		publishRequest = self.graph[asn].preparePublishRequest() 

		for neighbour in publishRequest[1]:
			self.queue.append((neighbour, publishRequest[0]))

	def isCaught(self):
		if len(self.caughtByDector) > 0:
			return True
		return False

	"Getters"
	def getUsedBGPNodes(self):
		return self.usedBGPNodes

	def getSelectedPaths(self):
		return { asn:self.graph[asn].getSelectedRoute() for asn in self.usedBGPNodes }

	def getAlternativePaths(self):
		return { asn:self.graph[asn].getAlternativeRoutes() for asn in self.usedBGPNodes }
