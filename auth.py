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

        body_string = """
<center><h2>Login</h2></center>
<center>Register <a href="/register/">here</a> before logging in.</center><br><br>
<center>
<form method="post" action="/auth/login">
<input type="hidden" name="from_page" value="{0}" />
username: <br><br>
<input type="text" id="username" name="username" size="18" /><br><br>
password: <br><br>
<input type="password" id="password" name="password" size="18" /> <br><br>
<button type="submit">
Login
</button>
</center>
<br><br>
<center>{1}</center>
<br>
""".format(from_page,str(message))

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
            
