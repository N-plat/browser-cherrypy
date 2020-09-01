import MySQLdb

import cherrypy

import os

import json

from cherrypy.lib import static

from require import require

class Follow(object):

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
            
        body_string = """<center>
        <form target="console_iframe" id="follow_form" method="post" action="follow" enctype="multipart/form-data">
        <input type="text" id="username" name="username"/> <br><br>
        <button id="contact_request" class="fg-button ui-state-default ui-corner-all" type="submit">
        Submit
        </button>
        </form>
        <iframe name="console_iframe" id ="console_iframe" class="terminal" /></iframe>
        </center>"""
        
        body_string += """
<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script>
<script type="text/javascript">

$('#follow_form').submit(function(event) {
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
            console_iframe.contentWindow.document.write('<head><base target="_parent"></head><center style="color:blue;font-size:20px;font-weight:bold">Follow was successful.</center>');
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
    @require()
    def follow(self, username):

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

        if cherrypy.session.get('_cp_username') == username:
            json_object["success"] = False
            json_object["errors"].append("You cannot follow yourself.")
            print json.dumps(json_object)
            return json.dumps(json_object)            
        
        curs.execute("select * from follows where follower = \""+cherrypy.session.get('_cp_username')+"\" and followed = \""+username+"\"")

        if len(curs.fetchall()) > 0:
            json_object["success"] = False
            json_object["errors"].append("You are already following this user.")
            print json.dumps(json_object)
            return json.dumps(json_object)
        
        curs.execute("select * from user_info where username = \""+username+"\"")

        if len(curs.fetchall()) == 0:
            json_object["success"] = False
            json_object["errors"].append("Username does not exist.")
            print json.dumps(json_object)
            return json.dumps(json_object)
        
        curs.execute("insert into follows set follower=\""+cherrypy.session.get('_cp_username')+"\", followed=\""+username+"\", time = now(6)")

        conn.commit()

        conn.close()
        
        print json.dumps(json_object)
        return json.dumps(json_object)        
