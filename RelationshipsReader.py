"""
Class for reading in the AS relationships.
The relationships retrieved from CAIDA are the economical relationships between two AS's,
divided into p2p, c2p and p2c relationships. Their meaning depends on the order of the AS
in the relationships file.

Class variables:
	(a) relationsFileLocation: string - The location of CAIDA's AS relationship file.
"""
class RelationshipsReader:

	def __init__(self, relationsFileLocation):
		self.relationsFileLocation = relationsFileLocation
		self.relationships = dict()

	def parse(self):
		with open(self.relationsFileLocation, "r") as infile:
			for line in infile:
				line = line.strip("\n")

				if "#" in line:
					continue

				self.parsingRelationsLine(line)

	"""
	Parses an AS relationship line from the CAIDA relationship data.

	Input argument:
		(a) line: string - Line of relationship data.
	"""
	def parsingRelationsLine(self, line):
		components = line.split("|")

		"Check if the line follows the format CAIDA described"
		assert len(components) == 4
		assert components[0].isdigit()
		assert components[1].isdigit()
		assert components[2].strip("-").isdigit()

		"Add missing ASNs to the relationships dictionary"
		if components[0] not in self.relationships:
			self.relationships[components[0]] = ([], [], [], [])
		if components[1] not in self.relationships:
			self.relationships[components[1]] = ([], [], [], [])

		"Add economical relations"
		if components[2] == "0":
			self.relationships[components[0]][0].append(components[1])
			self.relationships[components[1]][0].append(components[0])
		elif components[2] == "-1":
			self.relationships[components[0]][2].append(components[1])
			self.relationships[components[1]][1].append(components[0])

	"Getters"
	def getRelationships(self):
		return self.relationships
