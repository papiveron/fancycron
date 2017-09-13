# File: userdict-example-1.py
import ast
from UserDict import UserDict

SERVER_PORT = 20042

class FCPacket:
	def __init__(self, packet_type, data):
		self.__packet_type = packet_type
		self.__data = data
                print SERVER_PORT

	def getPacketType(self):
            return (self.__packet_type)
	def getData(self):
            return (self.__data)

class FancyDict(UserDict):
    def __init__(self, data = {}, **kw):
        UserDict.__init__(self)
        self.update(data)
        self.update(kw)

    def __add__(self, other):
        dict = FancyDict(self.data)
        dict.update(b)
        return dict

a = FancyDict(a = 1)
b = FancyDict(b = 2)
dict = {'name' : "my_name", 'class' : "my_class"}
c = FancyDict(dict)

ready = FancyDict({'ipddress' : "172.123.12.2"})

packet = FCPacket(0, ready)

dict1 = {'one':1, 'two':2, 'three': {'three.1': 3.1, 'three.2': 3.2 }}

packet1 = FCPacket("HELO", dict1)
str1 = str(dict1)
str2 = packet1.getPacketType() + ' ' +  str(packet1.getData()) + '\n'
#dict2 = eval(str1)
dict2 = ast.literal_eval(str1)
dict3 = ast.literal_eval(str2[str2.find('{') : str2.find('\n')])

print a + b
print c
print c["name"]
print type(c)
b = c
print b

print packet.getPacketType()
print packet.getData()

print  type(str1)

print dict1==dict2==dict3
print  str1
print  str2
print  str2[len(str2) - 2]
print "-------------- After str1 and str2 ----------------"
print  dict1
print  dict2
print  dict3
