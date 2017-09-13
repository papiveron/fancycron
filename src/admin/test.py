#!/usr/bin/env python
#import sys; sys.path.append('../../../') # show python where the web modules are
from WebTemplate import WebTemplate


#dict =  {
#	'welcomeMessage':'Welcome to the test page!',
#	'testVar':True,
#	'title':'Cheetah Example',
#}
		
welcomeMessage = 'Welcome to the test page!'
testVar = True
title = 'Cheetah Example'


class Test(WebTemplate):
	welcomeMessage = 'Welcome to the test page!'
	testVar = True
	title = 'Cheetah Example'
	def __init__(self):
		WebTemplate.__init__(self)
	def answer():
		self.respond()

class Test1(WebTemplate):
	def __init__(self, title, testvar, welcome):
		WebTemplate.__init__(self)
		self.welcomeMessage = welcome
		self.testVar = testvar
		self.title = title
	def answer():
		self.respond()


myClass = Test1("Cheetah Exampmle", True, "Welcome to the test page!")
#print WebTemplate.respond()
print myClass.respond()


