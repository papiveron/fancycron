#! /usr/bin/python

# Required Modules
#------------------------------------------------------------------------------------------------
import ast
from UserDict import UserDict

# Global variables initialisation
#------------------------------------------------------------------------------------------------
end_of_packet = '\0'

# Module Classes declaration
#------------------------------------------------------------------------------------------------
class FancyPacket:
	"Class for building fancycron packets"
	def __init__(self, packet_type, data):
		print "contructing packet"
		self.__packet_type = packet_type
		self.__data = data
	def getType(self):
            return (self.__packet_type)
	def getData(self):
            return (self.__data)

class FancyDict(UserDict):
	"Class for building fancycron packets data content"
	def __init__(self, data = {}, **kw):
		UserDict.__init__(self)
		self.update(data)
		self.update(kw)

	def __add__(self, other):
		dict = FancyDict(self.data)
		dict.update(b)
		return dict

def Serialize(packet):
	data = packet.getType() + str(packet.getData()) + end_of_packet
	return data
	#return (packet.getType() + str(packet.getData()) + end_of_packet)
			
def Deserialize(data):
	print data
	#data = "HELLO{'id' : 45}\0"
	data_type =  data.find('{')
	print "index of dict : %d" %data_type
	end = data.find(end_of_packet)
	print "index of end of the packet : %d" %end
	packet = FancyPacket(data[: data_type], ast.literal_eval(data[data_type : data.find(end_of_packet)]))
	#print Serialize(packet)
	return packet
	#return (FancyPacket(data[: data_type], ast.literal_eval(data[data_type : data.find(end_of_packet)])))
	       
