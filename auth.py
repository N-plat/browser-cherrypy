import MySQLdb

import hashlib

import cherrypy

def is_session_authenticated(*args, **kwargs):

    username = cherrypy.session.get('_cp_username')
    if username:
        return True
    else:
        return False

def is_right_password(username, password):

    secrets_file=open("/home/ec2-user/secrets.txt")

    passwords=secrets_file.read().rstrip('\n')

    db_password = passwords.split('\n')[0]

    dbname = "nplat"

    conn = MySQLdb.connect(host='nplat-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

    curs = conn.cursor()

    curs.execute("use "+dbname+";")

    curs.execute("select * from user_info where username = \""+username+"\";")

    colnames = [desc[0] for desc in curs.description]

    user_infos=curs.fetchall()

    if len(user_infos) == 0:
        return [False,"Login failed. The username that you entered was not found."]
    else:
        assert(len(user_infos) == 1)

    user_info=user_infos[0]

    user_info_dict=dict(zip(colnames, user_info))

    hashed_password = user_info_dict["hashed_password"]

    h = hashlib.sha256()

    h.update(password)

    conn.close()

    if h.hexdigest() == hashed_password:
        return [True,""]
    else:
        return [False,"Login failed. The password that you entered is not the one associated with the username that you entered."]

class Authenticate(object):

    def login_html(self,  message="", from_page="/"):

        gtag_string = open("gtag.js").read()

        disclaimer_string = open("disclaimer.html").read()

        if is_session_authenticated():
            desktop_menu_string = open("desktop_authenticated_menu.html").read()
            mobile_menu_string = open("mobile_authenticated_menu.html").read()
        else:
            desktop_menu_string = open("desktop_unauthenticated_menu.html").read()
            mobile_menu_string = open("mobile_unauthenticated_menu.html").read()
        
        from_page = from_page.replace(chr(1),"&&").replace(chr(0),"%22")

        is_mobile = False

        if "User-Agent" in cherrypy.request.headers and ("Android" in cherrypy.request.headers['User-Agent'] or "iPhone" in cherrypy.request.headers['User-Agent'] or "iPad" in cherrypy.request.headers['User-Agent']):
            is_mobile = True

        desktop_html_string = """
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
{1}
</div>
</div>
</header>
<div class="nonheader">
<div class="divider"></div>
<br><br><br>
<center><h2>Login</h2></center>
<center>Register <a href="/register/">here</a> before logging in.</center><br><br>
<center>
<form method="post" action="/auth/login">
<input type="hidden" name="from_page" value="{2}" />
username: <br><br>
<input type="text" id="username" name="username" size="18" /><br><br>
password: <br><br>
<input type="password" id="password" name="password" size="18" /> <br><br>
<button type="submit">
Login
</button>
</center
<br><br>
<center>{3}</center>
<br>
<center>{4}</center>
</body>
</html>
""".format(gtag_string,desktop_menu_string,from_page,str(message),disclaimer_string)

        mobile_html_string = """
<html>
<head>
{0}
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
nav {{
    width: 250px;
    height: 100%;
    position: fixed;
    transform: translate(-250px, 0);
    transition: transform 0.3s ease;
}}
nav.open {{
    transform: translate(0, 0);
}}
a#menu svg {{
    width: 40px;
    fill: #000;
}}
main {{
    width: 100%;
    height: 100%;
}}
html, body {{
    height: 100%;
    width: 100%;
    margin-top:0;
    margin-left:0;
    margin-right:0;
}}
.header {{
float : right
}}
.content {{
padding-left:1em;
padding-right:1em;
}}
</style>
</head>
<body>
<nav id="drawer" style="background-color:LightGrey">
<center><h2 style="margin-top:0">N-plat</h2></center>
{1}
</nav>
<main>
<a id="menu">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
    <path d="M2 6h20v3H2zm0 5h20v3H2zm0 5h20v3H2z" />
  </svg>
</a>
<div class = "header">
<h1 style="margin-top:0;margin-bottom:0">N-plat</h1>
</div>
<center><h1>A Neutral Platform</h1></center>
<center>
<div style = "font-size:120%">Register <a href="/register/">here</a> before logging in.</div><br>
<form method="post" action="/auth/login">
<input type="hidden" name="from_page" value="{2}" />
<div style = "font-size:120%">username:</div><br>
<input type="text" id="username" name="username" size="18" /><br><br>
<div style = "font-size:120%">password:</div> <br>
<input type="password" id="password" name="password" size="18" /> <br><br>
<button type="submit">
Login
</button>
<br><br>
{3}
</center>
<br>
<center>{4}</center>
</main>
<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script>
<script type="text/javascript">
var menu = document.querySelector('#menu');
var main = document.querySelector('main');
var drawer = document.querySelector('#drawer');
menu.addEventListener('click', function(e) {{
    drawer.classList.toggle('open');
    e.stopPropagation();
}});
main.addEventListener('click', function() {{
    drawer.classList.remove('open');
}});
main.addEventListener('touchstart', function() {{
    drawer.classList.remove('open');
}});
</script>
</body>
</html>
""".format(gtag_string,mobile_menu_string,from_page,str(message),disclaimer_string)

        if is_mobile:
            html_string = mobile_html_string
        else:
            html_string = desktop_html_string
            
        return html_string    
        
    @cherrypy.expose
    def login(self, username=None, password=None, from_page="/"):

        from_page = from_page.strip('"')

        if username is None or password is None:
            print "username or password is none"
            return self.login_html(from_page=from_page)

        print "username: " + str(username)

        print "len(password): " + str(len(password))
        
        [pass_password_check,error_msg] = is_right_password(username, password)
        if not pass_password_check:
            print "fails password check"
            return self.login_html(error_msg, from_page)
        else:

            print "successful login"

            cherrypy.request.login = username

            cherrypy.session.acquire_lock()

            cherrypy.session['_cp_username'] = username

            cherrypy.session.release_lock()

            from_page = from_page.strip('"')
            
            raise cherrypy.HTTPRedirect(from_page)
    
    @cherrypy.expose
    def logout(self, from_page="/"):

        cherrypy.session.acquire_lock()

        cherrypy.session['_cp_username'] = None

        cherrypy.session.release_lock()

        cherrypy.request.login = None
        raise cherrypy.HTTPRedirect(from_page)
            
