import cherrypy

import os

from cherrypy.lib import static

class Images(object):
    @cherrypy.expose
    def index(self,filename):

        return static.serve_file("/home/ec2-user/images/"+filename)

