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
# FancyCron Client Module web Service, for remote processes ececutipn.

# Required Modules
#------------------------------------------------------------------------------------------------
import os
import pwd
import time
import logging
import datetime
import xmlrpclib
import subprocess
from shutil import move
from xml.dom import minidom
from tempfile import mkstemp
from os import remove, close
from FancyCronParser import  FancyCronParser

# Global variables initialisation
#------------------------------------------------------------------------------------------------
#client_path = '/fancycron/trunk/client-linux'
client_path = '/home/papi/dev/fancycron/trunk/client-linux'
#client_path = os.environ['FANCYCLIENT_PATH']
#client_rpc_log_file = client_path + '/log/client_rpc.log'

# Logs configuration
#------------------------------------------------------------------------------------------------
logger = logging.getLogger('FancyClient.FancyClientRPCService')

# Static functions declaration
#------------------------------------------------------------------------------------------------
def FancyCronAlter(mode, user_file, pattern, subst):
    logger.info('Altering crontab entries in %s' %user_file)
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'wr')
    old_file = open(user_file, 'r')
    logger.debug('File onpened successfully for reading %s' %user_file)
    for line in old_file:
        if pattern in line:
            if mode == 0:
                logger.debug("Desactivating job")
                new_file.write("#" + line)
            elif mode == 1:
                logger.debug("Activating job")
                new_file.write(line.strip("#"))
            elif mode == 2:
                logger.debug("Modifying job parameters, new crontab entry : %s" %subst)
                if line[0] == "#":
                    subst = "#" + subst
                new_file.write(subst)

        else:
            new_file.write(line)
    new_file.close()
    close(fh)
    old_file.close()
    remove(user_file)
    move(abs_path, user_file)

def FancyCronEntryLookup(user_file, pattern):
    logger.info('Getting a crontab entry from : %s', user_file)
    mem_file = open(user_file, "r")
    for line in mem_file:
        if pattern in line:
            mem_file.close()
            logger.debug('Line matching the pattern : %s' %line)
            return line
    mem_file.close()
    logger.debug("No crontab entry found matching the pattern : %s" % pattern)
    return None

def process_created(job, runner, old_param = None):
    logger.info('Creating a new crontab for user %s : ' %str(job['user']))
    process_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    crontab_line = None
    shifted = False
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
    logger.debug('end of crontab backup, user : %s, error : %s', job["user"], err or "No backup error")
    pattern = runner + " " + str(job["id"]) + " "
    line = FancyCronEntryLookup(backup_user_cron_file, pattern)
    if line:
        crontab_line = line[(line.index(pattern) + len(pattern)):]
        return (True, out, process_time, crontab_line)
    
    # cron create job
    if old_param and old_param['shift']:
        cmd = "echo '" + str(job["schedule"]["minute"]) + " " + str(job["schedule"]["hour"]) + \
            " " + str(job["schedule"]["dom"]) + " " + str(job["schedule"]["month"]) + " " + str(job["schedule"]["dow"]) + \
            " " + runner + " " + str(job["id"]) + " " + '"' + str(job["command"]) + " " + str(job["command_param"]) + '"' + \
            ' "' + old_param['shift'] + '"' + "'" + " >> " + backup_user_cron_file
        shifted = True
    else:
        cmd = "echo '" + str(job["schedule"]["minute"]) + " " + str(job["schedule"]["hour"]) + \
            " " + str(job["schedule"]["dom"]) + " " + str(job["schedule"]["month"]) + " " + str(job["schedule"]["dow"]) + \
            " " + runner + " " + str(job["id"]) + " " + '"' + str(job["command"]) + " " + str(job["command_param"]) + '"' + "'" + \
            " >> " + backup_user_cron_file
    
    logger.debug("cmd: %s" % cmd)
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stderr=subprocess.PIPE,
                            )
    proc.wait()
    logger.debug('end of cronjob, user : %s, error : %s', job["user"], proc.stderr.read() or "No cronjob error")

    # cron edit(planify) job
    cmd = "crontab -u " + str(job["user"]) + " " + backup_user_cron_file
    logger.debug("Editing user crontab with command : %s" %cmd)
    os.chmod(backup_user_cron_file, 0644)
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                            )
    proc.wait()
    out = proc.stdout.read()
    err = proc.stderr.read()
    logger.debug('end of crontab generation,, user : %s, error : %s', job["user"], err)
    pattern =  runner + " " + str(job["id"]) + " "
    line = FancyCronEntryLookup(backup_user_cron_file, pattern)
    if line:
        crontab_line = line[(line.index(pattern) + len(pattern)):]
    else:
        crontab_line = None
    os.unlink(backup_user_cron_file)
    return ((err and (False, err, process_time, crontab_line, None)) or (True, out, process_time, crontab_line, old_param['shift']))

