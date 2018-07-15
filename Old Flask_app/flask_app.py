from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, Float, Column, ForeignKey, String
from db_setup import Dealers

app = Flask(__name__)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="DennisDemenis",
    password="advanced",
    hostname="DennisDemenis.mysql.pythonanywhere-services.com",
    databasename="DennisDemenis$cardealers",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        #trial = Trial.query.all()
        #return render_template("stroop.html")
        return render_template("stroop.html")
    else:
        #color = str(request.form["color"])
        #reactiontime = float(request.form["reactiontime"])

        #filename = "/home/DennisDemenis/WebPage/stroop.txt"
        #file = open(filename, 'a')
        #file.write("\n");file.write(str(color)); file.write("\t"); file.write(str(emotion))
        #file.close()
        return redirect(url_for('index'))

    #trial = Trial(color=color, emotion=emotion, reaction_time=reaction_time)
    #user = User(name=name, age=age, gender=gender, favcolor=favcolor)
    #db.session.add(trial)
    #db.session.add(user)
    #db.session.commit()

    # This is a comment
    return redirect(url_for('index'))
