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
# Models Manager for FanyCron admin module

# Required Modules
#------------------------------------------------------------------------------------------------
import os
#import views
import logging
import datetime
import ConfigParser
from django.db import models
import FancyModelsEventHandler
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.base import ModelBase
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.core.validators import validate_ipv4_address, validate_ipv6_address
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete

# Global variables initialisation
#-----------------------------------------------------------------------------------------------
#server_path = '/root/fancycron/trunk/server'
server_path = '/home/papi/dev/fancycron/trunk/server'
#server_path = '/home/veron/projets/fancycron/src/server'
#server_path = os.environ['FANCYSERVER_PATH']

server_conf_file = server_path + '/conf/server.conf'
server_log_file =  server_path + '/log/server.log'

old_param = {'name' : None, 'user': None, 'shift' : None, 'carry' : False}
RemoteBackendQuery = None
# Logs configuration
#------------------------------------------------------------------------------------------------
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=server_log_file)

# Reading configuration file
#------------------------------------------------------------------------------------------------
config = ConfigParser.ConfigParser()
client_port = ""

try:
	config.read(server_conf_file)
except:
	logging.error('Error reading configuration file : %s', server_conf_file)
try:
	client_port = config.get('network', 'client_port')
except:
	client_port = ""
	logging.error('Missing or wrong parameter in the configuration file : %s', server_conf_file)

fancy_models_event_handler = FancyModelsEventHandler.FancyModelsEventHandler(client_port)


# Static Functions
#------------------------------------------------------------------------------------------------

def setRemoteBackendQuery(value):
	global RemoteBackendQuery
	RemoteBackendQuery = value

# Module Classes declaration
#------------------------------------------------------------------------------------------------
class FancyCronModelBase(ModelBase):
	def __new__(cls, name, bases, attrs):
        	model = super(FancyCronModelBase, cls).__new__(cls, name, bases, attrs)
	        model._meta.db_table = name.lower()
	
		return model

class HostGroup(models.Model):
	__metaclass__ = FancyCronModelBase
	hostgroup_id = models.AutoField(primary_key=True)
	hostgroup_name =  models.CharField(max_length=200, default="Default", unique=True)
	hostgroup_description =  models.CharField(max_length=200, blank=True)
	hostgroup_insert_date = models.DateTimeField('HostGroup Insert Date', auto_now_add=True)
	hostgroup_update_date = models.DateTimeField('HostGroup Update Date', auto_now=True, auto_now_add=True)

	def __unicode__(self):
		return self.hostgroup_name

def get_hostgroup():
	return HostGroup.objects.get(hostgroup_name="Default")

class Host(models.Model):
	__metaclass__ = FancyCronModelBase
	host_id = models.AutoField(primary_key=True)
	hostgroup = models.ForeignKey(HostGroup,  default=lambda: get_hostgroup().hostgroup_id, blank=True, null=True, on_delete=models.SET_NULL)
	host_name =  models.CharField(max_length=200, default='localhost')
	host_ip =  models.CharField(max_length=200, default='127.0.0.1', validators=[validate_ipv4_address], blank=True)
	host_os =  models.CharField(max_length=200, blank=True)
	host_description =  models.CharField(max_length=200, blank=True)
	host_insert_date = models.DateTimeField('Host Insert Date', auto_now_add = True)
	host_update_date = models.DateTimeField('Host Update Date', auto_now = True, auto_now_add = True)
	
	def __unicode__(self):
		return self.host_name
	
	class Meta:
		unique_together = (("host_name", "hostgroup"), ("host_name", "host_ip"))
		
def get_host():
	return Host.objects.get(host_name="localhost")

class SystemUserGroup(models.Model):
	__metaclass__ = FancyCronModelBase
	systemusergroup_id = models.AutoField(primary_key=True)
	systemusergroup_name =  models.CharField(max_length=200, default = "Default", unique=True)
	systemusergroup_description =  models.CharField(max_length=200, blank=True)
	systemusergroup_insert_date = models.DateTimeField('SystemGroup Insert Date', auto_now_add=True)
	systemusergroup_update_date = models.DateTimeField('SystemGroup Update Date', auto_now=True, auto_now_add=True)
	
	def __unicode__(self):
		return self.systemusergroup_name

def get_systemgroup():
	return SystemUserGroup.objects.get(systemusergroup_name="Default")

class SystemUser(models.Model):
	__metaclass__ = FancyCronModelBase
	systemuser_id = models.AutoField(primary_key=True)
	systemusergroup = models.ForeignKey(SystemUserGroup,  default=lambda: get_systemgroup().systemusergroup_id, blank=True, null=True, on_delete=models.SET_NULL)
	host = models.ForeignKey(Host, null=True, on_delete=models.SET_NULL)
	systemuser_name =  models.CharField(max_length=200)
	systemuser_description =  models.CharField(max_length=200, blank=True)
	systemuser_insert_date = models.DateTimeField('SystemUser Insert Date', auto_now_add=True)
	systemuser_update_date = models.DateTimeField('SystemUser Update Date', auto_now=True, auto_now_add=True)

	def __unicode__(self):
		return self.systemuser_name

	class Meta:
		unique_together = ("systemuser_name", "host")
		
