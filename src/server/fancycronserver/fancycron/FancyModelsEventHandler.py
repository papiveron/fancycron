#-*- coding:utf-8 -*-
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
# Models Event Hanfler for FanyCron admin module

# Required Modules
#------------------------------------------------------------------------------------------------
import os
import models
import logging
import datetime
import xmlrpclib
from lxml import etree
from shutil import move
from tempfile import mkstemp
from django.db.models import Q

# Global variables initialisation
#------------------------------------------------------------------------------------------------
server_path = '/home/papi/dev/fancycron/trunk/server'
# server_path = '/opt/product/fancycron/'                                                                                                                      
#server_path = '/home/veron/projets/fancycron/src/server'
#server_path = '/root/fancycron/trunk/server'
server_rpc_log_file =  server_path + '/log/server_rpc.log'

# Logs configuration
#------------------------------------------------------------------------------------------------
logging.basicConfig(level = logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename = server_rpc_log_file)

#log                     = logging.getLogger(__name__)
log                     = logging.getLogger()


# Static functions declaration
#-----------------------------------------------------------------------------------------------

def process_created(job__id, process_result):
    if process_result and job__id:
        print "haha ", process_result[4]
        shift =  models.Job.objects.filter(job_id = job__id)[0].job_next_execution
        if process_result[4]:
            print "shitf ", process_result[4]
            ok = "Planified and Shifted Successfully on : %s" %process_result[2]
            status = 'Shifted'
            shift = process_result[4]
        else:
            print "not shifted ", process_result[4]
            ok = "Planified Successfully on : %s" %process_result[2]
            status = 'Planified'
        failed = "Planification Failed on : %s" %process_result[2] + " =====> "
        warning =  "Warning  =====> " + "Attempt to planify Failed on : %s" %process_result[2] + ", Unknow error"
        if process_result[0]:
            models.Job.objects.filter(job_id = job__id).update(job_status = status, 
                                                               job_recent_action = ok,
                                                               job_next_execution = shift)
        elif not process_result[0] and process_result[1] != "WARNING":
            models.Job.objects.filter(job_id = job__id).update(job_recent_action = failed + process_result[1])
        else:
            models.Job.objects.filter(job_id = job__id).update(job_recent_action = warning)
        models.Job.objects.filter(job_id = job__id).update(job_crontab_entry = process_result[3])

def process_modified(job__id, process_result):
    if process_result and job__id:
        ##print "\n\n",  process_result, " hum!!!!!!!!!!!"
        last_status = models.Job.objects.filter(job_id = job__id)[0].job_status
        if process_result[4]:
            ok = "Modified and Shifted Successfully on : %s" %process_result[2]
        else:
            ok = "Modified Successfully on : %s" %process_result[2]
        failed = "Modification Failed on : %s" %process_result[2] + " =====> "
        warning =  "Warning  =====> " + "Attempt to modify Failed on : %s" %process_result[2] + ", Unknow error"
        if process_result[0]:
            models.Job.objects.filter(job_id = job__id).update(job_recent_action = ok)
            if process_result[4] and  last_status == "Desactivated":
                models.Job.objects.filter(job_id = job__id).update(job_last_status = "Shifted")
            else:
                models.Job.objects.filter(job_id = job__id).update(job_status = "Shifted",
                                                                   job_last_status = 'None')
        elif not process_result[0] and process_result[1] != "WARNING":
            models.Job.objects.filter(job_id = job__id).update(job_recent_action = failed + process_result[1])
        else:
            models.Job.objects.filter(job_id = job__id).update(job_recent_action = warning)
        models.Job.objects.filter(job_id = job__id).update(job_crontab_entry = process_result[3])

def process_desactivated(job__id, process_result):
    if process_result and job__id:
        result = 0
        last_status = models.Job.objects.filter(job_id = job__id)[0].job_status 
        ##print "Desactivate begin: ", result
        ok = "Desactivated Successfully on : %s" %process_result[2]
        failed = "Desactivation Failed on : %s" %process_result[2] + " =====> "
        warning =  "Warning  =====> " + "Attempt to desactivate Failed on : %s" %process_result[2] + ", Unknow error"
        if process_result[0]:
            models.Job.objects.filter(job_id = job__id).update(job_last_status = last_status,
                                                               job_status = "Desactivated",
                                                               job_recent_action = ok)
            result = 1
        ##print "Desactivate : ", result
        elif not process_result[0] and process_result[1] != "WARNING":
            models.Job.objects.filter(job_id = job__id).update(job_recent_action = failed + process_result[1])
        ##print "Desactivate error: ", result
        else:
            models.Job.objects.filter(job_id = job__id).update(job_recent_action = warning)
            ##print "Desactivate warnning: ", result
        return result

