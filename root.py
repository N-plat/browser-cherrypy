import MySQLdb

import cherrypy

import os

import json

from auth import Authenticate

from followers import Followers

from following import Following

from post import Post

from myposts import MyPosts

from register import Register

from feed import Feed

from follow import Follow

from singlepost import SinglePost

#from stream import Stream

#from images import Images

from cherrypy.lib import static

import html_strings

from auth import is_session_authenticated

from require import require

json_out = cherrypy.config(**{'tools.json_out.on': True})
json_in = cherrypy.config(**{'tools.json_in.on': True})

class Root(object):

    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True,
        'tools.sessions.locking': 'explicit' #this and the acquire_lock and the release_lock statements in the login and logout functions are necessary so that multiple ajax requests can be processed in parallel in a single session
    }

#    stream = Stream()

#    images = Images()    

    follow = Follow()

    following = Following()

    followers = Followers()

    myposts = MyPosts()
    
    post = Post()

    feed = Feed()

    auth = Authenticate()

    register = Register()

    singlepost = SinglePost()
    
#    @cherrypy.expose
#    def default(self,*args):
#        return static.serve_file("/home/ec2-user/server/google_verification_file.html");        

    @cherrypy.expose
    def index(self):

        gtag_string = open("gtag.js").read()

        disclaimer_string = open("disclaimer.html").read()
        
        if is_session_authenticated():
            raise cherrypy.HTTPRedirect("/feed/");

        desktop_menu_string = open("desktop_unauthenticated_menu.html").read()
        mobile_menu_string = open("mobile_unauthenticated_menu.html").read()
        
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
    
        curs.execute("select username,name,registration_time from user_info;")
    
        userinfo_fetchall = curs.fetchall()

        colnames = [desc[0] for desc in curs.description]

        body_string = "<center>\n"
        
        for userinfo in userinfo_fetchall:
            userinfo_dict=dict(zip(colnames, userinfo))        
            body_string += "<a href=\""+userinfo_dict["username"]+"\">"+userinfo_dict["username"] + " (" + userinfo_dict["name"] + ")</a><br>\n" 

        body_string += "<br>\n"
                
        curs.execute("select t1.*,(select unique_id from posts where unique_id=t1.parent_unique_id limit 1),(select text from posts where unique_id=t1.parent_unique_id limit 1),(select video_unique_id from posts where unique_id=t1.parent_unique_id limit 1),(select image_unique_id from posts where unique_id=t1.parent_unique_id limit 1),(select time from posts where unique_id=t1.parent_unique_id limit 1),(select username from posts where unique_id=t1.parent_unique_id limit 1),(select count(*) from loves where post_unique_id=t1.unique_id),(select count(*) from posts where parent_unique_id=t1.unique_id),(select count(*) from loves where post_unique_id=t1.parent_unique_id),(select count(*) from posts where parent_unique_id=t1.parent_unique_id) FROM posts as t1 order by t1.time desc;")

        colnames = [desc[0] for desc in curs.description]

        posts=curs.fetchall()

        conn.close()
            
        body_string = "<center>\n"

        for post in posts:
            post_dict = dict(zip(colnames, post))

