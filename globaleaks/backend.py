# -*- coding: UTF-8
#   backend
#   *******
#   :copyright: 2012 Hermes No Profit Association - GlobaLeaks Project
#   :author: Claudio Agosti <vecna@globaleaks.org>
#            Arturo Filastò <art@globaleaks.org>
#   :license: see LICENSE
#

"""
Here is the logic for creating a twisted service. In this part of the code we
do all the necessary high level wiring to make everything work together.
Specifically we create the cyclone web.Application from the API specification,
we create a TCPServer for it and setup logging.

We also set to kill the threadpool (the one used by Storm) when the application
shuts down.
"""

import os

# hack to add globaleaks to the sys path
# this would avoid export PYTHONPATH=`pwd`
#cwd = '/'.join(__file__.split('/')[:-1])
#sys.path.insert(0, os.path.join(cwd, '../'))

from globaleaks.db import threadpool
from globaleaks.rest import api

from twisted.application.service import Application
from twisted.application import internet

from twisted.internet import reactor

from twisted.python import log
from cyclone import web

from twisted.python.log import FileLogObserver
from twisted.python.logfile import DailyLogFile

application = Application('GLBackend')
GLBackendAPIFactory = web.Application(api.spec, debug=True)
GLBackendAPI = internet.TCPServer(8082, GLBackendAPIFactory)
GLBackendAPI.setServiceParent(application)

# XXX make this a config option
log_file = "/tmp/glbackend.log"

log_folder = os.path.join('/', *log_file.split('/')[:-1])
log_filename = log_file.split('/')[-1]
daily_logfile = DailyLogFile(log_filename, log_folder)
log.addObserver(FileLogObserver(daily_logfile).emit)

reactor.addSystemEventTrigger('after', 'shutdown', threadpool.stop)
