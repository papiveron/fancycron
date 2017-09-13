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
# Web service for FanyCron server module

# Required Modules
#------------------------------------------------------------------------------------------------
import socket
from datetime import datetime
from lxml import etree
from django.db.models import Q
from django.http import HttpResponse
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from django.views.decorators.csrf import csrf_exempt 
from models import Job, Schedule, SystemUser, Host, JobHistory, setRemoteBackendQuery

# Global variables initialisation
#------------------------------------------------------------------------------------------------
dispatcher = SimpleXMLRPCDispatcher(allow_none=True, encoding=None) # Python 2.5
ip_list = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]
if ip_list : server_ip = ip_list[0]
else : server_ip = None

# Static functions declaration
#-----------------------------------------------------------------------------------------------
@csrf_exempt
def rpc_handler(request):
        """
        the actual handler:
        if you setup your urls.py properly, all calls to the xml-rpc service
        should be routed through here.
        If post data is defined, it assumes it's XML-RPC and tries to process as such
        Empty post assumes you're viewing from a browser and tells you about the service.
        """

        if len(request.POST):
                response = HttpResponse(mimetype="application/xml")
                response.write(dispatcher._marshaled_dispatch(request.raw_post_data))
        else:
                response = HttpResponse()
                response.write("<b>This is an XML-RPC Service.</b><br>")
                response.write("You need to invoke it using an XML-RPC Client!<br>")
                response.write("The following methods are available:<ul>")
                methods = dispatcher.system_listMethods()

                for method in methods:
                        sig = dispatcher.system_methodSignature(method)
                        help =  dispatcher.system_methodHelp(method)

                        response.write("<li><b>%s</b>: [%s] %s" % (method, sig, help))

                response.write("</ul>")
                response.write('<a href="http://www.djangoproject.com/"> <img src="http://media.djangoproject.com/img/badges/djangomade124x25_grey.gif" border="0" alt="Made with Django." title="Made with Django."></a>')

        response['Content-length'] = str(len(response.content))
        return response

def getJobList(ip_address):
        """
        Function taking a host ip address and return 
	all jobs of the host
        """
	if(ip_address == server_ip):
		ip_address = "127.0.0.1"
	#job_list = Job.objects.filter(Q(job_status = "Scheduled") | Q(job_status = "Shifted"), host__host_ip__contains = ip_address)
	job_list = Job.objects.filter(job_status = "Scheduled", host__host_ip__contains = ip_address)
	job_tree = etree.Element("JobList")
	for job in job_list:
		job_tag = etree.SubElement(job_tree, "Job")
		etree.SubElement(job_tag, "id").text = str(job.job_id)
		etree.SubElement(job_tag, "name").text = str(job.job_name)
		etree.SubElement(job_tag, "user").text = str(SystemUser.objects.get(systemuser_id = job.user_id).systemuser_name)
		etree.SubElement(job_tag, "command").text = str(job.job_command)
		etree.SubElement(job_tag, "command_param").text = str(job.job_command_parameter)
		etree.SubElement(job_tag, "status").text = str(job.job_status)
		etree.SubElement(job_tag, "shift").text = job.job_execution_shift_time and str(job.job_execution_shift_time)
		schedule_tag = etree.SubElement(job_tag, "schedule")
		etree.SubElement(schedule_tag, "minute").text = str(Schedule.objects.get(schedule_id = job.schedule_id).minute)
		etree.SubElement(schedule_tag, "hour").text = str(Schedule.objects.get(schedule_id = job.schedule_id).hour)
		etree.SubElement(schedule_tag, "dom").text = str(Schedule.objects.get(schedule_id = job.schedule_id).day_of_month)
		etree.SubElement(schedule_tag, "month").text = str(Schedule.objects.get(schedule_id = job.schedule_id).month)
		etree.SubElement(schedule_tag, "dow").text = str(Schedule.objects.get(schedule_id = job.schedule_id).day_of_week)
	
		return ((etree.tostring(job_tree, pretty_print=True)))

def createJob(job):
	try:
            job_tag = etree.Element("Job")
            etree.SubElement(job_tag, "id").text = str(job.job_id)
            etree.SubElement(job_tag, "name").text = str(job.job_name)
            etree.SubElement(job_tag, "user").text = str(models.SystemUser.objects.get(systemuser_id = job.user_id).systemuser_name)
            etree.SubElement(job_tag, "command").text = str(job.job_command)
            etree.SubElement(job_tag, "command_param").text = str(job.job_command_parameter)
            etree.SubElement(job_tag, "status").text = str(job.job_status)
            schedule_tag = etree.SubElement(job_tag, "schedule")
            etree.SubElement(schedule_tag, "minute").text = str(models.Schedule.objects.get(schedule_id = job.schedule_id).minute)
            etree.SubElement(schedule_tag, "hour").text = str(models.Schedule.objects.get(schedule_id = job.schedule_id).hour)
            etree.SubElement(schedule_tag, "dom").text = str(models.Schedule.objects.get(schedule_id = job.schedule_id).day_of_month)
            etree.SubElement(schedule_tag, "month").text = str(models.Schedule.objects.get(schedule_id = job.schedule_id).month)
            etree.SubElement(schedule_tag, "dow").text = str(models.Schedule.objects.get(schedule_id = job.schedule_id).day_of_week)
	    return(etree.tostring(job_tag, pretty_print=True))
	except:
                log.error('Error occured in fonction createJob')
		return (None)

