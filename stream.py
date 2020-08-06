import cherrypy

import os

from cherrypy.lib import static

class Stream(object):
    @cherrypy.expose
    def index(self,filename):

        return static.serve_file("/home/ec2-user/videos/"+filename,"application/x-download", "attachment","mp4 file")

