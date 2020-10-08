from BGPNode import BGPNode
from DelegatedReader import DelegatedReader
from DetectorASReader import DetectorASReader
from RelationshipsReader import RelationshipsReader


"""
Class for generating an AS graph.

The construction of a graph, where nodes represent ASes and edges their economical
relationships, consists of three phases:
	1) Parsing AS (economical) relations
		The ASes share an economical relationship, consisting of 'Customer-to-Provider',
		'Peer-to-Peer' or 'Provider-to-Customer' relationships. The information
		containing the relationships between ASes has to be parsed into an usable format.
	2) Filter not-existing ASes
		As the relational information is based on data suspectible for manipulation,
		a check is performed to remove not-existing ASes from the data.
	3) Marking nodes as detectors
		There are ASes connected to route collectors, which are able to collect information
		used for hijack detection. These nodes in the graph should be marked as detectors
		to be used in any detection simulation.
		
Class variables:
	(a) fileLocationRelations: string - The location of CAIDA's AS relationship file.
	(b) locationDelegatedFiles: string - The location to the folder containing the RIR 
										delegated files.
"""
class GraphGenerator:

	def __init__(self, fileLocationRelations, locationDelegatedFiles):
		self.relationsFileLocation = fileLocationRelations
		self.delegatedFilesLocation = locationDelegatedFiles

		self.nodes = dict()
		self.relationships = dict()

	def retrieveASRelations(self):
		rr = RelationshipsReader(self.relationsFileLocation)
		rr.parse()
		return rr.getRelationships()

	def retrieveAllocatedASNs(self):
		dr = DelegatedReader(self.delegatedFilesLocation)
		dr.parse()
		return dr.getAllocatedASNs()

	def retrieveAllDetectors(self):
		dr = DetectorASReader()
		dr.parse()
		return dr.getAllDetectors()

	def constructGraph(self):
		"Stage 1: parsing AS (economical relations)"
		self.relationships = self.retrieveASRelations()

		"Stage 2: filtering not-existing ASes"
		self.filter()

		"Stage 2.5: formatting current relationships"
		self.convert()

		"Stage 2.75: creating nodes"
		self.nodeCreator()

		"Stage 3: mark nodes as detectors"
		self.markDetectors()

	"""
	Filters ASNs not in use from the data.
	"""
	def filter(self):
		allocatedASNs = self.retrieveAllocatedASNs()
		existingRelations = dict()

		for asn in self.relationships:
			if asn in allocatedASNs:
				existingRelations[asn] = ([], [], [], [])

				for relationType in range(len(self.relationships[asn])):
					for neighbourASN in self.relationships[asn][relationType]:
						if neighbourASN in allocatedASNs:
							existingRelations[asn][relationType].append(neighbourASN)

		self.relationships = existingRelations

	"""
	Formats the relation data into an easy-to-use format for the BGPNode class.

	It creates a dictionary for each ASN, which contains tuples with neighbour data,
	ordered by the neighbours' ASN. The default local preference is passed to all
	neighbours, indicating it is not used.
	"""
	def convert(self):
		formattedRelations = dict()
		defaultLocalPreference = 0

		for asn in self.relationships:
			neighbours = dict()

			for relationType in range(len(self.relationships[asn])):
				for neighbourASN in self.relationships[asn][relationType]:
					neighbours[neighbourASN] = (relationType, defaultLocalPreference)

			formattedRelations[asn] = neighbours

		self.relationships = formattedRelations
				
	"""
	Instantiates all nodes.

	Uses the relation data to instantiate all required BGP nodes.
	"""
	def nodeCreator(self):
		for asn in self.relationships:
			self.nodes[asn] = BGPNode(asn, None, None, self.relationships[asn])

	"""
	Marks nodes as detectors.

	If an ASN appears in the list of detectors, this BGPNode is set to be a detector.
	"""
	def markDetectors(self):
		detectorASNs = self.retrieveAllDetectors()

		for asn in self.relationships:
			if asn in detectorASNs:
				self.nodes[asn].setDetector(True)

	"Getters"
	def getGraph(self):
		return self.nodes