def setJobStatus(mode, history_id, job, status, output, process_time, user, time_info):
	print "job status has changed : ", type(job['id']), job['id'], " jobhistory_id : ", history_id, " ", status, " executing user ", user
	if time_info:
		print time_info["next"], " ", process_time, " ", time_info["prev"]
	#if "RUNNING" in status:
	create_id = None
	if process_time[0] == 'None':
		process_time[0] = None
	if process_time[1] == 'None':
		process_time[1] = None
	if mode == 0:
		if job['id'] <= 0:
			print "Non existing Job", job['id']
			try:
				setRemoteBackendQuery("CreateJob")
				schedule = Schedule.objects.get_or_create(minute = job['schedule']['minute'],
									  hour = job['schedule']['hour'],
									  day_of_month = job['schedule']['dom'],
									  month = job['schedule']['month'],
									  day_of_week = job['schedule']['dow'])
				schedule[0].save()
				print "\nSchedule id : ", schedule[0].schedule_id
				print "host parameter ", job['host_name'],  " ", job['host_ip']
				new_host = Host.objects.get_or_create(host_name = job['host_name'])
				new_host[0].save()
				if job['host_ip'] and new_host[0].host_id:
					Host.objects.filter(host_id = new_host[0].host_id).update(host_ip = job['host_ip'])
				print "\nnew_host id : ", new_host[0].host_id
				new_user = new_host[0].systemuser_set.get_or_create(systemuser_name = job['user'])
				print "\nnew_user id : ", new_user[0].systemuser_id
				j = schedule[0].job_set.get_or_create(host = new_host[0],
								      user = new_user[0],
								      job_crontab_entry = job['command'])
				if job['command'] and j[0].job_id:
					job['id'] = j[0].job_id
					Job.objects.filter(job_id = j[0].job_id).update(job_name = job['command'], job_command = job['command'], job_status = "Planified")
					print "New job created or gotten", job['id']
					created_id = j[0].job_id
				setRemoteBackendQuery(None)
			except:
				print "Get a fatal error when creating host, data will be deleted"
			#RemoteBackendQuery = None
		#else:
		print "Creating History"
		try:
			run_number = 0
			j = Job.objects.get(job_id = job['id'])
			scheduled_time = Job.objects.get(job_id = job['id']).job_next_execution
			jobhistory = j.jobhistory_set.create(job_started_time = process_time[0],
							     job_ended_time = process_time[1],	
							     job_scheduled_time = scheduled_time,
							     jobhistory_status = status,
							     jobhistory_output = output,
							     job_executing_user = user)
			print "\n\nupdating job!!!!", job['id'], process_time, time_info
			Job.objects.filter(job_id = job['id']).update(job_status = "Planified",
								      job_last_status = 'None',
								      job_execution_shift_time = None,
								      job_last_execution = process_time[0],
								      job_next_execution = time_info and time_info["next"],
								      job_previous_execution = time_info and time_info["prev"])
			print "\n papa i said History created!!!!", jobhistory.jobhistory_id, "and the job ", j.job_id
			run_number = jobhistory.jobhistory_id
			return (run_number, str(created_id))
		except:
			print "mais qu'est ce qui se passe? ", run_number
			return (run_number, None)
	else:
		try:
			if history_id > 0:
				if process_time[0] != 'None' and process_time[1] != 'None':
					format = "%Y-%m-%d %H:%M:%S.%f"
					t0 = datetime.strptime(process_time[0], format)
					t1 = datetime.strptime(process_time[1], format)
					t = str(t1 - t0)
				else:
					t = "0:00:00"
				JobHistory.objects.filter(jobhistory_id = history_id).update(job_started_time = process_time[0],
											     job_ended_time = process_time[1],
											     jobhistory_status = status,
											     jobhistory_output = output,
											     job_executing_user = user,
											     job_execution_duration = t)
				
			elif history_id != -2:
				print "\n why isn't a good history id ? ", history_id
				setJobStatus(0, history_id, job, status, output, process_time, user, time_info)
			if mode == 2 and job['id'] > 0:
				Job.objects.filter(job_id = job['id']).update(job_last_result = status)
			return(0, None)
		except:
			print "hum these errors"
			return (-2, None)

def notify(state):
	print state

def setCreateResult(process_result, crontab_line):
	print "Ha!  Seems like a job has been created"
	print crontab_line , " from server side"
	print process_result[1]
	shift = Job.objects.filter(job_id = int(process_result[0]))[0].job_execution_shift_time
	if shift:
		ok = "Planified and Shifted Successfully on : %s" %process_result[3]
		status = 'Shifted'
	else:
		ok = "Planified Successfully on : %s" %process_result[3]
		status = 'Planified'
	print "my god, what?"
	failed = "Planification Failed on : %s" %process_result[3] + " =====> "
	warning =  "Warning  =====> " + "Attempt to planify Failed on : %s" %process_result[3] + ", Unknow error"
	if process_result[1] == "OK":
		Job.objects.filter(job_id = int(process_result[0])).update(job_status = status, 
									   job_recent_action = ok,
									   job_next_execution = shift)
	elif process_result[1] == "ERROR":
		Job.objects.filter(job_id = int(process_result[0])).update(job_recent_action = failed + process_result[2])
	else:
		Job.objects.filter(job_id = int(process_result[0])).update(job_recent_action = warning)
	Job.objects.filter(job_id = int(process_result[0])).update(job_crontab_entry = crontab_line)

dispatcher.register_function(notify, 'notify')		
dispatcher.register_function(getJobList, 'getJobList')
dispatcher.register_function(setJobStatus, 'setJobStatus')
dispatcher.register_function(setCreateResult, 'setCreateResult')
