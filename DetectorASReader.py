import os

"""
Class to read the ASN of all ASes connected to a route collector.
It reads the ASNs from a list obtained from RouteViews, RIPE RIS en PCH. 
BGPMon is excluded as it requires parsing MRT data to obtain a subset of the data.
"""
class DetectorASReader:

	def __init__(self):
		self.storage_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.join("..", "..", "data", "collectors")))

		self.peerASN = dict()
		self.ripePeerASN = dict()
		self.routeviewsPeerASN = dict()
		self.pchPeerASN = dict()

	"""
	Parses the collector file.
	"""
	def parse(self):
		with open(os.path.join(self.storage_path, "collectors.txt"), "r") as infile:
			for line in infile:
				line = line.strip("\n")
				collector_data = line.split("|")
				
				collector_name = collector_data[0].strip()
				collector_peers = collector_data[1].strip().split(" ")
				
				"Store all ASNs"
				self.peerASN[collector_name] = collector_peers

				"Separate the collectors read"
				if "rrc" in collector_name:
					self.ripePeerASN[collector_name] = collector_peers
				elif "pch.net" in collector_name:
					self.pchPeerASN[collector_name] = collector_peers
				else:
					self.routeviewsPeerASN[collector_name] = collector_peers

	"""
	Returns all unique ASNs in a list

	Input argument:
		(a) peers: list - A list of ASNs
	"""
	def getUniqueASN(self, peers):
		unique_peers = dict()

		for collector in peers:
			for peer in peers[collector]:
				unique_peers[peer] = 1

		return unique_peers

	"Getters"
	def getAllDetectors(self):
		return self.getUniqueASN(self.peerASN)

	def getRipeDetectors(self):
		return self.getUniqueASN(self.ripePeerASN)

	def getRouteviewsDetectors(self):
		return self.getUniqueASN(self.routeviewsPeerASN)

	def getPCHDetectors(self):
		return self.getUniqueASN(self.pchPeerASN)
