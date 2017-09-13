#! /usr/bin/python

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('fancycron.views',
    # Examples:
    # url(r'^$', 'fancronserver.views.home', name='home'),
    # url(r'^fancycronserver/', include('fancycronserver.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
	url(r'^jobhistory/(?P<jobhistory_id>\d+)/job_exec_user_error/$', 'job_exec_user_error'),
	#url(r'^$', 'job_exec_user_error'),
)
