import MySQLdb

import cherrypy

import os

import json

from cherrypy.lib import static

from require import require

from auth import is_session_authenticated

json_out = cherrypy.config(**{'tools.json_out.on': True})
json_in = cherrypy.config(**{'tools.json_in.on': True})

class Repost(object):

    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True,
        'tools.sessions.locking': 'explicit' #this and the acquire_lock and the release_lock statements in the login and logout functions are necessary so that multiple ajax requests can be processed in parallel in a single session
    }

    @cherrypy.expose
    @require()
    @json_in
    def index(self):

        post_id = cherrypy.request.json['post_id']        

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "nplat"

        json_object = {}

        json_object["success"] = True

        json_object["errors"] = []

        conn = MySQLdb.connect(host='nplat-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("select * from posts where username = \""+cherrypy.session.get('_cp_username')+"\" and parent_unique_id = \""+post_id+"\";")

        if len(curs.fetchall()) > 0:
                json_object["success"] = False
                json_object["errors"] = ["You already reposted this post."]

                print json.dumps(json_object)
                return json.dumps(json_object)
        
        curs.execute('insert into posts set username="'+cherrypy.session.get('_cp_username')+'", parent_unique_id="'+post_id+'", time=now(6);')

        conn.commit()
