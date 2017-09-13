#!/opt/csw/bin/python
# -*- coding: iso-8859-1 -*
# vim: set expandtab tabstop=4 shiftwidth=4:
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
# Job runner for FanyCron client module


# Required Modules
#------------------------------------------------------------------------------------------------
import errno
import os
import ast
import sys
import time
import logging
import getpass
import datetime
import xmlrpclib
import subprocess
import ConfigParser
from shutil import move
from xml.dom import minidom
from tempfile import mkstemp
from os import remove, close
from FancyCronParser import  FancyCronParser
from datetime import datetime as str_datetime
from FancyClientStorage import FancyClientStorage

# Global variables initialisation
#----------------------------------------------------------------------------------------------
client_path = '/fancycron/trunk/client-solaris'
#client_path = '/home/veron/projets/fancycron/src/client'
#client_path = '/etc/fancycron/os.environ['FANCYCLIENT_PATH']

client_conf_file = client_path + '/conf/client.conf'
client_job_debug_file =  client_path + '/log/client_job_debug.log'

# Help routines
#------------------------------------------------------------------------------------------------
def usage():
	#print ' FancyJobRunner.py / v1.0 - Eugene NG <engontan@bouyguestelecom.fr>.\n'
	#print ' Running local jobs, and send job state to the job engine process. The program also use a SQLITE databse to store local informations'
	#print ' Usage: FancyJobRunner.py [id] command'
	#print ' Arguments :'
	#print ' id : The id of the job beeing executed, this id is use for database management'
	#print ' command , The command executed by the job'

# Getting the current user
#------------------------------------------------------------------------------------------------
user = getpass.getuser()

# Logs configuration
#------------------------------------------------------------------------------------------------
d = {'user': user}

logger = logging.getLogger('FancyJobRunner')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(client_job_debug_file)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - User : %(user)-8s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.info('\n\n----------------------------------------------------Start launching Job Runner at %s--------------------------------------------------' %time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), extra=d)

# Reading configuration file
#------------------------------------------------------------------------------------------------
config = ConfigParser.ConfigParser()

logger.info('Getting configuration from : %s' %client_conf_file, extra=d)

try:
	config.read(client_conf_file)
except:
	logger.exception('Error reading configuration file : %s' %client_conf_file, extra=d)
	sys.exit(2)
try:
	engine_port = config.get('network', 'engine_port')
	job_runner = config.get('job', 'job_runner')
	db_file = config.get('storage', 'db_file')
	engine_address = config.get('network', 'engine_address')
except:
	logger.exception('Missing or wrong parameter in the configuration file : %s, the engine port and address will be set empty' %client_conf_file, extra=d)
	engine_port, engine_address = "", ""

# Static functions declaration
#------------------------------------------------------------------------------------------------
def FancyCronEntryLookup(user_file, pattern):
	logger.info('Getting a crontab entry from : %s', user_file, extra=d)
	mem_file = open(user_file, "r")
	for line in mem_file:
		if pattern in line:
			mem_file.close()
			logger.debug('Line matching the pattern : %s' %line, extra=d)
			return line
		mem_file.close()
	logger.debug("No crontab entry found matching the pattern : %s" % pattern, extra=d)
	return None

def remove_shift_(user, user_file, entry):
	logger.info('Removing the shift time from crontab entry : %s in %s' %(entry, user_file), extra=d)
	fh, abs_path = mkstemp()
	new_file = open(abs_path,'wr')
	old_file = open(user_file, 'r')
	try:
		for line in old_file:
			if entry in line:
				new_line = line[:line.index(entry)] + entry + "\n"
				new_file.write(new_line)
				logger.debug('Crontab shift time removed, new entry : %s' %new_line, extra=d)
			else:
				new_file.write(line)
		new_file.close()
		close(fh)
		old_file.close()
		remove(user_file)
		move(abs_path, user_file)
		
		cmd = "crontab %s" % (user_file)
		logger.debug("Editing crontab with command : %s" % cmd, extra=d)
		os.chmod(user_file, 0644)
		proc = subprocess.Popen(cmd,
					shell=True,
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE
					)
		proc.wait()
		out = proc.stdout.read()
		err = proc.stderr.read()
		logger.debug('end of crontab shift time removing, error : %s' %err, extra=d)
	except:
		logger.exception('Error while modifying and remove shift time from : %s' %entry, extra=d)
		new_file.close()
		close(fh)
		old_file.close()
		
