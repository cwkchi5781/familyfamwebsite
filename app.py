from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import gunicorn, mysql.connector
from datetime import datetime

app = Flask(__name__)

app.secret_key = "abcdefg"

db = mysql.connector.connect(
    host="us-cdbr-east-04.cleardb.com",
    user="b8601831567355",
    password="40a53098",
    database="heroku_008b3dac9b6fd1b"
)
#mysql://b8601831567355:40a53098@us-cdbr-east-04.cleardb.com/heroku_008b3dac9b6fd1b?reconnect=true


cursor = db.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(50), password VARCHAR(50))")

cursor.execute("CREATE TABLE IF NOT EXISTS posts (id INT PRIMARY KEY AUTO_INCREMENT, title VARCHAR(50) ,host VARCHAR(50), description VARCHAR(255), day DATE, starttime TIME, endtime TIME, status VARCHAR(10))")
db.commit()

#cursor.execute("INSERT INTO posts(host, description, day, starttime, endtime, status) VALUES ()")

cursor.execute("SELECT starttime FROM posts")
print(cursor.fetchall())


cursor.execute("SHOW DATABASES")
print(cursor.fetchall())

#cursor.execute("DELETE FROM users WHERE username='name'")
#db.commit()
#print("hi")

"""
values=("one", "two")
sql=("INSERT INTO users(username, password) VALUES (%s, %s)")
cursor.execute(sql, values)
db.commit()
"""

cursor.execute("SELECT * FROM users WHERE username='name'")
none = str(cursor.fetchone())
#print("should be empty")
print(none)

print("before")
cursor.execute("SELECT * FROM `BIGFAMILYPROJECT`.`users` WHERE 'username'='name'")
cursor.execute("SELECT * FROM users WHERE username='name'")
output = cursor.fetchall()

if output == []:
    cursor.execute("INSERT INTO users(username, password) VALUES ('name', 'password')")
    db.commit()
    #print("username not taken")
else:
    #print("username already taken")
    pass


#print(str(cursor.fetchone() == none))
#print("after")
cursor.execute("SELECT * FROM users WHERE username='name'")
print(cursor.fetchall())
#print("hello")


"""
class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column("name", db.String(100))
    password = db.Column("password", db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password
"""

@app.route('/', methods=["POST", "GET"])
def index():

    if request.method == "POST":
        name = request.form["username"]
        if (name==""):
            return render_template("index.html", message="No Username")
        if(len(name) > 50):
            return render_template("index.html", message="Username too long. Max length is 50 characters")

        print('name')
        print(name)

        #session["user"] = name
        password = request.form["password"]
        if (password == ""):
            return render_template("index.html", messag="No Password")
        if (len(password) > 50):
            return render_template("index.html", message="Password too long. Max length is 50 characters")

        sql = "SELECT * FROM users WHERE username=%s"

        cursor.execute(sql, (name,))

        shouldbe = cursor.fetchone()

        if str(password) == shouldbe[2]:
            session["user"] = name
            """
            sql = "SELECT * FROM posts WHERE host=%s"

            cursor.execute(sql, (name,))

            userList = cursor.fetchall()
            return render_template("home.html", user=name, list=userList)
            """
            return redirect(url_for("home", message="Just logged in"))

        else:

            return render_template("index.html", message="Invalid Inputs")

    elif "user" in session:
        print("already logged in")
        return redirect(url_for("home", message="Already logged in"))

    return render_template("index.html")
#this is also the login screen


@app.route('/login', methods=["POST", "GET"])
def login():
    return redirect(url_for("index"))


@app.route('/logout', methods=["POST", "GET"])
def logout():
    session.pop("user", none)
    return redirect(url_for("index"))
    #don't forget to add logout alert

@app.route('/home', methods=["POST", "GET"])
def home():
    if "user" in session:
        name = session["user"]
        sql = "SELECT * FROM posts ORDER BY day"
        cursor.fetchall()

        cursor.execute(sql)

        List = cursor.fetchall()
        print(List)

        return render_template("home.html", user=name, list=List)
    else:
        return render_template("index.html")
#extends layout



