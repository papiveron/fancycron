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
# Storage manager for FanyCron client module

# Required Modules
#------------------------------------------------------------------------------------------------
import time
import sqlite3

# Module Classes declaration
#------------------------------------------------------------------------------------------------

class FancyClientStorage:
	"FancyCron cleint data base management class"
	def __init__(self, database = 'fancyclient.db', table = 'jobhistory'):
		self._db = database
		self.__conn = sqlite3.connect(self._db)
		self.__is_opened = True
		self.__cursor = self.__conn.cursor()
		self._current_table = table
		self.__ready = False
		#self.__conn.commit()
		try:
			self.__cursor.execute("create table if not exists " + self._current_table + " (history_id INTEGER PRIMARY KEY,job_id INTEGER, jobhistory_id INTEGER, job_name TEXT, job_status TEXT, job_scheduled_time DATE, job_started_time DATE, job_ended_time DATE, output TEXT, historized TEXT, user TEXT, timeinfo TEXT)")
			self.__ready = True
			self.__conn.commit()
		except:
			pass
		
	def is_ready(self):
                return (self.__ready, self.__is_opened)

	def connect(self):
                try:
			self.__conn = sqlite3.connect(self._db)
			self.__cursor = self.__conn.cursor()
			self.__is_opened = True
                except:
			self.__is_opened = False
		return self.__is_opened
		
	def close(self):
                if not self.__is_opened :
			self.__cursor.close()
			self.__conn.close()
			self.__is_opened = False
		
	def insert(self, value):
		'''value = (job_id (1), jobhistory_id(2), job_name(3), job_status(4), job_scheduled_time(5),
		job_started_time(6), job_ended_time(7), output(8), historized(9), user(10), timeinfo(11))'''
		return_value = True
		param = (self._current_table,) + value
		try:
			self.__cursor.execute("insert into " + self._current_table + " (job_id, jobhistory_id, job_name, job_status, job_scheduled_time, job_started_time, job_ended_time, output, historized, user, timeinfo) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", value)
			#print "insert succeed!"
			self.__conn.commit()
		except:
			#print "insert failed!"
			return_value = False
		self.__cursor.execute("select * from " + self._current_table + " where (job_status not like '%ENDED%' and job_started_time = ?)", (value[5],))
		return(return_value, self.__cursor.fetchall())
        

        def create_table(self, table_name, fields):
		try:
			self.__cursor.execute('create table ' + table_name + fields)
		except:
			return (False)
		self.__conn.commit()
		return (True)
        
        def update(self, status, history__id):
		if status == 1:
			self.__cursor.execute("update %s set historized = 'YES' where history_id = %d" % (self._current_table, history__id))
		#	print "\n---update database sucessfully!!! : ", history__id
		else:
			self.__cursor.execute("update %s set historized = 'NO' where history_id = %d" % (self._current_table, history__id))
		#	print "\n---update database unsucessfully!!!"
		self.__conn.commit()
            
	def set_ended(self, job_status, job_ended_time, output, history_id, jobhistory_id):
		self.__cursor.execute('update ' + self._current_table + ' set jobhistory_id = ?' + ', job_status = "' + job_status + '", job_ended_time = "' + job_ended_time + '", output = ?' + ', historized = ' + "'NO'"  + ' where history_id = ?', (jobhistory_id, output, history_id))
		self.__conn.commit()
		self.__cursor.execute("select * from " + self._current_table + " where historized != 'YES'")
		return(self.__cursor.fetchall())
		#print "finish end"

        def delete(self, history_id):
		self.__cursor.execute("delete from " + self._current_table + " where history_id = ?", (history_id,))
		self.__conn.commit()

        def get_non_ended(self):
		self.__cursor.execute("select * from " + self._current_table + " where job_status not like '%ENDED%'")
		return(self.__cursor.fetchall())
        
        def get_non_historized(self):
		self.__cursor.execute("select * from " + self._current_table + " where historized = 'NO'")
		return(self.__cursor.fetchall())
