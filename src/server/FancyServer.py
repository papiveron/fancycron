#! /usr/bin/python

# Required Modules
#------------------------------------------------------------------------------------------------
import socket
import os
import sys
import logging
import ConfigParser
sys.path.append( "../commons")
import FancyPacketManager
from FancyServerStorage import FancyServerStorage
from FancyServerEngine import FancyServerEngine

# Global variables initialisation
#------------------------------------------------------------------------------------------------
server_conf_file = os.environ['FANCYCRON_DIR'] + '/conf/server.conf'
server_log_file =  os.environ['FANCYCRON_DIR'] + '/log/server.log'

# Logs configuration
#------------------------------------------------------------------------------------------------
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=server_log_file)

# Reading configuration file
#------------------------------------------------------------------------------------------------
config = ConfigParser.ConfigParser()

try:
    config.read(server_conf_file)
except:
    logging.error('Error reading configuration file : %s', server_conf_file)
    print 'error in server config file'
    sys.exit(2)
try:
    server_port = eval(config.get('network', 'server_port'))
except:
    logging.error('Missing or wrong parameter in the configuration file : %s', server_conf_file)
    print 'error getting server confifiguration'
    sys.exit(2)

# Module Classes declaration
#------------------------------------------------------------------------------------------------
class FancyServer:
    "FancyCron Server Class"
    def __init__(self):
      # self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       # self.__socket.bind(("", server_port))
       # self.host_ip_list = FancyStorage["host_ip_list"]
        ip_list = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]
        if ip_list : self.__ip = ip_list[0]
	else : self.__ip = None
	self.__port = server_port

    def getSocket(self):
        return self.__socket

    def getIpPort(self):
        return (self.__ip, self.__port)

    def sendData(packet, host):
        self.__socket.sendto(packet, hostt_ip_list)
    
    def start(self):
        storage = FancyServerStorage()
        engine = FancyServerEngine(("", self.__port), storage=storage)
        engine.serve_forever()

  #  def processData(packet, host):
        #call a function pointer corresponding to the packet type, and send back the answer to the corresponding client


# Starting Module process
#------------------------------------------------------------------------------------------------
server = FancyServer()
server.start()
