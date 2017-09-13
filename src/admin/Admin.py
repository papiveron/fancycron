#! /usr/bin/python
import time
import cherrypy
from LoginTemplate import LoginTemplate
from FancyStotrage import FancyStorage

storage = FancyStorage()

class LoginPage(object):
	"FancyCron Login Page Clas"
        def __init__(self):
		self.tmpl = LoginTemplate()
		self.tmpl.title = "Login Page"
		self.tmpl.motd = "Login to FancyCron"
		self.tmpl.logo = "images/logo-bouygues.png"

	def index(self):
		return self.tmpl.respond()
	index.exposed = True

class HomePage(object):
	"FancyCron Home Page Class"
	def __init__(self):
		self.tmpl = HomeTemplate()
		self.tmpl.date = time.strftime("%H:%M:%S  %Y-%m-%d", time.localtime()) #The date of the day
		self.tmpl.profile = storage.getLoginProfile()


#login = LoginPage("Login Page", "Login to FancyCron System", "/images/logo-bouygues.png")
#cherrypy.config.update({'server.socket_host': '0.0.0.0',
 #                       'server.socket_port': 8080,
 #                      })
#cherrypy.quickstart(LoginPage())

#cherrypy.tree.mount(login, "/"
#cherrypy.engine.start()
	
