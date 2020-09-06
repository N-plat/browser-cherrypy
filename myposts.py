import MySQLdb

import cherrypy

import os

import json

from cherrypy.lib import static

from require import require

json_out = cherrypy.config(**{'tools.json_out.on': True})
json_in = cherrypy.config(**{'tools.json_in.on': True})

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
            
        curs.execute("select t1.*,(select unique_id from posts where unique_id=t1.parent_unique_id limit 1),(select text from posts where unique_id=t1.parent_unique_id limit 1),(select video_unique_id from posts where unique_id=t1.parent_unique_id limit 1),(select image_unique_id from posts where unique_id=t1.parent_unique_id limit 1),(select time from posts where unique_id=t1.parent_unique_id limit 1),(select username from posts where unique_id=t1.parent_unique_id limit 1),(select count(*) from loves where post_unique_id=t1.unique_id),(select count(*) from posts where parent_unique_id=t1.unique_id),(select count(*) from loves where post_unique_id=t1.parent_unique_id),(select count(*) from posts where parent_unique_id=t1.parent_unique_id) FROM posts as t1 WHERE t1.username= \""+cherrypy.session.get('_cp_username')+"\" ORDER by t1.time desc;")

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

        body_string += """

<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script>
<script type="text/javascript"> 
$('img.heart').click(function(event) {
   event.preventDefault();
   request_json_object = {"post_id" : event.target.parentNode.parentNode.lastChild.firstChild.href.split('=')[1]}
   $.ajax({
      url: 'love',
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
      url: 'repost',
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
