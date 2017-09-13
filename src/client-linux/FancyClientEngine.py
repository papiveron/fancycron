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
# FancyCron Client Module Engine, run the main client process, handle server notifications and job execution status from the job runner


# Required Modules
#------------------------------------------------------------------------------------------------
import os
import time
import socket
import logging
import asyncore
import subprocess
from xml.dom import minidom
from SimpleXMLRPCServer import SimpleXMLRPCServer

# Global variables initialisation
#------------------------------------------------------------------------------------------------
#client_path = '/fancycron/trunk/client-linux'
client_path = '/home/papi/dev/fancycron/trunk/client-linux'
#client_path = os.environ['FANCYCLIENT_PATH']
#client_debug_file =  client_path + '/log/client_debug.log'

# Logs configuration
#------------------------------------------------------------------------------------------------

# Module Classes declaration
#------------------------------------------------------------------------------------------------
class FancyClientEngine():
    "Class for handling http connection and commications!!!"

    def __init__(self, client_rpc_service, engine_port, runner):
        self.__logger = logging.getLogger('FancyClient.FancyClientEngine')
        self._engine = SimpleXMLRPCServer(("0.0.0.0", engine_port), allow_none=True)
        self._rpc_service = client_rpc_service
        self._runner = str(runner)
        self._engine.register_instance(self._rpc_service)
        try:
            self.__logger.debug("retrieving non planified jobs from server")
            self.processJob(self._rpc_service.retrieveJobList())
        except:
            self.__logger.exception("Execption while getting job list")

    def processJob(self, jobs):
        self.__logger.info("enter job procesing with : %s" %str(jobs))
        if jobs:
            try:
                jobdict = {"schedule":{}}
                xmldoc = minidom.parseString(jobs)
                joblist = xmldoc.getElementsByTagName("Job")
                for job in joblist:
		    for name in ("id", "name", "command", "command_param", "user", "status", "shift"):
			try:
                    		if job.getElementsByTagName(name)[0].hasChildNodes():
                    			jobdict[name] = str((job.getElementsByTagName(name))[0].firstChild.data)
				else:
					jobdict[name] = ""
			except:
                            self.__logger.exception("Got an exception while parsing %s node" % name)

                    schedule = job.getElementsByTagName("schedule")
		    for name in ("minute", "hour", "dom", "month", "dow"):
			try:
                    		if job.getElementsByTagName(name)[0].hasChildNodes():
                    			jobdict["schedule"][name] = str((schedule[0].getElementsByTagName(name))[0].firstChild.data)
				else:
					jobdict["schedule"][name] = ""
			except:
                            self.__logger.exception("Got exception when parsing %s node" % name)
	            print jobdict		
                    self.generateCrontab(jobdict)
            except:
                self.loggger.exception('Exception while getting jobs list and generating crontabs')
        else:
            self.__logger.debug("No Job to create!")

    def entryLookup(self, user_file, pattern):
        self.__logger.info('Getting a crontab entry from : %s', user_file)
        mem_file = open(user_file, "r")
        for line in mem_file:
            if pattern in line:
                self.__logger.debug('Line matching the pattern : %s' %line)
                mem_file.close()
                return line
        self.__logger.debug("No crontab entry found matching the pattern : %s" % pattern)
        mem_file.close()
        return None
       
    def generateCrontab(self, job):
        self.__logger.info('Creating a new crontab for user %s : ' %str(job['user']))
        process_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        crontab_line = None
        backup_user_cron_file = "/tmp/fancycron.tmp"
        backup_user_cron_cmd = "crontab -u " + str(job["user"]) + " -l"

	# cron backup
	proc = subprocess.Popen(backup_user_cron_cmd,
				shell=True,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				)
	proc.wait()
        f = open(backup_user_cron_file, "wr")
	err = proc.stderr.read()
	out = proc.stdout.read()
        if out:
            f.write(out)
        f.close()
        self.__logger.debug('end of crontab backup, user : %s, error : %s', job["user"], err or "No backup error")
        
        pattern =  self._runner + " " + str(job["id"]) + " "
        line = self.entryLookup(backup_user_cron_file, pattern)
        if line:
            crontab_line = line[(line.index(pattern) + len(pattern)):]
            self._rpc_service.sendCreateResult((job["id"], "OK", out, process_time), crontab_line)
        else:
            if job['shift']:
                # cron create job
                cmd = "echo '" + str(job["schedule"]["minute"]) + " " + str(job["schedule"]["hour"]) + \
                    " " + str(job["schedule"]["dom"]) + " " + str(job["schedule"]["month"]) + " " + str(job["schedule"]["dow"]) + \
                    " " + self._runner + " " + str(job["id"]) + " " + '"' + str(job["command"]) + " " + str(job["command_param"]) + '"' + \
                    ' "' + job['shift'] + '"' + "'" + " >> " + backup_user_cron_file
            else:
                cmd = "echo '" + str(job["schedule"]["minute"]) + " " + str(job["schedule"]["hour"]) + \
                    " " + str(job["schedule"]["dom"]) + " " + str(job["schedule"]["month"]) + " " + str(job["schedule"]["dow"]) + \
                    " " + self._runner + " " + str(job["id"]) + " " + '"' + str(job["command"]) + " " + str(job["command_param"]) + '"' + "'" + \
                    " >> " + backup_user_cron_file
                
            self.__logger.debug("The crontab line : %s" % cmd)
            proc = subprocess.Popen(cmd,
                                    shell=True,
                                    stderr=subprocess.PIPE,
                                    )
            proc.wait()
            self.__logger.debug('end of cronjob, user : %s, error : %s', job["user"], proc.stderr.read() or "No cronjob error")
            
            # cron edit(planify) job
            cmd = "crontab -u " + str(job["user"]) + " " + backup_user_cron_file
            self.__logger.debug("Editing user crontab with command : %s" % cmd)
            os.chmod(backup_user_cron_file, 0644)
            proc = subprocess.Popen(cmd,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE
                                    )
            proc.wait()
            out = proc.stdout.read()
            err = proc.stderr.read()
            self.__logger.debug('end of crontab generation,, user : %s, error : %s', job["user"], err)
            pattern =  self._runner + " " + str(job["id"]) + " "
            line = self.entryLookup(backup_user_cron_file, pattern)
            if line:
                crontab_line = line[(line.index(pattern) + len(pattern)):]
            else:
                crontab_line = None
            os.unlink(backup_user_cron_file)
            self._rpc_service.sendCreateResult((err and (job["id"], "ERROR", err, process_time)) or
                                               (job["id"], "OK", out, process_time), crontab_line)
                                  

    def start(self):
        try:
            self.__logger.debug('Fancy Client Engine listening...')
            self._engine.serve_forever()
        except KeyboardInterrupt, ex:
            try:
                self._rpc_service.bye()
            except:
                self.__logger.debug('Stopping Fancy Client Engine by user request.')
                
# Starting Module process
#------------------------------------------------------------------------------------------------
