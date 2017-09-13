#! /usr/bin/python

# Required Modules
#------------------------------------------------------------------------------------------------
import os
import socket
import logging
import asyncore
import FancyPacketManager
from FancyServerStorage import FancyServerStorage

# Global variables initialisation
#------------------------------------------------------------------------------------------------
server_debug_file =  os.environ['FANCYCRON_DIR'] + '/log/server_debug.log'


logging.basicConfig(level = logging.DEBUG,
                    format = "%(created)-15s %(msecs)d %(levelname)8s %(thread)d %(name)s %(message)s",
                    filename = server_debug_file)

#log                     = logging.getLogger(__name__)
log                     = logging.getLogger()

BACKLOG                 = 5 #To be set to the right value if necessary, and used
SIZE                    = 1024 #To be ajusted if neccessary


# Static functions declaration
#------------------------------------------------------------------------------------------------
def process_hello(data, server):
    return (FancyPacketManager.Serialize(FancyPacketManager.FancyPacket("READY", FancyPacketManager.FancyDict({'id' : 65}))))

def process_ready(data, server):
    return ""

def process_gettask(data, server):
    tasklist = server.getJobList()
    return (FancyPacketManager.Serialize(FancyPacket("GETTASK", tasklist)))

def process_planified(data, server):
    #Look carefully for what is to be put here, how the engine process will notify taks status changes
    server.notify("PLANIFIED", data)
    return ""

def process_declined(data, server):
    server.notify("DECLINED", data)
    return ""

def process_ok(data, server):
    return ""

def process_started(data, server):
    server.notify("STARTED", data)
    return ""

def process_stopped(data, server):
    server.notify("STOPPED", data)
    return ""

def process_end_ok(data, server):
    server.notify("ENDEDOK", data)
    return ""

def process_end_warn(data, server):
    server.notify("ENDEDWARNING", data)
    return ""

def process_end_error(data, server):
    server.notify("ENDEDERROR", data)
    return ""

def process_running(data, server):
    return ""

def process_bye(data, server):
    return ""

# Module Classes declaration
#------------------------------------------------------------------------------------------------
class FancyClientHandler(asyncore.dispatcher):
    "Class for handling client data!!!"
    def __init__(self, conn_sock, client_address, server = None):
        self._server             = server
        self._client_address     = client_address
        self._writing_buffer     = ""
        self._reading_buffer     = ""
        self._is_writable        = False
        self._func_map = {"HELLO" : process_hello,
                         "READY" : process_ready,
                         "GETTASK" : process_gettask,
                         "PLANIFIED" : process_planified,
                         "DECLINED" : process_declined,
                         "OK" : process_ok,
                         "STARTED" : process_started,
                         "STOPPED" : process_stopped,
                         "ENDEDOK" : process_end_ok,
                         "ENDEDWARNING" : process_end_warn,
                         "ENDERROR" : process_end_error,
                         "RUNNING" : process_running,
                         "BYE" : process_bye
                         }

        asyncore.dispatcher.__init__(self, conn_sock)
        log.debug("created handler; waiting for loop")

    def readable(self):
        return True

    def writable(self):
        return self._is_writable 

    def set_writable(self):
        self._is_writable = True

    def handle_request(self, packet):
        try:
            print packet.getType()
            print packet.getData()["id"]
            self._writing_buffer += self._func_map[packet.getType()](packet.getData(), self._server)
        except:
            log.debug("error processing data, may be unknown packet type deserialization issues")
            self._writing_buffer += ""
            
    def check_reading(self, data = ""):
        self._reading_buffer += data
        end = self._reading_buffer.find(FancyPacketManager.end_of_packet)
        if end >= 0:
            self.handle_request(FancyPacketManager.Deserialize(self._reading_buffer[:(end+ 1)]))
            self._reading_buffer = self._reading_buffer[(end + 1):]
            self.check_reading()

    def handle_read(self):
        print "reading"
        log.debug("handle_read")
        data = self.recv(SIZE)
        log.debug("after recv")
        if data:
            print data.find(FancyPacketManager.end_of_packet), data
            log.debug("got data : " + data)
        else:
            log.debug("got null data")
        self.check_reading(data)
        if self._writing_buffer: self._is_writable = True  # sth to send back now

    def handle_write(self):
        log.debug("handle_write")
        if self._writing_buffer:
            sent = self.send(self._writing_buffer)
            log.debug("sent data")
            self._writing_buffer = self._writing_buffer[sent:]
        else:
            log.debug("nothing to send")
        if len(self._writing_buffer) == 0:
            self._is_writable = False

    # Will this ever get called?  Does loop() call
    # handle_close() if we called close, to start with?
    def handle_close(self):
        log.debug("handle_close")
        log.info("conn_closed: client_address=%s:%s" % \
                     (self._client_address[0],
                      self._client_address[1]))
        self.close()
        #pass

class FancyServerEngine(asyncore.dispatcher):
    "Class for handling client connections!!!"
    _allow_reuse_address         = False
    _request_queue_size          = BACKLOG
    _address_family              = socket.AF_INET
    _socket_type                 = socket.SOCK_STREAM

    def __init__(self, address, storage, handlerClass=FancyClientHandler):
        self._address            = address
        self._handlerClass       = handlerClass
        self._storage            = storage

        asyncore.dispatcher.__init__(self)
        self.create_socket(self._address_family,
                               self._socket_type)

        if self._allow_reuse_address:
            self._set_resue_addr()

        self.server_bind()
        self.server_activate()

    def server_bind(self):
        self.bind(self._address)
        log.debug("bind: address=%s:%s" % (self._address[0], self._address[1]))

    def server_activate(self):
        self.listen(self._request_queue_size)
        log.debug("listen: backlog=%d" % self._request_queue_size)

    def fileno(self):
        return self.socket.fileno()

    def serve_forever(self):
        asyncore.loop()

    #Here, a message has to be sent in the queue, to the storage process
    def notify(self, status, task):
        #fancy_storage_process.update(status, task)
        self._storage.update(status, task)
        print "job state notification : %s" %status
        

    def getJobList():
        return _storage._job_list
    # TODO: try to implement handle_request()

    # Internal use
    def handle_accept(self):
        (conn_sock, client_address) = self.accept()
        if self.verify_request(conn_sock, client_address):
            self.process_request(conn_sock, client_address)

    def verify_request(self, conn_sock, client_address):
        return True

    def process_request(self, conn_sock, client_address):
        log.info("conn_made: client_address=%s:%s" % \
                     (client_address[0],
                      client_address[1]))
        self._handlerClass(conn_sock, client_address, self)

    def handle_close(self):
        self.close()

# Starting Module process
#------------------------------------------------------------------------------------------------
