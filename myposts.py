import MySQLdb

import cherrypy

import os

import json

from cherrypy.lib import static

from require import require

class MyPosts(object):

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
            
        curs.execute("select * from posts where username = \""+cherrypy.session.get('_cp_username')+"\" order by time desc;")
            
        colnames = [desc[0] for desc in curs.description]

        posts=curs.fetchall()
        
        conn.close()
            
        body_string = "<center>\n"
            
        for post in posts:
            post_dict = dict(zip(colnames, post))
            body_string += "<div class=\"post\">\n"
            body_string += "<b>" + post_dict["username"] + "</b> <i>" + post_dict["text"] + "</i><br><br>\n"

            if post_dict["video_unique_id"] != None:
                if is_mobile:
                    body_string += "<video width=\"90%\" height=\"240\" controls>  <source src=\"https://video.n-plat.com/?filename=video"+str(post_dict["video_unique_id"])+".mp4\" type=\"video/mp4\"></video><br>\n"
                else:    
                    body_string += "<video width=\"320\" height=\"240\" controls>  <source src=\"https://video.n-plat.com/?filename=video"+str(post_dict["video_unique_id"])+".mp4\" type=\"video/mp4\"></video><br>\n"


            if post_dict["image_unique_id"] != None:
                if is_mobile:
                    body_string += "<img style=\"max-width: 90%; max-height: 300\" src=\"https://image.n-plat.com/?filename=image"+str(post_dict["image_unique_id"])+".jpeg\"></img><br>\n"
                else:
                    body_string += "<img style=\"max-width: 300; max-height: 300\" src=\"https://image.n-plat.com/?filename=image"+str(post_dict["image_unique_id"])+".jpeg\"></img><br>\n"

            body_string += "</div>"    

        body_string += "</center>\n"

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

