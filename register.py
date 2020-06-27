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

#"""+(html_strings.authenticated_header if utils.is_session_authenticated() else html_strings.not_authenticated_header)+"""

class Register(object):
    @cherrypy.expose
    def index(self):

        gtag = open("gtag.js").read()
        
        return """
<html>
<head>
{0}
</head>
<body>
<center><h1>A Neutral Platform</h1></center>
<center><h2>Registration</h2></center>
<center>N-plat is a social media website like Twitter or Facebook, except that it does not censor content. Currently only text is supported, but we will hopefully add photos and videos soon. All information posted is viewable by anyone on the open internet, and there is no way to delete anything. There is no way to recover lost passwords right now. Please contact nplat.feedback@gmail.com for comments, feature requests, etc. </center><br><br>
<center>
   <form id="register_form" target="console_iframe" method="post" action="register">
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
<br><br>
<center>This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact nplat.feedback@gmail.com for comments, feature requests, etc.</center>
</body>
</html>
""".format(gtag)



    @cherrypy.expose
    def register(self, username, password,name):

        print "len(username): "+str(len(username))
        print "username.encode('utf-8'): "+username.encode('utf-8')
        print "username: "+username
        print "len(password): "+str(len(password))
        print "name.encode('utf-8'): "+name.encode('utf-8')
        print "name: "+name

#        $( "iframe" ).clear()
        def register_function():

            json_object = {}

            json_object["success"] = True

            json_object["errors"] = []

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
            
            if len(password) < 6:
                json_object["success"] = False
                json_object["errors"].append("Password shorter than 6 characters.")
                os.system("rm /home/ec2-user/registering_someone");
                print json.dumps(json_object)
                return json.dumps(json_object)
            
            curs.execute("insert into user_info set username = \""+username+"\", hashed_password = \""+h.hexdigest()+"\", name = \""+name+"\", registration_time = now(6)")

            conn.commit()

            os.system("rm /home/ec2-user/registering_someone");

            conn.close()

            print json.dumps(json_object)

            return json.dumps(json_object)

        return register_function()
