import MySQLdb

import cherrypy

import os

import json

from require import require

class Following(object):

    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True,
        'tools.sessions.locking': 'explicit' #this and the acquire_lock and the release_lock statements in the login and logout functions are necessary so that multiple ajax requests can be processed in parallel in a single session
    }

    @cherrypy.expose
    @require()
    def index(self):

        gtag_string = open("gtag.js").read()

        disclaimer_string = open("disclaimer.html").read()
        
        desktop_menu_string = open("desktop_authenticated_menu.html").read()
        mobile_menu_string = open("mobile_authenticated_menu.html").read()
        
        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]
        
        dbname = "nplat"

        is_mobile = False

        if "User-Agent" in cherrypy.request.headers and ("Android" in cherrypy.request.headers['User-Agent'] or "iPhone" in cherrypy.request.headers['User-Agent'] or "iPad" in cherrypy.request.headers['User-Agent']):
            is_mobile = True

        conn = MySQLdb.connect(host='nplat-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)
            
        curs = conn.cursor()
        
        curs.execute("use "+dbname+";")    
            
        curs.execute("select followed from follows where follower=\""+cherrypy.session.get('_cp_username')+"\"");
    
        follows_fetchall = curs.fetchall()

        colnames = [desc[0] for desc in curs.description]

        body_string = "<center>\n"
        
        for follow in follows_fetchall:
            follow_dict=dict(zip(colnames, follow))        
            body_string += "<a href=/"+follow_dict["followed"]+">"+follow_dict["followed"]+"</a><br>\n" 

        body_string += "<br>\n"
                
        colnames = [desc[0] for desc in curs.description]    

        desktop_html_string = open("desktop.html").read()
            
        desktop_html_string=desktop_html_string.format(
            a=gtag_string,
            b="",
            c=desktop_menu_string,
            d=body_string,
            e=disclaimer_string)
        
        mobile_html_string = open("mobile.html").read()
            
        mobile_html_string = mobile_html_string.format(
            a=gtag_string,
            b="",
            c=mobile_menu_string,
            d=body_string,
            e=disclaimer_string)
            
        if is_mobile:
            html_string = mobile_html_string
        else:
            html_string = desktop_html_string
                
        return html_string