@app.route('/myevents', methods=["POST", "GET"])
def myevents():
    if "user" in session:
        name = session["user"]

        sql = "SELECT * FROM posts WHERE host=%s ORDER BY day"
        cursor.execute(sql, (name,))

        userList = cursor.fetchall()
        #userList = db.execute("SELECT * FROM post WHERE username=" + str(name) + "")

        return render_template("myevents.html", list=userList, user=name)
    else:
        return render_template("index.html")
#extents layout

@app.route('/cancel/<eventid>', methods=["POST", "GET"])
def cancel(eventid):
    if "user" in session:
        name = session["user"]
        print("got inside user")
        sql = "UPDATE posts SET status='Canceled' WHERE id=%s"
        vars = (eventid,)
        cursor.execute(sql, vars)
        print("hi hello im trying")
        db.commit()
        return redirect(url_for("myevents", message="Event cancelled"))


@app.route('/update/<eventid>', methods=["POST", "GET"])
def edit(eventid):
    if "user" in session:
        name = session["user"]
        if request.method == "POST":
            title = request.form["title"]
            description = request.form["description"]
            day = request.form["day"]
            starttime = request.form["starttime"]
            endtime = request.form["endtime"]

            t1 = datetime.strptime(starttime, "%H:%M")
            t2 = datetime.strptime(endtime, "%H:%M")

            latest = max((t1, t2))

            if latest == t1:
                print("invalid times")
                return redirect(url_for("edit", message="Invalid Time"))

            sql = "UPDATE posts set title = %s, description = %s, day = %s, starttime = %s, endtime = %s, status = %s) WHERE id = %s"
            vars = (title, name, description, day, starttime, endtime, "Normal", eventid)
            cursor.execute(sql, vars)
            db.commit()
            return redirect(url_for("home", message="Event edited"))
        else:
            name = session["user"]
            sql = "SELECT * FROM posts WHERE id=%s and host=%s"
            cursor.execute(sql, (eventid, name))
            eventedit = cursor.fetchone()

            if(eventedit == None):
                return redirect(url_for("home", message="Event doesn't exist"))
            return render_template("edit.html", event=eventedit)
        return redirect(url_for("home", message="Event edit error"))
    return render_template("index.html")

#extends layout
#s

@app.route('/add', methods=["POST", "GET"])
def add():
    if "user" in session:
        name = session["user"]

        if request.method == "POST":
            title = request.form["title"]
            description = request.form["description"]
            day = request.form["day"]
            starttime = request.form["starttime"]
            endtime = request.form["endtime"]

            print(day)
            print(starttime)
            print(endtime)

            t1 = datetime.strptime(starttime, "%H:%M")
            t2 = datetime.strptime(endtime, "%H:%M")

            latest = max((t1, t2))

            if latest == t1:
                print("invalid times")
                return redirect(url_for("add", message="Invalid Time"))

            sql = "INSERT INTO posts(title, host, description, day, starttime, endtime, status) VALUES (%s, %s, %s, %s,%s, %s, %s)"
            vars = (title, name, description, day, starttime, endtime, "Normal")
            cursor.execute(sql, vars)
            db.commit()
            return redirect(url_for("home", message="Event added"))
        return render_template("add.html", user=name)
    else:
        return render_template("index.html")



#extends layout


@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        name = request.form["username"]
        password = request.form["password"]
        compassword = request.form["confirm-password"]


        if (len(name) > 50):
            return render_template("signup.html", message="Username too long. 50 characters max")

        if (len(password) > 50):
            return render_template("signup.html", message="Password too long. 50 characters max")

        sql="SELECT * FROM users WHERE username=%s"
        cursor.execute(sql, (name,))
        derp = cursor.fetchone()
        if(derp != None):
            return render_template("signup.html", message="Username already taken")

        if (compassword != password):
            return render_template("signup.html", message="Passwords do not match")

        sql = "INSERT INTO users(username, password) VALUES (%s, %s)"
        cursor.execute(sql, (name, password))
        db.commit()

        session["user"] = name

        #return render_template("home.html", user=name)
        return redirect(url_for("home", message="Account created"))
    return render_template("signup.html")




if __name__ == '__main__':
    app.run()