def process_activated(job__id, process_result):
    if process_result and job__id:
        result = 0
        last_status = models.Job.objects.filter(job_id = job__id)[0].job_last_status
        ok = "Activated Successfully on : %s" %process_result[2]
        failed = "Activation Failed on : %s" %process_result[2] + " =====> "
        warning =  "Warning  =====> " + "Attempt to activate Failed on : %s" %process_result[2] + ", Unknow error"
        if process_result[0]:
            models.Job.objects.filter(job_id = job__id).update(job_status = last_status,
                                                               job_last_status = 'None',
                                                               job_recent_action = ok)
            ##print "Activate : ", result
            result = 1
        elif not process_result[0] and process_result[1] != "WARNING":
            models.Job.objects.filter(job_id = job__id).update(job_recent_action = failed + process_result[1])
        else:
            models.Job.objects.filter(job_id = job__id).update(job_recent_action = warning)
        return result

def process_deleted(job__id, process_result, crontab_line = None):
    if process_result and job__id:
        ok = "Deleted Successfully on : %s" %process_result[2]
        failed = "Deletion Failed on : %s" %process_result[2] + " =====> "
        warning =  "Warning  =====> " + "Attempt to delete Failed on : %s" %process_result[2] + ", Unknow error"
        if process_result[0]:
            models.Job.objects.filter(job_id = job__id).update(job_recent_action = ok)
        elif not process_result[0] and process_result[1] != "WARNING":
            models.Job.objects.filter(job_id = job__id).update(job_recent_action = failed + process_result[1])
        else:
            models.Job.objects.filter(job_id = job__id).update(job_recent_action = warning)

# Module Classes declaration
#------------------------------------------------------------------------------------------------
class FancyModelsEventHandler(object):
    "Class for handling Fancy Client RPC services!!!"
    
    def __init__(self, client_port):
        self.__client_port = client_port
        self.__rpc_service_up = True
        if not client_port:
            self.__rpc_service_up = False
        self._func_map = {"CREATED" : process_created,
                          "MODIFIED" : process_modified,
                          "DESACTIVATED" : process_desactivated,
                          "ACTIVATED" : process_activated,
                          "DELETED" : process_deleted,
                          }

    def jobProcess(self, job, mode, old_param = None):
        if self.__rpc_service_up:
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
            #host_ip = str(models.Host.objects.get(host_id = job.host_id).host_ip)
            host_address = str(job.host.host_name)
            ##print host_ip, old_param
            address = "http://" + host_address + ":" + self.__client_port
            try:
                rpc_service = xmlrpclib.ServerProxy(address, allow_none=True)
                if old_param and old_param['name'] and (old_param['name'] != host_address):
                    ##print  old_param['ip']
                    old_param['carry'] = True
                    old_address = "http://" + old_param['name'] + ":" + self.__client_port
                    old_rpc_service = xmlrpclib.ServerProxy(old_address, allow_none=True)
                    try:
                        self._func_map['CREATED'](job.job_id, rpc_service.processJob(etree.tostring(job_tag, pretty_print=True), 'CREATED', old_param))
                    except:
                        pass
                    job_tag.find("user").text = old_param['user']
                    self._func_map['DELETED'](job.job_id, old_rpc_service.processJob(etree.tostring(job_tag, pretty_print=True), 'DELETED'))
                else:
                    if (mode == "CREATED" or
                        ((mode == "MODIFIED" or mode == "DELETED") and 
                         str(job.job_status) != "Scheduled")):
                        print "the mode ",  mode
                        self._func_map[mode](job.job_id, rpc_service.processJob(etree.tostring(job_tag, pretty_print=True), mode, old_param))
            except:
                log.error('Error sending job informations')

    def jobAlter(self, queryset, mode):
        if self.__rpc_service_up:
            rows_updated = 0
            for job in queryset:
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
                host_address = str(models.Host.objects.get(host_id = job.host_id).host_name)
                #print host_address
                address = "http://" + host_address + ":" + self.__client_port
               # try:
                rpc_service = xmlrpclib.ServerProxy(address, allow_none=True)
                if (((mode == "ACTIVATED" and job.job_status == "Desactivated") or 
                     (mode == "DESACTIVATED" and job.job_status != "Desactivated") or 
                     mode == "SHIFTED") and  str(job.job_status) != "Scheduled"):
                    #print "Desactivate before: ", rows_updated
                    rows_updated += self._func_map[mode](job.job_id, rpc_service.processJob(etree.tostring(job_tag, pretty_print=True), mode))
               # #print "Desactivate error: ", rows_updated
                    # except:
               # #print "error here!!!"
                    log.error('Error sending job informations')
            #print "Desactivate error: ", rows_updated
            return rows_updated
