import ast

class FCPacket:
	def __init__(self, packet_type, data):
		self.__packet_type = packet_type
		self._data = data
                print SERVER_PORT

	def getPacketType(self):
            return (self.__packet_type, 56)


dict1 = {'one':1, 'two':2, 'three': {'three.1': 3.1, 'three.2': 3.2 }}
str1 = str(dict1)

#dict2 = eval(str1)
dict2 = ast.literal_eval(str1)
dict3 = ast.literal_eval('{}')

print  type(str1)

print dict1==dict2
print  str1
print  dict1
print  dict2
print  dict3
