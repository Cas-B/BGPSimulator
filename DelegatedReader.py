import os

"""
Class for reading in the AS relationships.
The relationships retrieved from CAIDA are the economical relationships between two AS's,
divided into p2p, c2p and p2c relationships. Their meaning depends on the order of the AS
in the relationships file.

Class variables:
	(a) relationsFileLocation: string - The location of CAIDA's AS relationship file.
"""
class DelegatedReader:

	def __init__(self, delegatedFilesLocation):
		self.delegatedFilesLocation = delegatedFilesLocation
		self.allocatedASNs = dict()

	"""
	Parses information from every delegated summary from the RIRs.
	"""
	def parse(self):
		delegatedFilenames = os.listdir(self.delegatedFilesLocation)

		for filename in delegatedFilenames:
			with open(os.path.join(self.delegatedFilesLocation, filename), "r") as infile:
				for line in infile:
					line = line.strip("\n")
					
					if "#" in line or "*" in line:
						continue

					ASNList = self.parseASN(line)

					if ASNList is not None:
						for asn in ASNList:
							self.allocatedASNs[asn] = 1

	"""
	Parses an AS information line from the RIR AS data.

	Input argument:
		(a) line: string - Line of AS information data.
	"""
	def parseASN(self, line):
		lineSplits = line.split("|")

		"Check if line contains ASN information"
		if len(lineSplits) < 7:
			return None

		if lineSplits[2] == "asn" and (lineSplits[6] == "allocated" or lineSplits[6] == "assigned"):
			return [str(x) for x in range(int(lineSplits[3]), int(lineSplits[3]) + int(lineSplits[4]))]
	
	"Getters"	
	def getAllocatedASNs(self):
		return self.asns