def process_modified(job, runner, old_param = None):
    logger.info('Modifying a crontab entry for user %s : ' %str(job['user']))
    shifted = False
    if old_param and  old_param['user']:
        new_job = job.copy()
        job["user"] = old_param["user"]
        result = process_deleted(job, runner)
       # if result[0]:
        #    print "\n\n yes we deleted!!!!"
        #else:
          #  print "\n\n no we didn't deleted!!!!"
        result = process_created(new_job, runner, old_param)
        return (result)
    process_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
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
    logger.debug('end of crontab backup, user : %s, error : %s', job["user"], err or "No backup error")

    # cron create job
    if old_param and old_param['shift']:
        logger.debug('yes shifting ', type(old_param['shift']), " ", old_param['shift'])
        cmd = str(job["schedule"]["minute"]) + " " + str(job["schedule"]["hour"]) + " " + \
            str(job["schedule"]["dom"]) + " " + str(job["schedule"]["month"]) + " " + str(job["schedule"]["dow"]) + \
            " " + runner + " " + str(job["id"]) + " " + '"' + str(job["command"]) + " " + str(job["command_param"]) + '"' \
            ' "' + old_param['shift'] + '"'
        shifted =  True
    else:
        logger.debug('no shifting ')
        cmd = str(job["schedule"]["minute"]) + " " + str(job["schedule"]["hour"]) + " " + \
            str(job["schedule"]["dom"]) + " " + str(job["schedule"]["month"]) + " " + str(job["schedule"]["dow"]) + \
            " " + runner + " " + str(job["id"]) + " " + '"' + str(job["command"]) + " " + str(job["command_param"]) + '"'
    FancyCronAlter(2, backup_user_cron_file, runner + " " + str(job["id"]), cmd + "\n")

    # cron edit job
    cmd = "crontab -u " + str(job["user"]) + " " + backup_user_cron_file
    logger.debug("Editing user crontab with command : %s " %cmd)
    os.chmod(backup_user_cron_file, 0644)
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                            )
    proc.wait()
    out = proc.stdout.read()
    err = proc.stderr.read()
    logger.debug('end of crontab modification,, user : %s, error : %s', job["user"], err)
    pattern =  runner + " " + str(job["id"]) + " "
    line = FancyCronEntryLookup(backup_user_cron_file, pattern)
    if line:
        crontab_line = line[(line.index(pattern) + len(pattern)):]
    else:
        crontab_line = None
    os.unlink(backup_user_cron_file)
    return ((err and (False, err, process_time, crontab_line, None)) or (True, out, process_time, crontab_line, old_param['shift']))

def process_desactivated(job, runner, old_param = None):
    logger.info('Desactivating a crontab entry for user %s : ' %str(job['user']))
    process_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
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
    logger.debug('end of crontab backup, user : %s, error : %s', job["user"], err or "No backup error")

    # cron edit job
    cmd = "crontab -u " + str(job["user"]) + " " + backup_user_cron_file
    logger.debug("Editing user crontab with command : %s" % cmd)
    FancyCronAlter(0, backup_user_cron_file, runner + " " + str(job["id"]), "")
    os.chmod(backup_user_cron_file, 0644) 
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                            )
    proc.wait()
    out = proc.stdout.read()
    err = proc.stderr.read()
    logger.debug('end of crontab desactivation, user : %s, error : %s', job["user"], err)
    os.unlink(backup_user_cron_file)
    return ((err and (False, err, process_time)) or (True, out, process_time))