#                datetime_string_fmt = '%Y-%m-%d %H:%M:%S.%f'
            datetime_string_fmt = '%Y-%m-%d'                

            body_string += "<div class=\"post\">\n"

            if post_dict["parent_unique_id"]:

                body_string += "<p style=\"float:left;text-align:left;position:relative;top:-20px;width:75%;\"><b>"+post_dict["(select username from posts where unique_id=t1.parent_unique_id limit 1)"] + "</b> (reposted by <b>"+post_dict["username"]+"</b>)</p>"
                body_string += "<p style=\"float:left;text-align:right;position:relative;top:-20px;width:25%;\">"+post_dict["(select time from posts where unique_id=t1.parent_unique_id limit 1)"].strftime(datetime_string_fmt)+"</p>"

                body_string += "<i>" + post_dict["(select text from posts where unique_id=t1.parent_unique_id limit 1)"] + "</i><br><br>\n"

                if post_dict["(select video_unique_id from posts where unique_id=t1.parent_unique_id limit 1)"] != None:
                    if is_mobile:
                        body_string += "<video width=\"90%\" height=\"240\" controls>  <source src=\"https://video.n-plat.com/?filename=video"+str(post_dict["(select video_unique_id from posts where unique_id=t1.parent_unique_id limit 1)"])+".mp4\" type=\"video/mp4\"></video><br>\n"
                    else:    
                        body_string += "<video width=\"320\" height=\"240\" controls>  <source src=\"https://video.n-plat.com/?filename=video"+str(post_dict["(select video_unique_id from posts where unique_id=t1.parent_unique_id limit 1)"])+".mp4\" type=\"video/mp4\"></video><br>\n"


                if post_dict["(select image_unique_id from posts where unique_id=t1.parent_unique_id limit 1)"] != None:
                    if is_mobile:
                        body_string += "<img style=\"max-width: 90%; max-height: 300\" src=\"https://image.n-plat.com/?filename=image"+str(post_dict["(select image_unique_id from posts where unique_id=t1.parent_unique_id limit 1)"])+".jpeg\"></img><br>\n"
                    else:
                        body_string += "<img style=\"max-width: 300; max-height: 300\" src=\"https://image.n-plat.com/?filename=image"+str(post_dict["(select image_unique_id from posts where unique_id=t1.parent_unique_id limit 1)"])+".jpeg\"></img><br>\n"
                            
                body_string += "<p style=\"float:left;position:relative;bottom:-20px;width:33.3333333333333333333333%;text-align:left;\"><img class=\"heart\" height=\"20\" width=\"20\" src=\"https://image.n-plat.com/?filename=heart_outline.png\"/>"+str(post_dict["(select count(*) from loves where post_unique_id=t1.parent_unique_id)"])+"</p>"
                body_string += "<p style=\"float:left;position:relative;bottom:-20px;width:33.3333333333333333333333%;text-align:center;\"><img class=\"repost\" height=\"20\" width=\"20\" src=\"https://image.n-plat.com/?filename=repost.png\"/>"+str(post_dict["(select count(*) from posts where parent_unique_id=t1.parent_unique_id)"])+"</p>"                
                body_string += "<p style=\"float:left;position:relative;bottom:-20px;width:33.3333333333333333333333%;text-align:right;\"><a href=\"https://n-plat.com/singlepost/?id="+str(+post_dict["unique_id"])+"\"><img height=\"20\" width=\"20\" src=\"https://image.n-plat.com/?filename=share.png\"/></a></p>"
            else:
                
                body_string += "<p style=\"float:left;text-align:left;position:relative;top:-20px;width:75%;\"><b>"+post_dict["username"] + "</b></p>"
                body_string += "<p style=\"float:left;text-align:right;position:relative;top:-20px;width:25%;\">"+post_dict["time"].strftime(datetime_string_fmt)+"</p>"

                body_string += "<i>" + post_dict["text"] + "</i><br><br>\n"

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

                            
                body_string += "<p style=\"float:left;position:relative;bottom:-20px;width:33.3333333333333333333333%;text-align:left;\"><img class=\"heart\" height=\"20\" width=\"20\" src=\"https://image.n-plat.com/?filename=heart_outline.png\"/>"+str(post_dict["(select count(*) from loves where post_unique_id=t1.unique_id)"])+"</p>"
                body_string += "<p style=\"float:left;position:relative;bottom:-20px;width:33.3333333333333333333333%;text-align:center;\"><img class=\"repost\" height=\"20\" width=\"20\" src=\"https://image.n-plat.com/?filename=repost.png\"/>"+str(post_dict["(select count(*) from posts where parent_unique_id=t1.unique_id)"])+"</p>"                
                body_string += "<p style=\"float:left;position:relative;bottom:-20px;width:33.3333333333333333333333%;text-align:right;\"><a href=\"https://n-plat.com/singlepost/?id="+str(+post_dict["unique_id"])+"\"><img height=\"20\" width=\"20\" src=\"https://image.n-plat.com/?filename=share.png\"/></a></p>"

            body_string += "</div>"

        body_string += "</center>\n"

        desktop_html_string = open("desktop.html").read()
            
        desktop_html_string = desktop_html_string.format(
            a=gtag_string,
            b="",
            c=desktop_menu_string,
            d=body_string,
            e=disclaimer_string)

        mobile_html_string = open("mobile.html").read()
            
        mobile_html_string=mobile_html_string.format(
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

    @cherrypy.expose
    def default(self, user):

        gtag_string = open("gtag.js").read()

        disclaimer_string = open("disclaimer.html").read()
        
        if is_session_authenticated():
            desktop_menu_string = open("desktop_authenticated_menu.html").read()
            mobile_menu_string = open("mobile_authenticated_menu.html").read()
        else:
            desktop_menu_string = open("desktop_unauthenticated_menu.html").read()
            mobile_menu_string = open("mobile_unauthenticated_menu.html").read()
        
        is_mobile = False

        if "User-Agent" in cherrypy.request.headers and ("Android" in cherrypy.request.headers['User-Agent'] or "iPhone" in cherrypy.request.headers['User-Agent'] or "iPad" in cherrypy.request.headers['User-Agent']):
            is_mobile = True

        valid_username = True    
            
        for c in user:
            if c != 'a' and c != 'b' and c != 'c' and c != 'd' and c != 'e' and c != 'f' and c != 'g' and c != 'h' and c != 'i' and c != 'j' and c != 'k' and c != 'l' and c != 'm' and c != 'n' and c != 'o' and c != 'p' and c != 'q' and c != 'r' and c != 's' and c != 't' and c != 'u' and c != 'v' and c != 'w' and c != 'x' and c != 'y' and c != 'z' and c != 'A' and c != 'B' and c != 'C' and c != 'D' and c != 'E' and c != 'F' and c != 'G' and c != 'H' and c != 'I' and c != 'J' and c != 'K' and c != 'L' and c != 'M' and c != 'N' and c != 'O' and c != 'P' and c != 'Q' and c != 'R' and c != 'S' and c != 'T' and c != 'U' and c != 'V' and c != 'W' and c != 'X' and c != 'Y' and c != 'Z' and c != '0' and c != '1' and c != '2' and c != '3' and c != '4' and c != '5' and c != '6' and c != '7' and c != '8' and c != '9' and c != '_' and c != '-' and c != '.':
                valid_username = False

        if not valid_username:
            body_string = "<center>Invalid username</center>"
        else:    
            secrets_file=open("/home/ec2-user/secrets.txt")

            passwords=secrets_file.read().rstrip('\n')
            
            db_password = passwords.split('\n')[0]
            
            dbname = "nplat"
            
            conn = MySQLdb.connect(host='nplat-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)
            
            curs = conn.cursor()
    
            curs.execute("use "+dbname+";")
       
            curs.execute("select * from user_info where username=\""+user+"\";")

            userinfo_fetchall = curs.fetchall()
        
            if len(userinfo_fetchall):
                assert(len(userinfo_fetchall) == 1)
                colnames = [desc[0] for desc in curs.description]
                name_string = "<center>\n"
                for userinfo in userinfo_fetchall:
                    userinfo_dict=dict(zip(colnames, userinfo))        
                    name_string += "<h2>" + userinfo_dict["name"] + "</h2>\n<br>\n" 
                name_string += "</center>\n"

                curs.execute("select t1.*,(select unique_id from posts where unique_id=t1.parent_unique_id limit 1),(select text from posts where unique_id=t1.parent_unique_id limit 1),(select video_unique_id from posts where unique_id=t1.parent_unique_id limit 1),(select image_unique_id from posts where unique_id=t1.parent_unique_id limit 1),(select time from posts where unique_id=t1.parent_unique_id limit 1),(select username from posts where unique_id=t1.parent_unique_id limit 1),(select count(*) from loves where post_unique_id=t1.unique_id),(select count(*) from posts where parent_unique_id=t1.unique_id),(select count(*) from loves where post_unique_id=t1.parent_unique_id),(select count(*) from posts where parent_unique_id=t1.parent_unique_id) FROM posts as t1 WHERE t1.username=\""+user+"\" ORDER by t1.time desc;")

                colnames = [desc[0] for desc in curs.description]

                posts=curs.fetchall()

                if len(posts) != 0:
                    body_string = "<center>\n"
                    for post in posts:
                        post_dict = dict(zip(colnames, post))

                        datetime_string_fmt = '%Y-%m-%d'                

                        body_string += "<div class=\"post\">\n"

                        if post_dict["parent_unique_id"]:

                            body_string += "<p style=\"float:left;text-align:left;position:relative;top:-20px;width:75%;\"><b>"+post_dict["(select username from posts where unique_id=t1.parent_unique_id limit 1)"] + "</b> (reposted by <b>"+post_dict["username"]+"</b>)</p>"
                            body_string += "<p style=\"float:left;text-align:right;position:relative;top:-20px;width:25%;\">"+post_dict["(select time from posts where unique_id=t1.parent_unique_id limit 1)"].strftime(datetime_string_fmt)+"</p>"

                            body_string += "<i>" + post_dict["(select text from posts where unique_id=t1.parent_unique_id limit 1)"] + "</i><br><br>\n"

                            if post_dict["(select video_unique_id from posts where unique_id=t1.parent_unique_id limit 1)"] != None:
                                if is_mobile:
                                    body_string += "<video width=\"90%\" height=\"240\" controls>  <source src=\"https://video.n-plat.com/?filename=video"+str(post_dict["(select video_unique_id from posts where unique_id=t1.parent_unique_id limit 1)"])+".mp4\" type=\"video/mp4\"></video><br>\n"
                                else:    
                                    body_string += "<video width=\"320\" height=\"240\" controls>  <source src=\"https://video.n-plat.com/?filename=video"+str(post_dict["(select video_unique_id from posts where unique_id=t1.parent_unique_id limit 1)"])+".mp4\" type=\"video/mp4\"></video><br>\n"

                            if post_dict["(select image_unique_id from posts where unique_id=t1.parent_unique_id limit 1)"] != None:
                                if is_mobile:
                                    body_string += "<img style=\"max-width: 90%; max-height: 300\" src=\"https://image.n-plat.com/?filename=image"+str(post_dict["(select image_unique_id from posts where unique_id=t1.parent_unique_id limit 1)"])+".jpeg\"></img><br>\n"
                                else:
                                    body_string += "<img style=\"max-width: 300; max-height: 300\" src=\"https://image.n-plat.com/?filename=image"+str(post_dict["(select image_unique_id from posts where unique_id=t1.parent_unique_id limit 1)"])+".jpeg\"></img><br>\n"
                            
                            body_string += "<p style=\"float:left;position:relative;bottom:-20px;width:33.3333333333333333333333%;text-align:left;\"><img class=\"heart\" height=\"20\" width=\"20\" src=\"https://image.n-plat.com/?filename=heart_outline.png\"/>"+str(post_dict["(select count(*) from loves where post_unique_id=t1.parent_unique_id)"])+"</p>"
                            body_string += "<p style=\"float:left;position:relative;bottom:-20px;width:33.3333333333333333333333%;text-align:center;\"><img class=\"repost\" height=\"20\" width=\"20\" src=\"https://image.n-plat.com/?filename=repost.png\"/>"+str(post_dict["(select count(*) from posts where parent_unique_id=t1.parent_unique_id)"])+"</p>"                
                            body_string += "<p style=\"float:left;position:relative;bottom:-20px;width:33.3333333333333333333333%;text-align:right;\"><a href=\"https://n-plat.com/singlepost/?id="+str(+post_dict["unique_id"])+"\"><img height=\"20\" width=\"20\" src=\"https://image.n-plat.com/?filename=share.png\"/></a></p>"
                        else:
                
                            body_string += "<p style=\"float:left;text-align:left;position:relative;top:-20px;width:75%;\"><b>"+post_dict["username"] + "</b></p>"
                            body_string += "<p style=\"float:left;text-align:right;position:relative;top:-20px;width:25%;\">"+post_dict["time"].strftime(datetime_string_fmt)+"</p>"

                            body_string += "<i>" + post_dict["text"] + "</i><br><br>\n"

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
                            
                            body_string += "<p style=\"float:left;position:relative;bottom:-20px;width:33.3333333333333333333333%;text-align:left;\"><img class=\"heart\" height=\"20\" width=\"20\" src=\"https://image.n-plat.com/?filename=heart_outline.png\"/>"+str(post_dict["(select count(*) from loves where post_unique_id=t1.unique_id)"])+"</p>"
                            body_string += "<p style=\"float:left;position:relative;bottom:-20px;width:33.3333333333333333333333%;text-align:center;\"><img class=\"repost\" height=\"20\" width=\"20\" src=\"https://image.n-plat.com/?filename=repost.png\"/>"+str(post_dict["(select count(*) from posts where parent_unique_id=t1.unique_id)"])+"</p>"                
                            body_string += "<p style=\"float:left;position:relative;bottom:-20px;width:33.3333333333333333333333%;text-align:right;\"><a href=\"https://n-plat.com/singlepost/?id="+str(+post_dict["unique_id"])+"\"><img height=\"20\" width=\"20\" src=\"https://image.n-plat.com/?filename=share.png\"/></a></p>"

                        body_string += "</div>"

                        body_string += """

<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script>
<script type="text/javascript"> 
$('img.heart').click(function(event) {
   event.preventDefault();
   request_json_object = {"post_id" : event.target.parentNode.parentNode.lastChild.firstChild.href.split('=')[1]}
   $.ajax({
      url: '/love',
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(request_json_object),
//      data: '',
      success: function(data){
         response_json_object = JSON.parse(data)
         if (json_object["success"]) {

         }
         else {

         }
      },
      error : function (data) {

      }
   });
});
$('img.repost').click(function(event) {
   event.preventDefault();
   request_json_object = {"post_id" : event.target.parentNode.parentNode.lastChild.firstChild.href.split('=')[1]}
   $.ajax({
      url: '/repost',
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(request_json_object),
      success: function(data){
         response_json_object = JSON.parse(data)
         if (json_object["success"]) {

         }
         else {

         }
      },
      error : function (data) {

      }
   });
});
</script>

"""
        

                        
                else:
                    body_string="<center><i>"+user+" has not posted anything yet</i></center>"

            else:
                body_string = "<center>Username not found</center>"
                
        desktop_html_string = open("desktop.html").read()
                
        desktop_html_string = desktop_html_string.format(
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


    @cherrypy.expose
    @require()
    @json_in
    def repost(self):

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

        curs.execute('insert into posts set username="'+cherrypy.session.get('_cp_username')+'", parent_unique_id="'+str(post_id)+'", time=now(6);')

        conn.commit()

    @cherrypy.expose
    @require()
    @json_in
    def love(self):

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

        curs.execute('insert into loves set username="'+cherrypy.session.get('_cp_username')+'", post_unique_id="'+post_id+'", time = now(6);')

        conn.commit()
