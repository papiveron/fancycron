#! /usr/bin/python
# -*- coding: iso-8859-1 -*
#
# @see http://eip.epitech.eu/2013/ultimaade/                                                                                                                                      
# @author 2012 Eugène Ngontang <ngonta_e@epitech.com> 
# @see The GNU Public License (GPL) 
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02110-1301, USA.
#
# FancyCron client module, entry point of all the client process of FanyCron client module

# Required Modules
#------------------------------------------------------------------------------------------------
import os
import sys
import time
import socket
import logging
import asyncore
import ConfigParser
from FancyClientEngine import FancyClientEngine
from FancyClientRPCService import FancyClientRPCService

# Global variables initialisation
#------------------------------------------------------------------------------------------------
#client_path = '/fancycron/trunk/client-linux'
client_path = '/home/papi/dev/fancycron/trunk/client-linux'
#client_path = os.environ['FANCYCLIENT_PATH']
client_conf_file = client_path + '/conf/client.conf'
client_log_file =  client_path + '/log/client_debug.log'

# Logs configuration
#------------------------------------------------------------------------------------------------
logger = logging.getLogger('FancyClient')

logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(client_log_file)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.info('\n\n----------------------------------------------------Start launching FancyCron Client main process at %s--------------------------------------------------' %time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

# Reading configuration file
#------------------------------------------------------------------------------------------------
config = ConfigParser.ConfigParser()

try:
    config.read(client_conf_file)
except:
    logger.exception('Error reading configuration file : %s', client_conf_file)
    sys.exit(2)
try:
    server_port = config.get('network', 'server_port')
    job_runner = config.get('job', 'job_runner')
    server_address = config.get('network', 'server_address')
    engine_port = eval(config.get('network', 'engine_port'))
except:
    logger.exception('Missing or wrong parameter in the configuration file : %s', client_conf_file)
    sys.exit(2)

# Module Classes declaration
#------------------------------------------------------------------------------------------------
class FancyClient:
    "FancyCron client Class"
    def __init__(self):
      # self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       # self.__socket.bind(("", server_port))
       # self.host_ip_list = FancyStorage["host_ip_list"]
        name = socket.gethostname()
        ip_list = [ip for ip in socket.gethostbyname_ex(name)[2] if not ip.startswith("127.")]
        if ip_list : self.__ip = ip_list[0]
    	else : self.__ip = None
        if name : self.__host_name = name
        else: self.__host_name = None
	self.__server_port = server_port
	self.__job_runner = job_runner
        self.__server_address = server_address
        self.__rpc_server =  "http://" + server_address + ":" + server_port + "/xml_rpc_srv"

    def getServerAddress(self):
        return (self.__server_address, self.__server_port)
    
    def start(self):
        client_rpc_service = FancyClientRPCService(self.__ip, self.__rpc_server, job_runner, self.__host_name)
        engine = FancyClientEngine(client_rpc_service, engine_port, self.__job_runner)
        engine.start() 
        
# Starting Module process
#------------------------------------------------------------------------------------------------
client = FancyClient()
client.start()
