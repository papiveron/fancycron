#! /usr/bin/python

# Module Classes declaration
#------------------------------------------------------------------------------------------------

class FancyServerStorage:
    "Class for database and storage processing"
    def __init__(self):
        print "contructing storage"
        self._job_list = {}
        
    def update(self, status, job):
        print "Updating Job"