def process_activated(job, runner, old_param = None):
    logger.info('Activating a crontab entry for user %s : ' %str(job['user']))
    process_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
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
    logger.debug('end of crontab backup, user : %s, error : %s', job["user"], err or "No backup error")

    # cron edit job
    cmd = "crontab -u " + str(job["user"]) + " " + backup_user_cron_file
    logger.debug("Editing user crotab with command : %s" % cmd)
    FancyCronAlter(1, backup_user_cron_file, runner + " " + str(job["id"]), "")
    os.chmod(backup_user_cron_file, 0644) 
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                            )
    proc.wait()
    out = proc.stdout.read()
    err = proc.stderr.read()
    logger.debug('end of crontab activation, user : %s, error : %s', job["user"], err)
    os.unlink(backup_user_cron_file)
    return ((err and (False, err, process_time)) or (True, out, process_time))

def process_deleted(job, runner, old_param = None):
    logger.info('Deleting a crontab entry for user %s : ' %str(job['user']))
    process_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
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
    logger.debug('end of crontab backup, user : %s, error : %s', job["user"], err or "No backup error")

    # cron edit job
    cmd = "crontab -u " + str(job["user"]) + " " + backup_user_cron_file
    logger.debug("Editing user crontab with command : %s" % cmd)
    FancyCronAlter(4, backup_user_cron_file, runner + " " + str(job["id"]), "")
    os.chmod(backup_user_cron_file, 0644) 
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                            )
    proc.wait()
    out = proc.stdout.read()
    err = proc.stderr.read()
    logger.debug('end of crontab deletion, user : %s, error : %s', job["user"], err)
    os.unlink(backup_user_cron_file)
    return ((err and (False, err, process_time)) or (True, out, process_time))

def process_shifted(job, runner, old_param = None):
    logger.info('Shifting job execution for user %s : ' %str(job['user']))
    process_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
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
    logger.debug('end of crontab backup, user : %s, error : %s', job["user"], err or "No backup error")

    # cron edit job
    cmd = "crontab -u " + str(job["user"]) + " " + backup_user_cron_file
    logger.debug("cmd: %s" % cmd)
    FancyCronAlter(3, backup_user_cron_file, runner + " " + str(job["id"]), "")
    os.chmod(backup_user_cron_file, 0644) 
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                            )
    proc.wait()
    out = proc.stdout.read()
    err = proc.stderr.read()
    logger.debug('end of crontab deletion, user : %s, error : %s', job["user"], err)
    os.unlink(backup_user_cron_file)
    return ((err and (False, err, process_time)) or (True, out, process_time))

