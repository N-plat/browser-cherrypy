import MySQLdb
import os
import datetime
import cherrypy
import hashlib

import html_strings

from cherrypy.lib import static

#from require import require

import utils

import json

from auth import is_session_authenticated

class Register(object):
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
        
        is_mobile = False
        
        if "User-Agent" in cherrypy.request.headers and ("Android" in cherrypy.request.headers['User-Agent'] or "iPhone" in cherrypy.request.headers['User-Agent'] or "iPad" in cherrypy.request.headers['User-Agent']):
            is_mobile = True

        body_string = """<center><h2>Registration</h2></center>
<center>N-plat is a social media website like Twitter or Facebook, except that it does not censor content. Currently only text is supported, but we will hopefully add photos and videos soon. All information posted is viewable by anyone on the open internet, and there is no way to delete anything. There is no way to recover lost passwords right now. Please contact nplat.feedback@gmail.com for comments, feature requests, etc. </center><br><br>
<center>
   <form id="register_form" target="console_iframe" method="post" action="register">
   e-mail address: * <br><br>
   <input type="text" id="email" name="email" size="30" /><br><br>
   username: * <br><br>
   <input type="text" id="username" name="username" size="18" /><br><br>
   password: * <br><br>
   <input type="password" id="password" name="password" size="18" /> <br><br>
   name: <br><br>
   <input type="text" id="name" name="name" size="18" /><br><br>

<b>By clicking the "Register" button, you agree that you have read and understand the above description of what N-plat is.</b> 

<br> <br>

  <button id="register" type="submit">
  Register
  </button>
  </form>
  <iframe name="console_iframe" id ="console_iframe" class="terminal" /></iframe>
</center>
<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script>
  <script type="text/javascript">
$('#register_form').submit(function(event) {{
   event.preventDefault();
   var $this = $(this);
   $.ajax({{
      url: $this.attr('action'),
      type: 'POST',
      data: $this.serialize(),
      success: function(data){{
        json_object = JSON.parse(data)
        if (json_object["success"]) {{
            var console_iframe = document.getElementById('console_iframe');
            console_iframe.contentWindow.document.open();
            console_iframe.contentWindow.document.close();
            $('#register_form').hide();
            console_iframe.contentWindow.document.write('<head><base target="_parent"></head><center style="color:blue;font-size:20px;font-weight:bold">Registration was successful.<br>You can now <a href="/auth/login/">login</a>.</center>');
            gtag_report_conversion();
        }}
        else {{
            var console_iframe = document.getElementById('console_iframe');
            console_iframe.contentWindow.document.open();
            console_iframe.contentWindow.document.close();
            console_iframe.contentWindow.document.write('<center style="color:red;font-size:20px;font-weight:bold;white-space:pre-wrap">'+json_object["errors"]+'</center>');
        }}
      }},
      error : function (data) {{
        var console_iframe = document.getElementById('console_iframe');
        console_iframe.write("Error.");
      }}
   }});
}});
</script>        
<br><br>
"""

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
    def register(self, email, username, password,name):

        print "len(username): "+str(len(username))
        print "username.encode('utf-8'): "+username.encode('utf-8')
        print "username: "+username
        print "len(password): "+str(len(password))
        print "name.encode('utf-8'): "+name.encode('utf-8')
        print "name: "+name
        print "len(email): "+str(len(email))
        print "email.encode('utf-8'): "+email.encode('utf-8')
        print "email: "+email

