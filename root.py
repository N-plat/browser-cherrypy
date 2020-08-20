import MySQLdb

import cherrypy

import os

import json

from auth import Authenticate

from followers import Followers

from following import Following

from post import Post

from register import Register

#from stream import Stream

#from images import Images

from cherrypy.lib import static

import html_strings

from auth import is_session_authenticated

class Root(object):

    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True,
        'tools.sessions.locking': 'explicit' #this and the acquire_lock and the release_lock statements in the login and logout functions are necessary so that multiple ajax requests can be processed in parallel in a single session
    }

#    stream = Stream()

#    images = Images()    

    following = Following()

    followers = Followers()

    post = Post()

    auth = Authenticate()

    register = Register()

#    @cherrypy.expose
#    def default(self,*args):
#        return static.serve_file("/home/ec2-user/server/google_verification_file.html");        

    @cherrypy.expose
    def index(self):

        gtag_string = open("gtag.js").read()

        disclaimer_string = open("disclaimer.html").read()
        
        if is_session_authenticated():
            desktop_menu_string = open("desktop_authenticated_menu.html").read()
            mobile_menu_string = open("mobile_authenticated_menu.html").read()
        else:
            desktop_menu_string = open("desktop_unauthenticated_menu.html").read()
            mobile_menu_string = open("mobile_unauthenticated_menu.html").read()
        
        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]
        
        dbname = "nplat"

        is_mobile = False

        if "User-Agent" in cherrypy.request.headers and ("Android" in cherrypy.request.headers['User-Agent'] or "iPhone" in cherrypy.request.headers['User-Agent'] or "iPad" in cherrypy.request.headers['User-Agent']):
            is_mobile = True
            
        if not is_session_authenticated():

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
                
            curs.execute("select * from posts order by time desc;")            

            colnames = [desc[0] for desc in curs.description]

            posts=curs.fetchall()
        
            conn.close()
            
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

            body_string += "<center>\n"
            
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

        else:

            conn = MySQLdb.connect(host='nplat-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)
            
            curs = conn.cursor()
        
            curs.execute("use "+dbname+";")
            
            curs.execute("select * from posts where username = \""+cherrypy.session.get('_cp_username')+"\" order by time desc;")

            colnames = [desc[0] for desc in curs.description]

            posts=curs.fetchall()
        
            conn.close()
            
            body_string = """<center>
            <form target="console_iframe" id="post_form" method="post" action="post" enctype="multipart/form-data">
            <input type="file" id="video" name="video"/>
            <br><br>
            <input type="file" id="image" name="image"/>
            <br><br>
            <input type="text" id="text" name="text"/> <br><br>
            <button id="contact_request" class="fg-button ui-state-default ui-corner-all" type="submit">
            Submit
            </button>
            </form>
            <iframe name="console_iframe" id ="console_iframe" class="terminal" /></iframe>
            </center>"""
        
            body_string += "<center>\n"
            
            for post in posts:
                post_dict = dict(zip(colnames, post))
                body_string += "<b>" + post_dict["username"] + "</b> <i>" + post_dict["text"] + "</i><br>\n"

            body_string += "</center>\n"

            body_string += """
<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script>
<script type="text/javascript">

$('#post_form').submit(function(event) {
   event.preventDefault();
   var $this = $(this);
   var formdata = new FormData($(this)[0]);         
   $.ajax({
      url: $this.attr('action'),
      type: 'POST',
      data: formdata,
      processData: false,
      contentType: false,
      success: function(data){
        json_object = JSON.parse(data)
        if (json_object["success"]) {
            var console_iframe = document.getElementById('console_iframe');
            console_iframe.contentWindow.document.open();
            console_iframe.contentWindow.document.close();
//            $('#register_form').hide();
            console_iframe.contentWindow.document.write('<head><base target="_parent"></head><center style="color:blue;font-size:20px;font-weight:bold">Post was successful.</center>');
        }
        else {
            var console_iframe = document.getElementById('console_iframe');
            console_iframe.contentWindow.document.open();
            console_iframe.contentWindow.document.close();
            console_iframe.contentWindow.document.write('<center style="color:red;font-size:20px;font-weight:bold;white-space:pre-wrap">'+json_object["errors"]+'</center>');
        }
      },
      error : function (data) {
        var console_iframe = document.getElementById('console_iframe');
        console_iframe.write("Error.");
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

                curs.execute("select * from posts where username = \""+user+"\" order by time desc;")
                colnames = [desc[0] for desc in curs.description]
                posts=curs.fetchall()

                if len(posts) != 0:
                    body_string = "<center>\n"
                    for post in posts:
                        post_dict = dict(zip(colnames, post))
                        body_string += "<b>" + post_dict["username"] + "</b> <i>" + post_dict["text"] + "</i><br>\n"
                    body_string += "<center>\n"
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