# Module Classes declaration
#------------------------------------------------------------------------------------------------
class FancyClientRPCService(object):
    "Class for handling Fancy Client RPC services!!!"
    
    def __init__(self, client_ip, rpc_server, runner, host_name):
        self.__logger = logging.getLogger('FancyClient.FancyClientRPCService')
        self.__rpc_service = xmlrpclib.ServerProxy(rpc_server, allow_none=True)
        self.__runner = runner
        self.__client_ip = client_ip
        self.__client_host_name = host_name 
        self.__rpc_service_up = True
        self._func_map = {"CREATED" : process_created,
                          "MODIFIED" : process_modified,
                          "DESACTIVATED" : process_desactivated,
                          "ACTIVATED" : process_activated,
                          "DELETED" : process_deleted,
                          "SHIFTED" : process_shifted,
                          }

    def retrieveJobList(self):
        self.__logger.debug('Retrieving job list from server with ip : %s' %self.__client_ip)
        return (self.__rpc_service.getJobList(self.__client_ip))

    def getJob(self, job_id, command, user):
        self.__logger.info("Trying to get crontab information for a job without id")
        job =  {"schedule":{}}
        backup_user_cron_file = "/tmp/fancycron.tmp"
        backup_user_cron_cmd = "crontab -u " + user + " -l"
	proc = subprocess.Popen(backup_user_cron_cmd,
				shell=True,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				)
	proc.wait()
	err = proc.stderr.read()
	out = proc.stdout.read()
	if out:
		f = open(backup_user_cron_file, "wr", 0644)
		f.write(out)
		f.close()
                pattern =  self.__runner + " " + str(job_id) + " " + command
                line = FancyCronEntryLookup(backup_user_cron_file, pattern)
                if not line:
                    real_command ='"' + command + '"'
                    pattern =  self.__runner + " " + str(job_id) + " " + real_command
                    line = FancyCronEntryLookup(backup_user_cron_file, pattern)
                if line:
                    try:
                        self.__logger.debug(command)
                        entry = FancyCronParser(line)
                        job['id'] = job_id
                        job['user'] = user
                        job['host_ip'] = self.__client_ip
                        job['host_name'] = self.__client_host_name
                        job['command'] = command
                        job['command_param'] = ""
                        job['name'] = command
                        job['schedule']['minute'] = ','.join([str(elem) for elem in entry.fields['minute']])
                        job['schedule']['hour'] = ','.join([str(elem) for elem in entry.fields['hour']])
                        job['schedule']['dom'] = ','.join([str(elem) for elem in entry.fields['day']])
                        job['schedule']['month'] = ','.join([str(elem) for elem in entry.fields['month']])
                        job['schedule']['dow'] = ','.join([str(elem) for elem in entry.fields['weekday']])
                    except:
                        self.__logger.exception("Got an exception while retrieving job informations in GetJob method, Job id will be set to -1")
                        job['id'] = -1
                os.unlink(backup_user_cron_file)
        else:
            self.__logger.error("Unable to get job information in GetJob method, Job id will be set to -1")
            job['id'] = -1
        return (job)
    
    def setJobStatus(self, mode, history_id, job_id, command, status, output, process_time, user, timeinfo):
       if job_id == 0:
           job = self.getJob(job_id, command, user)
           if job['id'] == -1:
               return (-2)
       else:
           job = {'id': job_id, 'schedule':{}}
       result = self.__rpc_service.setJobStatus(mode, history_id, job, status, output, process_time, user, timeinfo)
       self.__logger.debug("returned from server rpc, to change job status, history : %s, job : %s" %(result[0], result[1]))
       if result[1]:
           job['id'] = result[1]
           job['status'] = "Planified"
           self.__logger.debug("Rready to modify job after change the status")
           self._func_map["MODIFIED"](job, self.__runner)
       return (result[0])

    def processJob(self, job, mode, old_param = None):
        self.__logger.info("Processing job from RPC Service with mode : %s" %mode)
        if job:
           try:
               jobdict = {"schedule":{}}
               job_tag = minidom.parseString(job)
               for name in ("id", "name", "command", "command_param", "user", "status"):
                   try:
                       if job_tag.getElementsByTagName(name)[0].hasChildNodes():
                           jobdict[name] = str((job_tag.getElementsByTagName(name))[0].firstChild.data)
                       else:
                           jobdict[name] = ""
                   except:
                       self.__logger.exception("Got exception while parsing %s node" % name)
                       
               schedule = job_tag.getElementsByTagName("schedule")
               for name in ("minute", "hour", "dom", "month", "dow"):
                   try:
                       if job_tag.getElementsByTagName(name)[0].hasChildNodes():
                           jobdict["schedule"][name] = str((schedule[0].getElementsByTagName(name))[0].firstChild.data)
                       else:
                           jobdict["schedule"][name] = ""
                   except:
                       self.__logger.exception("Got exception while parsing %s node" % name)
               return (self._func_map[mode](jobdict, self.__runner, old_param))
           except:
                self.__logger.error('Got exception while getting job_tag and alter crontab')
                
    def bye(self):
        if self.__rpc_service_up:
            self.__logger.debug('Sending RPC Service disconnection notification to server')
            self.__rpc_service.notify("BYE")
            
    def sendCreateResult(self, result, crontab_line):
        if self.__rpc_service_up:
            self.__logger.debug('send crontab creation resultat with entry : %s' %crontab_line)
            self.__rpc_service.setCreateResult(result, crontab_line)
            
    def setRPCService(self, state):
        self.__logger.debug('RPC Service status changed')
        self.__rpc_service_up = state
