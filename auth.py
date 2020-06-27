import MySQLdb

import hashlib

import cherrypy

#import html_strings

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

        gtag = open("gtag.js").read()
        
        from_page = from_page.replace(chr(1),"&&").replace(chr(0),"%22")

        is_mobile = False

        if "User-Agent" in cherrypy.request.headers and ("Android" in cherrypy.request.headers['User-Agent'] or "iPhone" in cherrypy.request.headers['User-Agent'] or "iPad" in cherrypy.request.headers['User-Agent']):
            is_mobile = True

        if is_mobile:

            html_string = """
<html>
<head>
{0}
</head>
<body>
<center><h1>A Neutral Platform</h1></center>
<center>
<div style = "font-size:120%">Register <a href="/register/">here</a> before logging in.</div><br>
<form method="post" action="/auth/login">
<input type="hidden" name="from_page" value="{1}" />
<div style = "font-size:120%">username:</div><br>
<input type="text" id="username" name="username" size="18" /><br><br>
<div style = "font-size:120%">password:</div> <br>
<input type="password" id="password" name="password" size="18" /> <br><br>
<button type="submit">
Login"
</button>"
<br><br>
{2}
</center>
<br>
<center>This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact nplat.feedback@gmail.com for comments, feature requests, etc.</center>
</body>
</html>
""".format(gtag,from_page,str(message))

        else:
            html_string = """
<html>
<head>
{0}
</head>
<center><h1>A Neutral Platform</h1></center>
<center>Register <a href="/register/">here</a> before logging in.</center><br><br>
<center>
<form method="post" action="/auth/login">
<input type="hidden" name="from_page" value="{1}" />
username: <br><br>
<input type="text" id="username" name="username" size="18" /><br><br>
password: <br><br>
<input type="password" id="password" name="password" size="18" /> <br><br>
<button type="submit">
Login
</button>
</center
<br><br>
<center>{2}</center>
<br>
<center>This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact nplat.feedback@gmail.com for comments, feature requests, etc.</center>
</body>
</html>
""".format(gtag,from_page,str(message))
            
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