#        $( "iframe" ).clear()
        def register_function():

            json_object = {}

            json_object["success"] = True

            json_object["errors"] = []

            if len(email) == 0:
                json_object["success"] = False
                json_object["errors"].append("E-mail address is empty.")
                print json.dumps(json_object)
                return json.dumps(json_object)

            if len(email) > 100:
                json_object["success"] = False
                json_object["errors"].append("E-mail address is too long.")
                print json.dumps(json_object)
                return json.dumps(json_object)            

            if len(email.strip(" ")) == 0:
                json_object["success"] = False
                json_object["errors"].append("Empty spaces are not allowed in the e-mail address. The e-mail address that you entered is \""+username+"\".")
                print json.dumps(json_object)
                return json.dumps(json_object)
            
            if email[0] == " ":
                json_object["success"] = False
                json_object["errors"].append("Empty spaces are not allowed in the e-mail address. The e-mail address that you entered is \""+email+"\". There are one or more empty spaces at the beginning.")
                print json.dumps(json_object)
                return json.dumps(json_object)

            for c in email.rstrip(" "):
                if c != 'a' and c != 'b' and c != 'c' and c != 'd' and c != 'e' and c != 'f' and c != 'g' and c != 'h' and c != 'i' and c != 'j' and c != 'k' and c != 'l' and c != 'm' and c != 'n' and c != 'o' and c != 'p' and c != 'q' and c != 'r' and c != 's' and c != 't' and c != 'u' and c != 'v' and c != 'w' and c != 'x' and c != 'y' and c != 'z' and c != 'A' and c != 'B' and c != 'C' and c != 'D' and c != 'E' and c != 'F' and c != 'G' and c != 'H' and c != 'I' and c != 'J' and c != 'K' and c != 'L' and c != 'M' and c != 'N' and c != 'O' and c != 'P' and c != 'Q' and c != 'R' and c != 'S' and c != 'T' and c != 'U' and c != 'V' and c != 'W' and c != 'X' and c != 'Y' and c != 'Z' and c != '0' and c != '1' and c != '2' and c != '3' and c != '4' and c != '5' and c != '6' and c != '7' and c != '8' and c != '9' and c != '_' and c != '-' and c != '.' and c != "@":
                    json_object["success"] = False

                    if c == " ":
                        json_object["errors"].append("Empty spaces are not allowed in the e-mail address.")
                    elif c != '"' and c != "'":
                        print "ord(c): "+str(ord(c))
                        json_object["errors"].append('"' + c + '"' +" not allowed in e-mail address.")
                    else:
                        json_object["errors"].append(c +" not allowed in e-mail address.")
                        
                    print json.dumps(json_object)
                    return json.dumps(json_object)

            if len(email) != len(email.rstrip(" ")):
                json_object["success"] = False
                json_object["errors"].append("Empty spaces are not allowed in the e-mail address. The e-mail address that you entered is \""+email+"\". There are one or more empty spaces at the end.")
                print json.dumps(json_object)
                return json.dumps(json_object)
                
            if len(username) > 30:
                json_object["success"] = False
                json_object["errors"].append("username too long")
                print json.dumps(json_object)
                return json.dumps(json_object)
            
            if len(username) == 0:
                json_object["success"] = False
                json_object["errors"].append("Username is empty.")
                print json.dumps(json_object)
                return json.dumps(json_object)

            if len(username.strip(" ")) == 0:
                json_object["success"] = False
                json_object["errors"].append("Empty spaces are not allowed in the username. The username that you entered is \""+username+"\".")
                print json.dumps(json_object)
                return json.dumps(json_object)

            if username[0] == " ":
                json_object["success"] = False
                json_object["errors"].append("Empty spaces are not allowed in the username. The username that you entered is \""+username+"\". There are one or more empty spaces at the beginning.")
                print json.dumps(json_object)
                return json.dumps(json_object)
    
            for c in username.rstrip(" "):
                if c != 'a' and c != 'b' and c != 'c' and c != 'd' and c != 'e' and c != 'f' and c != 'g' and c != 'h' and c != 'i' and c != 'j' and c != 'k' and c != 'l' and c != 'm' and c != 'n' and c != 'o' and c != 'p' and c != 'q' and c != 'r' and c != 's' and c != 't' and c != 'u' and c != 'v' and c != 'w' and c != 'x' and c != 'y' and c != 'z' and c != 'A' and c != 'B' and c != 'C' and c != 'D' and c != 'E' and c != 'F' and c != 'G' and c != 'H' and c != 'I' and c != 'J' and c != 'K' and c != 'L' and c != 'M' and c != 'N' and c != 'O' and c != 'P' and c != 'Q' and c != 'R' and c != 'S' and c != 'T' and c != 'U' and c != 'V' and c != 'W' and c != 'X' and c != 'Y' and c != 'Z' and c != '0' and c != '1' and c != '2' and c != '3' and c != '4' and c != '5' and c != '6' and c != '7' and c != '8' and c != '9' and c != '_' and c != '-' and c != '.':
                    json_object["success"] = False

                    if c == " ":
                        json_object["errors"].append("Empty spaces are not allowed in the username.")
                    elif c != '"' and c != "'":
                        print "ord(c): "+str(ord(c))
                        json_object["errors"].append('"' + c + '"' +" not allowed in username.")
                    else:
                        json_object["errors"].append(c +" not allowed in username.")
                        
                    print json.dumps(json_object)
                    return json.dumps(json_object)

            if len(username) != len(username.rstrip(" ")):
                json_object["success"] = False
                json_object["errors"].append("Empty spaces are not allowed in the username. The username that you entered is \""+username+"\". There are one or more empty spaces at the end.")
                print json.dumps(json_object)
                return json.dumps(json_object)

            for c in password.rstrip(" "):
                if c != 'a' and c != 'b' and c != 'c' and c != 'd' and c != 'e' and c != 'f' and c != 'g' and c != 'h' and c != 'i' and c != 'j' and c != 'k' and c != 'l' and c != 'm' and c != 'n' and c != 'o' and c != 'p' and c != 'q' and c != 'r' and c != 's' and c != 't' and c != 'u' and c != 'v' and c != 'w' and c != 'x' and c != 'y' and c != 'z' and c != 'A' and c != 'B' and c != 'C' and c != 'D' and c != 'E' and c != 'F' and c != 'G' and c != 'H' and c != 'I' and c != 'J' and c != 'K' and c != 'L' and c != 'M' and c != 'N' and c != 'O' and c != 'P' and c != 'Q' and c != 'R' and c != 'S' and c != 'T' and c != 'U' and c != 'V' and c != 'W' and c != 'X' and c != 'Y' and c != 'Z' and c != '0' and c != '1' and c != '2' and c != '3' and c != '4' and c != '5' and c != '6' and c != '7' and c != '8' and c != '9' and c != '_' and c != '-' and c != '.' and c != '~' and c != '`' and c != '!' and c != '@' and c != '#' and c != '$' and c != '%' and c != '^' and c != '&' and c != '*' and c != '(' and c != ')' and c != '+' and c != '=' and c != ' ' and c != '{' and c != '}' and c != '[' and c != ']' and c != ':' and c != ';' and c != '?' and c != '/' and c != ',' and c != '<' and c != '>' and c != '?' and c != '/' and c != "'" and c != '"' and c != '|':
                    json_object["success"] = False
                    print "ord(c): "+str(ord(c))
                    json_object["errors"].append("One of the characters in the password that you entered is not allowed.")
                    print json.dumps(json_object)
                    return json.dumps(json_object)


            secrets_file=open("/home/ec2-user/secrets.txt")

            passwords=secrets_file.read().rstrip('\n')

            db_password = passwords.split('\n')[0]

            dbname = "nplat"

            h = hashlib.sha256()

            h.update(password)

            #only allow one person to register at a time
            ret=os.system("if [ -f /home/ec2-user/registering_someone ]; then exit 0; else exit 1; fi");

            if ret == 0:
                json_object["success"] = False
                print json.dumps(json_object)
                return json.dumps(json_object)

            os.system("touch /home/ec2-user/registering_someone");

            conn = MySQLdb.connect(host='nplat-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

            curs = conn.cursor()

            curs.execute("use "+dbname+";")

            curs.execute("select * from user_info where username = \""+username+"\"")

            user_infos = curs.fetchall()

            if len(user_infos) > 0:
                json_object["success"] = False
                json_object["errors"].append("This username is already taken.")
                os.system("rm /home/ec2-user/registering_someone");
                print json.dumps(json_object)
                return json.dumps(json_object)

            curs.execute("select * from user_info where email = \""+email+"\"")

            user_infos = curs.fetchall()

            if len(user_infos) > 0:
                json_object["success"] = False
                json_object["errors"].append("This e-mail address is already used.")
                os.system("rm /home/ec2-user/registering_someone");
                print json.dumps(json_object)
                return json.dumps(json_object)
            
            if len(password) < 6:
                json_object["success"] = False
                json_object["errors"].append("Password shorter than 6 characters.")
                os.system("rm /home/ec2-user/registering_someone");
                print json.dumps(json_object)
                return json.dumps(json_object)

            if username in ["auth","register","feed","post","follow","following","followers","myposts"]:
                json_object["success"] = False
                json_object["errors"].append("Invalid username.")
                os.system("rm /home/ec2-user/registering_someone");
                print json.dumps(json_object)
                return json.dumps(json_object)            
            
            curs.execute("insert into user_info set email = \""+email+"\", username = \""+username+"\", hashed_password = \""+h.hexdigest()+"\", name = \""+name+"\", registration_time = now(6)")

            conn.commit()

            os.system("rm /home/ec2-user/registering_someone");

            conn.close()

            print json.dumps(json_object)

            return json.dumps(json_object)

        return register_function()


