#! /usr/bin/python

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'fancronserver.views.home', name='home'),
    # url(r'^fancycronserver/', include('fancycronserver.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
	#url(r'^$', 'job_exec_user_error'),
    	url(r'^fancycron/', include('fancycron.urls')),
	url(r'^xml_rpc_srv$', 'fancycron.xml_rpc_srv.rpc_handler'),
	url(r'^admin/', include(admin.site.urls)),
)
