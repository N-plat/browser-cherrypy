import MySQLdb
import cherrypy

#from view import View

#from chat import Chat

from auth import Authenticate

from register import Register

#from about import About

#from emails import Email

#from compose import Compose

from cherrypy.lib import static

import html_strings

from auth import is_session_authenticated

class Root(object):

    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True,
        'tools.sessions.locking': 'explicit' #this and the acquire_lock and the release_lock statements in the login and logout functions are necessary so that multiple ajax requests can be processed in parallel in a single session
    }

#    view = View()

#    chat = Chat()

    auth = Authenticate()

#    loginlogout = Register()

    register = Register()

#    about = About()

#    email = Email()

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
                body_string += "<b>" + post_dict["username"] + "</b> <i>" + post_dict["text"] + "</i><br>\n"

            body_string += "<center>\n"
            
            desktop_html_string = open("desktop.html").read()
            
            desktop_html_string = desktop_html_string.format(
                a=gtag_string,
                b=desktop_menu_string,
                c=body_string,
                d=disclaimer_string)

            mobile_html_string = open("mobile.html").read()
            
            mobile_html_string=mobile_html_string.format(
                a=gtag_string,
                b=mobile_menu_string,
                c=body_string,
                d=disclaimer_string)
            
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
            <form id="post_form" method="post" action="post">
            <input type="text" id="text" name="text"/> <br><br>
            <button id="contact_request" class="fg-button ui-state-default ui-corner-all" type="submit">
            Submit
            </button>
            </form>
            </center>"""
        
            body_string += "<center>\n"
            
            for post in posts:
                post_dict = dict(zip(colnames, post))
                body_string += "<b>" + post_dict["username"] + "</b> <i>" + post_dict["text"] + "</i><br>\n"

            body_string += "<center>\n"
            
            desktop_html_string = open("desktop.html").read()
            
            desktop_html_string=desktop_html_string.format(
                a=gtag_string,
                b=desktop_menu_string,
                c=body_string,
                d=disclaimer_string)

            mobile_html_string = open("mobile.html").read()
            
            mobile_html_string = mobile_html_string.format(
                a=gtag_string,
                b=mobile_menu_string,
                c=body_string,
                d=disclaimer_string)
            
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
            b=desktop_menu_string,
            c=body_string,
            d=disclaimer_string)

        mobile_html_string = open("mobile.html").read()
            
        mobile_html_string = mobile_html_string.format(
            a=gtag_string,
            b=mobile_menu_string,
            c=body_string,
            d=disclaimer_string)
            
        if is_mobile:
            html_string = mobile_html_string
        else:
            html_string = desktop_html_string 
            
        return html_string

    @cherrypy.expose
    def post(self, text):

        print text
        
        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "nplat"

        conn = MySQLdb.connect(host='nplat-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")
        
        curs.execute("insert into posts set username = \""+cherrypy.session.get('_cp_username')+"\", text = \""+text.replace('"','\\\"').replace("'","\\\'")+"\", time=now(6)")

        conn.commit()

        conn.close()
