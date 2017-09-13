#! /opt/csw/bin/python
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
# Crontab-like string parse. Inspired on crontab.py of the
# gnome-schedule-1.1.0 package.

# Required Modules
#------------------------------------------------------------------------------------------------
import re
import datetime
from os import close

# Global variables initialisation
#------------------------------------------------------------------------------------------------

# Logs configuration
#------------------------------------------------------------------------------------------------

# Module Classes declaration
#------------------------------------------------------------------------------------------------
class FancyCronParser(object):
    """Contrab-like parser for fancycron.

    Only deals with the first 5 fields of a normal crontab
    entry."""

    def __init__(self, entry, expiration = 0):
        self.__setup_timespec()
        if entry:
            self.set_value(" ".join(elem for elem in (entry.strip("#")).split()[:5]))
        self.set_expiration(expiration)

    def set_expiration(self, val):
        self.expiration = datetime.timedelta(minutes=val)

    def set_value(self, entry):
        self.data = entry
        fields = re.findall("\S+", self.data)
        if len(fields) != 5 :
            raise ValueError("Crontab entry needs 5 fields")
        self.fields = {
            "minute" : fields[0],
            "hour"   : fields[1],
            "day"    : fields[2],
            "month"  : fields[3],
            "weekday": fields[4],
            }
        if not self._is_valid():
            raise ValueError("Bad Entry")

    #### HERE BEGINS THE CODE BORROWED FROM gnome-schedule ###
    def __setup_timespec(self):
        
        self.special = {
                "@reboot"  : '',
                "@hourly"  : '0 * * * *',
                "@daily"   : '0 0 * * *',
                "@weekly"  : '0 0 * * 0',
                "@monthly" : '0 0 1 * *',
                "@yearly"  : '0 0 1 1 *'
                }

        self.timeranges = { 
                "minute"   : range(0,60), 
                "hour"     : range(0,24),
                "day"      : range(1,32),
                "month"    : range(1,13),
                "weekday"  : range(0,8)
                }

        self.timenames = {
                "minute"   : "Minute",
                "hour"     : "Hour",
                "day"      : "Day of Month",
                "month"    : "Month",
                "weekday"  : "Weekday"
                }

        self.monthnames = {
                "1"        : "Jan",
                "2"        : "Feb",
                "3"        : "Mar",
                "4"        : "Apr",
                "5"        : "May",
                "6"        : "Jun",
                "7"        : "Jul",
                "8"        : "Aug",
                "9"        : "Sep",
                "10"       : "Oct",
                "11"       : "Nov",
                "12"       : "Dec"
                }

        self.downames = {
                "0"        : "Sun",
                "1"        : "Mon",
                "2"        : "Tue",
                "3"        : "Wed",
                "4"        : "Thu",
                "5"        : "Fri",
                "6"        : "Sat",
                "7"        : "Sun"
                }

    def checkfield (self, expr, type):
        """Verifies format of Crontab timefields

        Checks a single Crontab time expression.
        At first possibly contained alias names will be replaced by their
        corresponding numbers. After that every asterisk will be replaced by
        a "first to last" expression. Then the expression will be splitted
        into the komma separated subexpressions.

        Each subexpression will run through: 
        1. Check for stepwidth in range (if it has one)
        2. Check for validness of range-expression (if it is one)
        3. If it is no range: Check for simple numeric
        4. If it is numeric: Check if it's in range

        If one of this checks failed, an exception is raised. Otherwise it will
        do nothing. Therefore this function should be used with 
        a try/except construct.  
        """

        timerange = self.timeranges[type]

        # Replace alias names only if no leading and following alphanumeric and 
        # no leading slash is present. Otherwise terms like "JanJan" or 
        # "1Feb" would give a valid check. Values after a slash are stepwidths
        # and shouldn't have an alias.
        if type == "month": alias = self.monthnames.copy()
        elif type == "weekday": alias = self.downames.copy()
        else: alias = None
        if alias != None:
            while True:
                try: key,value = alias.popitem()
                except KeyError: break
                expr = re.sub("(?<!\w|/)" + value + "(?!\w)", key, expr)

        expr = expr.replace("*", str(min(timerange)) + "-" + str(max(timerange)) )

        lst = expr.split(",")
        rexp_step = re.compile("^(\d+-\d+)/(\d+)$")
        rexp_range = re.compile("^(\d+)-(\d+)$")

        expr_range = []
        for field in lst:
            # Extra variables for time calculation
            step = None
            buff = None
            
            result = rexp_step.match(field)
            if  result != None:
                field = result.groups()[0]
                # We need to take step in count
                step = int(result.groups()[1])
                if step not in timerange:
                    raise ValueError("stepwidth",
                                     self.timenames[type],
                                     "Must be between %(min)s and %(max)s" % { "min": min(timerange),
                                                                               "max": max(timerange) } )

            result = rexp_range.match(field)
            if (result != None): 
                if (int(result.groups()[0]) not in timerange) or (int(result.groups()[1]) not in timerange):
                    raise ValueError("range",
                                     self.timenames[type],
                                     "Must be between %(min)s and %(max)s" % { "min": min(timerange),
                                                                               "max": max(timerange) } )
                # Now we deal with a range...
                if step != None :
                    buff = range(int(result.groups()[0]), int(result.groups()[1])+1, step)
                else :
                    buff = range(int(result.groups()[0]), int(result.groups()[1])+1)

            elif not field.isdigit():
                raise ValueError("fixed",
                                 self.timenames[type],
                                 "%s is not a number" % ( field ) )
            elif int(field) not in timerange:                
                raise ValueError("fixed",
                                 self.timenames[type],
                                 "Must be between %(min)s and %(max)s" % { "min": min(timerange),
                                                                           "max": max(timerange) } )
            if buff != None :
                expr_range.extend(buff)
            else :
                expr_range.append(int(field))

        expr_range.sort()
        # Here we may need to check wether some elements have duplicates
        self.fields[type] = expr_range
 

    #### HERE ENDS THE CODE BORROWED FROM gnome-schedule ###

    def _is_valid(self):
        """Validates the data to check for a well-formated cron
        entry.
        Returns True or false"""

        try:
            for typ, exp in self.fields.items():
                self.checkfield(exp, typ)
        except ValueError,(specific,caused,explanation):
            print "PROBLEM TYPE: %s, ON FIELD: %s -> %s " % (specific,caused,explanation)
            return False
        return True

    def __next_time(self, time_list, time_now):
        """Little helper function to find next element on the list"""
        tmp = [x for x in time_list if x >= time_now]
        carry = False
        if len(tmp) == 0:
            carry = True
            sol = time_list[0]
        else:
            if not carry:
                sol = tmp[0]
            else :
                if len(tmp) == 1:
                    carry = True
                    sol = time_list[0]
                else :
                    carry = False
                    sol = tmp[1]
        return sol, carry

    def __prev_time(self, time_list, item):
        """Little helper function to find next element on the list"""
        pos = time_list.index(item)
        elem = time_list[pos-1]
        carry = elem >= time_list[pos]
        return elem, carry

    def __next_month(self, month, sol):
        """Find next month of execution given the month arg. If month
        is different than current calls all the other __next_*
        functions to set up the time."""
        
        sol['month'], carry = self.__next_time(self.fields['month'], month)
        if carry :
            sol['year'] += 1
        if sol['month'] != month :
            self.__next_day(1,sol)
            self.__next_hour(0,sol)
            self.__next_minute(0,sol)
            return False
        return True

    def __do_next_minute(self, time_list, time_now):
        """Little helper function to find next element on the list"""
        tmp = [x for x in time_list if x > time_now]
        carry = False
        if len(tmp) == 0:
            carry = True
            sol = time_list[0]
        else:
            if not carry:
                sol = tmp[0]
            else :
                if len(tmp) == 1:
                    carry = True
                    sol = time_list[0]
                else :
                    carry = False
                    sol = tmp[1]
        return sol, carry

    def __next_minute(self, minute, sol):
        """Find next minute of execution given the minute arg."""
        sol['minute'], carry = self.__do_next_minute(self.fields['minute'], minute)
        if carry:
            self.__next_hour(sol['hour']+1, sol)
        return True

    def __next_hour(self, hour, sol):
        """Find next hour of execution given the hour arg. If hour is
        different than current calls the __next_hour function to set
        up the minute """
        
        sol['hour'], carry = self.__next_time(self.fields['hour'], hour)
        if carry:
            self.__next_day(sol['day']+1, sol)
        if sol['hour'] != hour:
            self.__next_minute(0,sol)
            return False
        return True

    #el weekday se calcula a partir del dia, el mes y ao dentro de sol
    def __next_day(self, day, sol):
        """Find next day of execution given the day and the month/year
        information held on the sol arg. If day is different than
        current calls __next_hour and __next_minute functions to set
        them to the correct values"""
        now = datetime.date(sol['year'], sol['month'], day)
        # The way is handled on the system is monday = 0, but for crontab sunday =0
        weekday = now.weekday()+1
        # first calculate day
        day_tmp, day_carry = self.__next_time(self.fields['day'], day)
        day_diff = datetime.date(sol['year'], sol['month'], day_tmp) - now

        # if we have all days but we don't have all weekdays we need to
        # perform different
        if len(self.fields['day']) == 31 and len(self.fields['weekday']) != 8:
            weekday_tmp, weekday_carry = self.__next_time(self.fields['weekday'], weekday)
            # Both 0 and 7 represent sunday
            weekday_tmp -= 1
            if weekday_tmp < 0 : weekday_tmp = 6
            weekday_diff = datetime.timedelta(days=weekday_tmp - (weekday - 1))
            if weekday_carry :
                weekday_diff += datetime.timedelta(weeks=1)
            weekday_next_month = (now + weekday_diff).month != now.month
            # If next weekday is not on the next month
            if not weekday_next_month :
                sol['day'] = (now + weekday_diff).day
                if sol['day'] != day :
                    self.__next_hour(0,sol)
                    self.__next_minute(0, sol)
                    return False
                return True
            else :
                flag = self.__next_month(sol['month']+1, sol)
                if flag :
                    return self.__next_day(0, sol)
                return False

        # if we don't have all the weekdays means that we need to use
        # them to calculate next day
        if len(self.fields['weekday']) != 8:
            weekday_tmp, weekday_carry = self.__next_time(self.fields['weekday'], weekday)
            # Both 0 and 7 represent sunday
            weekday_tmp -= 1
            if weekday_tmp < 0 : weekday_tmp = 6
            weekday_diff = datetime.timedelta(days=weekday_tmp - (weekday - 1))
            if weekday_carry :
                weekday_diff += datetime.timedelta(weeks=1)
            weekday_next_month = (now + weekday_diff).month != now.month
            # If next weekday is not on the next month
            if not weekday_next_month :
                #  If the next day is on other month, the next weekday
                #  is closer to happen so is what we choose
                if day_carry:
                    sol['day'] = (now + weekday_diff).day
                    if sol['day'] != day :
                        self.__next_hour(0,sol)
                        self.__next_minute(0, sol)
                        return False
                    return True
                else :
                    # Both day and weekday are good candidates, let's
                    # find out who is going to happen
                    # sooner
                    diff = min(day_diff, weekday_diff)
                    sol['day'] = (now+diff).day
                    if sol['day'] != day :
                        self.__next_hour(0,sol)
                        self.__next_minute(0, sol)
                        return False
                    return True
                
        sol['day'] = day_tmp
        if day_carry :
            self.__next_month(sol['month']+1, sol)
        if sol['day'] != day :
            self.__next_hour(0,sol)
            self.__next_minute(0, sol)
            return False
        return True
                

    def next_run(self, time = datetime.datetime.now()):
        """Calculates when will the next execution be."""
        sol = {'minute': 0, 'hour': 0, 'day': 0, 'month' : 0, 'year' : time.year}
        # next_month if calculated first as next_day depends on
        # it. Also if next_month is different than time.month the
        # function will set up the rest of the fields
        self.__next_month(time.month, sol) and \
                                      self.__next_day(time.day, sol) and \
                                      self.__next_hour(time.hour, sol) and \
                                      self.__next_minute(time.minute, sol)
        return datetime.datetime(sol['year'], sol['month'], sol['day'], sol['hour'], sol['minute'], time.second)

    def prev_run(self, time = datetime.datetime.now()):
        """Calculates when the previous execution was."""
        base = self.next_run(time)
        # minute
        prev_minute, carry = self.__prev_time(self.fields['minute'], base.minute)
        min_diff = datetime.timedelta(minutes=(base.minute - prev_minute))
        base -= min_diff
        if not carry :
            return base

        # hour
        prev_hour, carry = self.__prev_time(self.fields['hour'], base.hour)
        hour_diff = datetime.timedelta(hours=(base.hour - prev_hour))
        base -= hour_diff
        if not carry :
            return base

        # day
        prev_day, carry_day = self.__prev_time(self.fields['day'], base.day)
        day_diff = datetime.timedelta(days=(base.day - prev_day))
        prev_weekday, carry_weekday = self.__prev_time(self.fields['weekday'], base.weekday()+1)
        
        # if we have all days but we don't have all weekdays we need to
        # perform different
        if len(self.fields['day']) == 31 and len(self.fields['weekday']) != 8:
            # Both 0 and 7 represent sunday
            prev_weekday -= 1
            if prev_weekday < 0 : prev_weekday = 6
            
            if carry_weekday :
                day_diff = datetime.timedelta(days=7+base.weekday() - prev_weekday)
                carry = base.month != (base - day_diff).month
            else :
                weekday_diff = datetime.timedelta(days=base.weekday() - prev_weekday)
                # weekday no es en el otro mes
                day_diff = min([day_diff, weekday_diff])
                carry = False

        elif len(self.fields['weekday']) != 8:
            # Both 0 and 7 represent sunday
            prev_weekday -= 1
            if prev_weekday < 0 : prev_weekday = 6
            weekday_diff = datetime.timedelta(days=base.weekday() - prev_weekday)
            
            if carry_weekday :
                weekday_diff += datetime.timedelta(weeks=1)
                if carry_day :
                    # ambos son el otro mes
                    day_diff = max([day_diff, weekday_diff])
                    carry = True
                else :
                    # el day simple esta en el mismo mes y el weekday en otro
                    pass
            else :
                # weekday no es en el otro mes
                if carry_day :
                    # el day esta en el otro mes y el weekday no
                    prev_day = weekday_diff
                    carry = False
                else :
                    # ambos estan el el mero mes
                    day_diff = min([day_diff, weekday_diff])
                    carry = False
                
        else :
            carry = carry_day
        base -= day_diff
        if not carry :
            return base

        # month
        prev_month, carry = self.__prev_time(self.fields['month'], base.month)
        month_diff = datetime.date(base.year, base.month, base.day) - \
                     datetime.date(base.year, prev_month, base.day)
        base -= month_diff

        return base 



    def is_expired(self, time = datetime.datetime.now()):
        """If the expiration parameter has been set this will check
        wether too much time has been since the cron-entry. If the
        expiration has not been set, it throws ValueError."""
        if self.expiration == 0 :
            raise ValueError("Missing argument",
                             "Expiration time has not been set")
        next_beg = self.next_run(time)
        next_end = next_beg + self.expiration
        prev_beg = self.prev_run(time)
        prev_end = prev_beg + self.expiration
        if (time >= next_beg and time <= next_end) or (time >= prev_beg and time <= prev_end) :
            return False
        return True

# Starting Module process
#------------------------------------------------------------------------------------------------
def _test():
    import doctest
    doctest.testfile("cronTest.txt")
    test_file = open("cronTest.txt")
    for line in test_file:
        if len(line) >= 10 and line[0] != "#":
          try:
              entry = FancyCronParser(line)
              print entry.next_run()
              print entry.prev_run()
          except:
              print """Error getting crontabs time executions, may be you have a bad crontab
                    entry, or you the day you're assking crontab on, does not match the crontab 
                    schedule day, or the test file does not exist"""
    test_file.close()

if __name__ == "__main__" :
    _test()