# Getting arguments
#------------------------------------------------------------------------------------------------
job_id = 0
command = ""
shift_time = None

if len(sys.argv) == 2:
	logger.debug("job running command : " +  sys.argv[1] + " | Usage: FancyTaskRunner.py [id(0 by default)] command [shift_time]", extra=d)
	command = sys.argv[1]
elif len(sys.argv) == 3:
	logger.debug("job id : " + sys.argv[1] + " running command : " +  sys.argv[2] +" |  Usage: FancyTaskRunner.py [id(0 by default)] command [shift_time]", extra=d)
	job_id = eval(sys.argv[1])
	command = sys.argv[2]
elif len(sys.argv) >= 4:
	logger.debug("job id : " + sys.argv[1] + " running command : " +  sys.argv[2] + " with shift time : " + sys.argv[3] + " |  Usage: FancyTaskRunner.py [id(0 by default)] command [shift_time]", extra=d)
	job_id = eval(sys.argv[1])
	command = sys.argv[2]
	shift_time = sys.argv[3]
else:
	logger.error("job with no id running no command |  Usage: FancyTaskRunner.py id(0 by default) command", extra=d)
	sys.exit(2)
	
# Module Classes declaration
#------------------------------------------------------------------------------------------------

# Starting Module process
#------------------------------------------------------------------------------------------------
logger.debug("Entering the job runner")
##print "Entering the job runner"
rpc_service_up = False
if engine_address and engine_port:
	logger.info('Got engine port and address successfuly', extra=d)
	engine = "http://" + engine_address + ":" + engine_port
	rpc_service = xmlrpclib.ServerProxy(engine, allow_none=True)
	rpc_service_up = True

storage = FancyClientStorage(db_file)
started_time = datetime.datetime.now()
str_started_time = str(started_time)

if shift_time:
	logger.info('The job is shifted, getting shift time', extra=d)
	format = "%Y-%m-%d %H:%M:%S"
	execute_time = str_datetime.strptime(shift_time, format)
	real_time = datetime.datetime(started_time.year,
					     started_time.month,
					     started_time.day,
					     started_time.hour,
					     started_time.minute,
					     started_time.second)
	
	if real_time < execute_time:
		logger.debug("job id : " + sys.argv[1] + " can not be executed for this occurence. Job has been shifted, and the shifted time has not been reached yet, the program will exit", extra=d)
		sys.exit(0)
 
logger.debug("It's the time to run the job", extra=d)
t = {"year" : started_time.year,
     "month" : started_time.month,
     "day" : started_time.day,
     "hour" : started_time.hour,
     "minute" : started_time.minute,
     "second" : started_time.second}

