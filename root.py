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

        gtag = open("gtag.js").read()
        
        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]
        
        dbname = "nplat"

        conn = MySQLdb.connect(host='nplat-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)
        
        curs = conn.cursor()
        
        curs.execute("use "+dbname+";")
    
        curs.execute("select username,name,registration_time from user_info;")
    
        userinfo_fetchall = curs.fetchall()

        colnames = [desc[0] for desc in curs.description]

        users_string = "<center>\n"
        
        for userinfo in userinfo_fetchall:
            userinfo_dict=dict(zip(colnames, userinfo))        
            users_string += "<a href=\""+userinfo_dict["username"]+"\">"+userinfo_dict["username"] + " (" + userinfo_dict["name"] + ")</a><br>\n" 

        users_string += "</center>\n"

        if is_session_authenticated():
            curs.execute("select * from posts where username = \""+cherrypy.session.get('_cp_username')+"\" order by time desc;")
        else:
            curs.execute("select * from posts order by time desc;")            

        colnames = [desc[0] for desc in curs.description]

        posts=curs.fetchall()
        
        conn.close()

        posts_string = "<center>\n"
            
        for post in posts:
            post_dict = dict(zip(colnames, post))
            posts_string += "<b>" + post_dict["username"] + "</b> <i>" + post_dict["text"] + "</i><br>\n"

        posts_string += "<center>\n"
            
        is_mobile = False

        if "User-Agent" in cherrypy.request.headers and ("Android" in cherrypy.request.headers['User-Agent'] or "iPhone" in cherrypy.request.headers['User-Agent'] or "iPad" in cherrypy.request.headers['User-Agent']):
            is_mobile = True

        if not is_session_authenticated():
            
            if is_mobile:

                html_string = """
<html>
<head>
{0}
</head>
<body>
<center><h1>A Neutral Platform </h1></center>
<center><h2>A social media platform that does not censor</h2></center>
{1}
<br>
{2}
<br>
<center>This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact nplat.feedback@gmail.com for comments, feature requests, etc.</center>
</body>
</html>
""".format(gtag,users_string,posts_string)
            
            else:    

                html_string = """
<html>
<head>
{0}
<meta name="google-site-verification" content="E6TUNugyrurnOh1poUxBpXfMFPwITmtF8gcpgZxZXFM" />

<style>
h1{{
margin-top: 0.0em; 
margin-bottom: 0.0em; 
}} 

h3{{
margin-top: 0.0em; 
}} 

.header1 {{width:380px; float:left;}}

.nav{{
float: right;
padding: 20px 0px 0px 0px;
text-align: right;
}}

header{{ background-color: White}}

header{{
position:fixed;
top:0px;
left:0px;
width:100%;
height:60px;
z-index:50;
}}

.page{{
width:960px; 
margin:0px auto 0px auto;
}}
</style>

</head>
<body>
<header>
<div class = "page">
<div class="header1">
<h1> N-plat </h1>
<h3>A neutral platform</h3>
</div>
<div class="nav">
<a href="/">Home</a> / <a href="/auth/login">Login</a> / <a href="/register/">Register</a>
</div>
</div>
</header>
<div class="nonheader">
<div class="divider"></div>
<br><br><br>
<center><h1>A social media platform that does not censor</h1></center>
<br>
{1}
<br>
{2}
<br>
<center>This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact nplat.feedback@gmail.com for comments, feature requests, etc.</center>
</div>
</body>
</html>
""".format(gtag,users_string,posts_string)

        else:

            if is_mobile:
                html_string = """
<html>
<head>
{0}
</head>
<body>
<center><h1>A Neutral Platform </h1></center>
{0}
<br>
{1}
<br>
<center>This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact nplat.feedback@gmail.com for comments, feature requests, etc.</center>
</body>
</html>
""".format(gtag,posts_string)
                
            else:
                html_string = """
<html>
<head>
{0}
</head>
<body>
<center><h1>A Neutral Platform </h1></center>
<center>
<form id="post_form" method="post" action="post">
<input type="text" id="text" name="text"/> <br><br>
<button id="contact_request" class="fg-button ui-state-default ui-corner-all" type="submit">
Submit
</button>
</form>
</center>
{0}
<br>
<center>This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact nplat.feedback@gmail.com for comments, feature requests, etc.</center>
</body>
</html>
""".format(gtag,posts_string)
                
        return html_string

    @cherrypy.expose
    def default(self, user):

        gtag = open("gtag.js").read()
        
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

            html_string = """
<html>
<head>
{0}
</head>
<body>
<center><h1>A Neutral Platform</h1></center>
<center>This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact nplat.feedback@gmail.com for comments, feature requests, etc.</center>
</body>
</html>
""".format(gtag)
            
        else:    
            html_string = """
<html>
<head>
{0}
</head>
<body>
<center><h1>A Neutral Platform</h1></center>
<center>Username not found</center>
<br><br>
<center>This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact nplat.feedback@gmail.com for comments, feature requests, etc.</center>
</body>
</html>
""".format(gtag)

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