class Schedule(models.Model):
	__metaclass__ = FancyCronModelBase
	schedule_id = models.AutoField(primary_key=True)
	schedule_name =  models.CharField(max_length=200, unique=True)
	minute =  models.CharField(max_length=200)
	hour =  models.CharField(max_length=200)
	day_of_month =  models.CharField(max_length=200)
	month =  models.CharField(max_length=200)
	day_of_week =  models.CharField(max_length=200)
	schedule_description =  models.CharField(max_length=200, blank=True)
	schedule_insert_date = models.DateTimeField('Schedule Insert Date', auto_now_add=True)
	schedule_update_date = models.DateTimeField('Schedule Update Date', auto_now=True, auto_now_add=True)

	def __unicode__(self):
		return self.schedule_name
	
	class Meta:
		unique_together = ("minute", "hour", "day_of_month", "month", "day_of_week")


class JobDependance(models.Model):
	__metaclass__ = FancyCronModelBase
	jobdependance_id = models.AutoField(primary_key=True)
	from_job = models.ForeignKey('Job', related_name = 'from_job')
	to_job = models.ForeignKey('Job', related_name = 'to_job')
	jobdependance_name =  models.CharField(max_length=200, unique=True)
	jobdependance_criteria = models.CharField(max_length=200)
	jobdependance_description =  models.CharField(max_length=200, blank=True)
	jobdependance_insert_date = models.DateTimeField('JobDependance Insert Date', auto_now_add = True)
	jobdependance_update_date = models.DateTimeField('JobDependance Update Date', auto_now = True, auto_now_add = True)
	
	def __unicode__(self):
		return self.jobdependance_name

	class Meta:
		unique_together = ("from_job", "to_job")

class Job(models.Model):
	__metaclass__ = FancyCronModelBase
	job_id = models.AutoField(primary_key=True)
	host = models.ForeignKey(Host, default=lambda: get_host().host_id, null=True, on_delete=models.SET_NULL)
	user = models.ForeignKey(SystemUser, null=True, on_delete=models.SET_NULL)
	schedule = models.ForeignKey(Schedule, null=True, on_delete=models.SET_NULL)
	job_name =  models.CharField(max_length=200, blank=True)
	job_command =  models.CharField(max_length=200)
	job_command_parameter =  models.CharField(max_length=200, blank=True)
	job_status =  models.CharField(max_length=200, default="Scheduled")
	job_last_status =  models.CharField(max_length=200, blank=True)
	job_agent_status =  models.CharField(max_length=200, default="STOPPED")
	job_recent_action =  models.CharField(max_length=200, blank=True)
	job_last_result =  models.CharField(max_length=200, blank=True)
	job_log_address =  models.CharField(max_length=200, blank=True)
	job_description =  models.CharField(max_length=200, blank=True)
	job_crontab_entry = models.CharField(max_length=200, default = str(job_command)  + str(job_command_parameter))
	job_insert_date = models.DateTimeField('Job Insert Date', auto_now_add = True)
	job_update_date = models.DateTimeField('Job Update Date', auto_now = True, auto_now_add = True)
	job_last_execution = models.DateTimeField('Job Last Execution Time', blank=True, null=True)
	job_next_execution = models.DateTimeField('Job Next Execution Time', blank=True, null=True)
	job_previous_execution = models.DateTimeField('Job Supposed Previous Execution Time', blank=True, null=True)
	job_execution_shift_time = models.DateTimeField('Stop job execution until', blank=True, null=True)
	dependance = models.ManyToManyField("self", symmetrical = False, through = JobDependance)
	
	def __unicode__(self):
		return self.job_name

	def host_group(self):
		return(self.host.hostgroup)

	def last_result(self):
		return (self.job_last_result != "ENDEDERROR")
	last_result.boolean = True
	last_result.short_description = 'Job Last Result'

	def agent_status(self):
		return (self.job_agent_status != "STOPPED")
	agent_status.boolean = True
	agent_status.short_description = 'Job Agent Status'
	
	def get_host_url(self):
		return '../host/%s/' % (self.host_id)

	def host_link(self):
		return '<a href="%s">%s</a>' % (self.get_host_url(), self.host)
	host_link.allow_tags = True

	def get_schedule_url(self):
		return '../schedule/%s/' % (self.schedule_id)

	def schedule_link(self):
		return '<a href="%s">%s</a>' % (self.get_schedule_url(), self.schedule)
	schedule_link.allow_tags = True

	def get_user_url(self):
		return '../systemuser/%s/' % (self.user_id)

	def user_link(self):
		return '<a href="%s">%s</a>' % (self.get_user_url(), self.user)
	user_link.allow_tags = True
	
	def get_hostgroup_url(self):
		return '../hostgroup/%s/' % (self.host.hostgroup_id)

	def hostgroup_link(self):
		return '<a href="%s">%s</a>' % (self.get_hostgroup_url(),
						self.host.hostgroup)
	hostgroup_link.allow_tags = True

	class Meta:
		unique_together = ("job_command", "job_command_parameter", "user", "host")

	