#started_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
history_list = ()
remote_id = 0
if storage.is_ready()[0]:
	# backup_user_cron_file = "/tmp/fancycron.tmp"
	fd_backup = tempfile.NamedTemporaryFile(prefix = "fancron_backup.")
	backup_user_cron_file = fd.name

	backup_user_cron_cmd = "crontab -l " + user
	proc = subprocess.Popen(backup_user_cron_cmd,
				shell=True,
				# stdout=subprocess.PIPE,
				stdout = fd_backup,
				stderr=subprocess.PIPE,
				)
	proc.wait()
	err = proc.stderr.read()
	out = proc.stdout.read()
	timeinfo = {
		"next" : None,
		"prev" : None}
	if out:
		f = open(backup_user_cron_file, "wr")
		f.write(out)
		f.close()
		pattern =  job_runner + " " + str(job_id)
		entry = FancyCronEntryLookup(backup_user_cron_file, pattern)
		if entry:
			logger.debug("Crontab entry found for the current user : %s" %entry, extra=d)
		else:
			logger.error("No crontab entry found for the current user, the program will exit", extra=d)
			sys.exit(0)
		try:
			logger.debug("Trying to get previous and next execution time for the running job", extra=d)
			exec_time = datetime.datetime(t["year"],
						      t["month"],
						      t["day"],
						      t["hour"],
						      t["minute"],
						      t["second"])
			crontab_entry = FancyCronParser(entry)
			timeinfo = {"next" : str(crontab_entry.next_run(exec_time)),
				    "prev" : str(crontab_entry.prev_run(exec_time))}
		except:
			logger.debug("Error while getting execution time informations for the running job", extra=d)
			timeinfo = {"next" : None,
				    "prev" : None}
		if shift_time:
			entry = pattern + ' "'  + command + '"'
			remove_shift_(user, backup_user_cron_file, entry)
        try:
			os.unlink(backup_user_cron_file)
        except OSError, (err_no, err_msg):
            if err_no ==  errno.ENOENT:
                pass

	if rpc_service_up:
		try:
			remote_id = rpc_service.setJobStatus(0, remote_id, job_id, command, "RUNNING",
							     "", (str_started_time, None), user, timeinfo)
			if remote_id <= 0:
				history_list = storage.insert((job_id, remote_id, command,
							       "RUNNING", timeinfo["next"], str_started_time,
							       "None", "None", "NO", user, str(timeinfo)))
			else:
				history_list = storage.insert((job_id, remote_id, command,
							       "RUNNING", timeinfo["next"], str_started_time,
							       "None", "None", "YES", user, str(timeinfo)))
			
		except:
			history_list = storage.insert((job_id, remote_id, command,
						       "RUNNING", timeinfo["next"], str_started_time,
						       "None", "None", "NO", user, str(timeinfo)))
			logger.exception("history start status not sent!", extra=d)
	else:
		history_list = storage.insert((job_id, remote_id, command,
					       "RUNNING", timeinfo["next"], str_started_time,
					       "None", "None", "NO", user, str(timeinfo)))
		logger.error("The Engine process was not ready when the job id " +
			      str(job_id) + " executing command " + command + " started!", extra=d)
	storage.close()
else :
	logger.error("The local database was not ready when the job id " +
		     str(job_id) + " executing command " + command + " started!", extra=d)

proc = subprocess.Popen(command,
                        shell=True,
			stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        )
proc.wait()
ended_time = str(datetime.datetime.now())
#ended_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
history_id = 0
##print history_list
if (history_list and history_list[0] and history_list[1]):
	for history in history_list[1]:
		if history[3] == command and  history[6] == str_started_time:
			history_id = history[0]
			break
	if history_id and storage.is_ready()[0] and  storage.connect():
		try:
			out = proc.stdout.read()
			err = proc.stderr.read()
			logger.debug("trying to save ending state out : %s, err : %s", out, err)
			jobhistory_list = storage.set_ended(((err and "ENDEDERROR") or 
							     (out and "ENDEDOK") or
							     "ENDEDWARNING"), ended_time,
							    (err or out), history_id, remote_id)
			logger.debug("history saved!", extra=d)
			if jobhistory_list:
				for jobhistory in jobhistory_list:
					if rpc_service_up and jobhistory[2] != -2:
						try:
							if (rpc_service.setJobStatus(2, jobhistory[2], jobhistory[1], jobhistory[3], jobhistory[4],
										     jobhistory[8], (jobhistory[6], jobhistory[7]),
										     jobhistory[10], ast.literal_eval(jobhistory[11]))) == 0:
								storage.update(1, jobhistory[0])
							else:
								storage.update(0, jobhistory[0])
						except:
							logger.exception("unable to send job status to the engine!", extra=d)
							storage.update(0, jobhistory[0])
					else:
						storage.update(0, jobhistory[0])
						logger.error("The Engine process was not ready when the job id " +
							      jobhistory[1] + " executing command " + jobhistory[3] + " ended!", extra=d)
			storage.close()
		except:
			logger.exception("history not saved!", extra=d)
			storage.close()
	
	else:
		logger.error("Unable to store the ended state of the job id " +
			     str(job_id) + " executing command " + command, extra=d)
			
logger.debug("FancyJobRunner : finished", extra=d)
