import MySQLdb

import cherrypy

import os

import json

from cherrypy.lib import static

from require import require

class Post(object):

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
    def post(self, text, video, image):

        cherrypy.session.get('_cp_username')
        
        assert(len(image.filename) == 0 or len(video.filename) == 0)
        
        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "nplat"

        json_object = {}

        json_object["success"] = True

        json_object["errors"] = []

        if len(text) == 0 and len(image.filename) == 0 and len(video.filename) == 0:
            json_object["success"] = False
            json_object["errors"].append("No content.")
            print json.dumps(json_object)
            return json.dumps(json_object)    
        
        if len(image.filename) > 0:

            tmp_filename=os.popen("mktemp").read().rstrip('\n')
            open(tmp_filename,'wb').write(image.file.read());

            output=os.popen("clamscan  --stdout --quiet "+tmp_filename+" 2>&1").read()

            if len(output) > 0:
                return
            
            conn = MySQLdb.connect(host='nplat-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)
        
            curs = conn.cursor()
            curs.execute("use "+str(dbname)+";")
            curs.execute("insert into images values(NULL,%s,now(6),now(6))", [cherrypy.session.get('_cp_username')])
            conn.commit()
        
            curs.execute("SELECT LAST_INSERT_ID()")
            conn.commit()

            image_unique_id = str(curs.fetchall()[0][0])

            os.system("mv "+tmp_filename+" /efs/ec2-user/images/image"+image_unique_id+".jpeg")
            
            conn = MySQLdb.connect(host='nplat-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

            curs = conn.cursor()

            curs.execute("use "+dbname+";")

            curs.execute("insert into posts set username = \""+cherrypy.session.get('_cp_username')+"\", text = \""+text.replace('"','\\\"').replace("'","\\\'")+"\", time=now(6), image_unique_id = "+image_unique_id)

            conn.commit()

            conn.close()

        elif len(video.filename) > 0:

            tmp_filename=os.popen("mktemp").read().rstrip('\n')
            open(tmp_filename,'wb').write(video.file.read());

            output=os.popen("clamscan  --stdout --quiet "+tmp_filename+" 2>&1").read()

            if len(output) > 0:
                return

            conn = MySQLdb.connect(host='nplat-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)
        
            curs = conn.cursor()
            curs.execute("use "+str(dbname)+";")

            curs.execute("insert into videos values(NULL,%s,now(6),now(6))", [cherrypy.session.get('_cp_username')])
            conn.commit()
        
            curs.execute("SELECT LAST_INSERT_ID()")
            conn.commit()

            video_unique_id = str(curs.fetchall()[0][0])

            os.system("mv "+tmp_filename+" /efs/ec2-user/videos/video"+video_unique_id+".mp4")
            
            conn = MySQLdb.connect(host='nplat-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

            curs = conn.cursor()

            curs.execute("use "+dbname+";")

            curs.execute("insert into posts set username = \""+cherrypy.session.get('_cp_username')+"\", text = \""+text.replace('"','\\\"').replace("'","\\\'")+"\", time=now(6), video_unique_id = "+video_unique_id)

            conn.commit()

            conn.close()

        else:

            conn = MySQLdb.connect(host='nplat-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

            curs = conn.cursor()

            curs.execute("use "+dbname+";")

            curs.execute("insert into posts set username = \""+cherrypy.session.get('_cp_username')+"\", text = \""+text.replace('"','\\\"').replace("'","\\\'")+"\", time=now(6)")

            conn.commit()

            conn.close()

            
        print json.dumps(json_object)
        return json.dumps(json_object)    
            