class JobHistory(models.Model):
	__metaclass__ = FancyCronModelBase
	jobhistory_id = models.AutoField(primary_key=True)
	job = models.ForeignKey(Job, null=True, on_delete=models.SET_NULL)
	job_scheduled_time = models.DateTimeField('Job Scheduled Time', blank=True, null=True)
	job_started_time = models.DateTimeField('Job Started Time', blank=True, null=True)
	job_ended_time = models.DateTimeField('Job Ended Time', blank=True, null=True)
	jobhistory_status =  models.CharField(max_length=200, blank=True)
	job_executing_user =  models.CharField(max_length=200, blank=True)
	job_execution_duration =  models.CharField(max_length=200, blank=True, default = "0:00:00")
	jobhistory_output =  models.CharField(max_length=200, blank=True)
	jobhistory_insert_date = models.DateTimeField('JobHistory Insert Date', auto_now_add = True)
	jobhistory_update_date = models.DateTimeField('JobHistory Update Date', auto_now = True, auto_now_add = True)
	
	#def __unicode__(self):
	#	return self.jobhistory_id
	
	def run_number(self):
		return(str(self.jobhistory_id))
	
	def get_job_url(self):
		return '../job/%s/' % (self.job_id)

	def job_name(self):
		return '<a href="%s">%s</a>' % (self.get_job_url(), self.job)
	job_name.allow_tags = True

	def get_user_url(self):
		return '../systemuser/%s/' % (self.job.user_id)

	def job_planified_user(self):
		return '<a href="%s">%s</a>' % (self.get_user_url(), self.job.user)
	job_planified_user.allow_tags = True

	def get_executing_user_url(self):
		user_list = SystemUser.objects.filter(systemuser_name = self.job_executing_user, host = self.job.host)
		if not user_list:
			#return ('http://www.google.com/')
			return (reverse('fancycron.views.job_exec_user_error', args=(self.jobhistory_id,)))
		else:
			return '../systemuser/%s/' % (user_list[0].systemuser_id)
	
	def job_execution_user(self):
		return '<a href="%s">%s</a>' % (self.get_executing_user_url(), self.job_executing_user)
	job_execution_user.allow_tags = True
		
	def get_host_url(self):
		return '../host/%s/' % (self.job.host_id)

	def job_host(self):
		return '<a href="%s">%s</a>' % (self.get_host_url(), self.job.host)
	job_host.allow_tags = True

	#def job_execution_duration(self):
	#print self.job_ended_time, " ", self.job_started_time
	#return ((not self.job_ended_time and "None") or
	#str((self.job_ended_time - self.job_started_time)))

@receiver(pre_save, sender=Job)
def pre_save_handler(sender, instance, weak=False, **kwargs):
	if not RemoteBackendQuery:
		global old_param
		print "is it a modification????"
		try:
			old_param['user'] = str(Job.objects.get(job_id = instance.job_id).user.systemuser_name)
			old_param['name'] = str(Job.objects.get(job_id = instance.job_id).host.host_name)
			old_param['shift'] = Job.objects.get(job_id = instance.job_id).job_execution_shift_time
			print old_param['shift']
			if (old_param['user'] == str(instance.user.systemuser_name) and 
			    old_param['name'] == str(instance.host.host_name)):
				old_param['name'] = None
				old_param['user'] = None
				old_param['carry'] = False
			if ((instance.job_execution_shift_time != old_param['shift']) and
			    instance.job_execution_shift_time):
			    print 'yoo shift time has been set!!! ' , old_param['shift']
			    old_param['shift'] = str(instance.job_execution_shift_time)
			else:
				old_param['shift'] = None
		except:
			print 'yii an error occuror, may the query does not match!!! ',  type(old_param), " ", old_param
			old_param['shift'] = instance.job_execution_shift_time and str(instance.job_execution_shift_time)
						
@receiver(post_save, sender=Job)
def post_save_job_handler(sender, instance, created, weak=False, **kwargs):
	if not RemoteBackendQuery:
		print "post_save::::"
		if created:
			print "Yes we created it"
			#if instance.job_next_execution -
			fancy_models_event_handler.jobProcess(instance, "CREATED", old_param)
		else:
			#print "\next execution changed : ", type(instance.job_next_execution), " ",  instance.job_next_execution
			fancy_models_event_handler.jobProcess(instance, "MODIFIED", old_param)

@receiver(pre_delete, sender=Job)
def delete_handler(sender, instance, weak=False, **kwargs):
	if not RemoteBackendQuery:
		fancy_models_event_handler.jobProcess(instance, "DELETED")

@receiver(post_save, sender=Schedule)
def post_save_schedule_handler(sender, instance, created, weak=False, **kwargs):
	print  RemoteBackendQuery
	if not RemoteBackendQuery:
		try:
			queryset = instance.job_set.all()
			#print queryset
			if len(queryset):
				for job in queryset:
					fancy_models_event_handler.jobProcess(job, "MODIFIED")
		except:
			pass
		print "\n-----We have signaled all schedules changed!!!-----"
	
