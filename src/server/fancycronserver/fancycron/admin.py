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
# FanyCron admin module, use django admin module

# Required Modules
#------------------------------------------------------------------------------------------------
from django.contrib import admin
from django.http import HttpResponse
from fancycron.models import Schedule
from fancycron.models import HostGroup, Host
from fancycron.models import fancy_models_event_handler 
from fancycron.models import SystemUserGroup, SystemUser
from fancycron.models import JobDependance, Job, JobHistory

# Module Classes declaration
#------------------------------------------------------------------------------------------------

class UserInline(admin.TabularInline):
    model = SystemUser
    readonly_fields = ('systemuser_insert_date', 'systemuser_update_date')
    extra = 3

class JobInline(admin.TabularInline):
    model = Job
    readonly_fields = ('job_status', 'job_last_execution', 'job_last_result', 'job_agent_status', 'job_insert_date', 'job_update_date')
    fieldsets = [
    (None, {'fields': ['schedule', 'user', 'job_name', 'job_command', 'job_command_parameter', 'job_log_address', 'job_description', 'job_status', 'job_last_result', 'job_agent_status', 'job_last_execution', 'job_insert_date', 'job_update_date']}),
    ('Execution Time Iinformation', {'fields': ['job_next_execution'], 'classes': ['collapse']}),
    ]
    extra = 3

class  HostInline(admin.TabularInline):
    model = Host 
    readonly_fields = ('host_insert_date', 'host_update_date')
    extra = 3

class JobAdmin(admin.ModelAdmin):
    readonly_fields = ('job_insert_date', 'job_update_date')
    fieldsets = [
        (None, {'fields': ['host', 'user', 'schedule', 'job_name', 'job_command', 'job_command_parameter', 'job_log_address', 'job_description', 'job_insert_date', 'job_update_date']}),
        ('Execution Time Iinformation', {'fields': ['job_execution_shift_time'], 'classes': ['collapse']}),]
    list_display = ('job_name', 'user_link', 'host_link', 'hostgroup_link', 'job_status', 'schedule_link', 'last_result', 'agent_status', 'job_last_execution', 'job_next_execution', 'job_crontab_entry', 'job_description', 'job_recent_action')
#    list_filter = ['job_insert_date']
    search_fields = ['job_name']
    date_hierarchy = 'job_insert_date'
    actions = ['activate', 'desactivate']

    def activate(self, request, queryset):
        rows_updated = fancy_models_event_handler.jobAlter(queryset, "ACTIVATED")
        message_bit = None
        if rows_updated == 0:
            self.message_user(request, "No Job was marked as activated.")
        else:
            if rows_updated == 1:
                message_bit = "1 job was"
            elif rows_updated > 1:
                message_bit = "%s jobs were" % rows_updated
            self.message_user(request, "%s successfully marked as activated." % message_bit)
    activate.short_description = "Activate"

    def desactivate(self, request, queryset):
        print "desactivation!!!!!!"
        rows_updated = fancy_models_event_handler.jobAlter(queryset, "DESACTIVATED")
        message_bit = None
        if rows_updated == 0:
            self.message_user(request, "No Job was marked as desactivated.")
        else:
            if rows_updated == 1:
                message_bit = "1 job was"
            elif rows_updated > 1:
                message_bit = "%s jobs were" % rows_updated
            self.message_user(request, "%s successfully marked as desactivated." % message_bit)
    desactivate.short_description = "Desactivate"

class  JobHistoryAdmin(admin.ModelAdmin):
    readonly_fields = ('jobhistory_insert_date', 'jobhistory_update_date')

    list_display = ('run_number', 'job_name', 'job_host', 'job_planified_user', 'job_execution_user', 'job_execution_duration', 'jobhistory_status', 'job_scheduled_time', 'job_started_time', 'job_ended_time')
    date_hierarchy = 'jobhistory_insert_date'
    search_fields = ['jobhistory_status']

class  HostGroupAdmin(admin.ModelAdmin):
    readonly_fields = ('hostgroup_insert_date', 'hostgroup_update_date')

    list_display = ('hostgroup_name', 'hostgroup_description')
    search_fields = ['hostgroup_name']
    date_hierarchy = 'hostgroup_insert_date'
    #inlines = [HostInline]

class  HostAdmin(admin.ModelAdmin):
    readonly_fields = ('host_insert_date', 'host_update_date')

    list_display = ('host_name', 'host_ip', 'host_os', 'hostgroup', 'host_description')
    search_fields = ['host_name']
    date_hierarchy = 'host_insert_date'
    #inlines = [UserInline, JobInline]

class  SystemUserGroupAdmin(admin.ModelAdmin):
    readonly_fields = ('systemusergroup_insert_date', 'systemusergroup_update_date')

    list_display = ('systemusergroup_name', 'systemusergroup_description')
    search_fields = ['systemusergroup_name']
    date_hierarchy = 'systemusergroup_insert_date'
    #inlines = [UserInline]

class  ScheduleAdmin(admin.ModelAdmin):
    readonly_fields = ('schedule_insert_date', 'schedule_update_date')

    list_display = ('schedule_name', 'minute', 'hour', 'day_of_month', 'month', 'day_of_week', 'schedule_description')
    search_fields = ['schedule_name']
    date_hierarchy = 'schedule_insert_date'

class  SystemUserAdmin(admin.ModelAdmin):
    readonly_fields = ('systemuser_insert_date', 'systemuser_update_date')

    list_display = ('systemuser_name', 'systemusergroup',  'host', 'systemuser_description')
    search_fields = ['systemuser_name']
    date_hierarchy = 'systemuser_insert_date'
    #inlines = [JobInline]

admin.site.register(HostGroup, HostGroupAdmin)
admin.site.register(Host, HostAdmin)
admin.site.register(SystemUserGroup, SystemUserGroupAdmin)
admin.site.register(SystemUser, SystemUserAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(JobDependance)
admin.site.register(Job, JobAdmin)
admin.site.register(JobHistory, JobHistoryAdmin)
