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
# Views for FanyCron admin module, use django admin module

# Required Modules
#------------------------------------------------------------------------------------------------
from django.shortcuts import get_object_or_404, render_to_response

# Statistic functions
#------------------------------------------------------------------------------------------------
def job_exec_user_error(request, jobhistory_id):
    return render_to_response('fancycron/job_exec_user_error.html', {'job' : jobhistory_id})

