import os
import datetime
import mysql
import simplejson as json
from flask import Flask, redirect, render_template, request, url_for, flash
from flask import  send_from_directory, session
from flask_socketio import join_room, leave_room
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean
from werkzeug.utils import secure_filename
from config import DB_URI, UP_FOLDER
from nlp_nltk import NLP

UPLOAD_FOLDER = UP_FOLDER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

application = Flask(__name__, static_folder = 'static')

SQLALCHEMY_DATABASE_URI = DB_URI

application.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
#application.config["SQLALCHEMY_POOL_RECYCLE"] = 3000
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

socketio = SocketIO(application)
db = SQLAlchemy(application)
nlp = NLP()

class Project(db.Model):
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(String(128))
    description = db.Column(String(1028))
    filename = db.Column(String(128))

class UserChat(db.Model):
    __tablename__ = "userchat"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(String(128)) #bot or user
    message = db.Column(String(1028))

class Fotos(db.Model):
    __tablename__ = "fotoalbum"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(String(128))
    filepath = db.Column(String(256))
   
#    last_updated = db.Column(DateTime, onupdate=datetime.datetime.now)
# RUN OUTSIDE OF THE SCRIPT:
#from db_setup import db
#db.create_all()
#or simply python db_setup.py

@application.route("/")
def index():
    return render_template('index.html')

@application.route("/playpage", methods=["GET"])
def playpage():
    print("Hallo Playpage")
    return render_template('playpage.html')

@application.route('/interactive', methods=["GET", "POST"])
def interactive():
    return render_template('interactive.html')

@application.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    return render_template("chatbot.html")

@application.route('/editwork', methods=["GET", "POST"])
def editwork():
    if request.method == "POST":
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(application.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            #return redirect(url_for('uploaded_file',filename=filename))
            name = str(request.form["name"])
            descr = str(request.form["descr"])
            project = Project(name=name, description=descr, filename = filepath[1:])
            db.session.add(project)
            db.session.commit()
            db.session.close()
        # return send_from_directory(directory, filename, as_attachment=True)
        return redirect(url_for('editwork'))
    else:
        #recipes = db.session.query(Recipe).all()
        return render_template('editwork.html', results = Project.query.all())

@application.route('/lebenslauf', methods=["GET"])
def lebenslauf():
    return render_template('lebenslauf.html')

@application.route('/fotoalbum', methods=["GET", "POST"])
def fotoalbum():
    return render_template('fotoalbum.html', fotos = Fotos.query.all())


@application.route('/editfotoalbum', methods=["GET", "POST"])
def editfotoalbum():
    if request.method == "POST":
        mydata = request.files.getlist("file")
        for file in mydata:
            filename = secure_filename(file.filename)
            filepath = os.path.join(application.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            foto = Fotos(filename=filename, filepath = filepath)
            db.session.add(foto)
            db.session.commit()
            db.session.close()

    return render_template('editfotoalbum.html', fotos = Fotos.query.all())

@application.route('/work', methods=["GET"])
def work():
    return render_template('work.html', results = Project.query.all())

@application.route('/showwork/<int:idd>', methods=["GET"])
def showwork(idd):
    item = db.session.query(Project).filter_by(id=idd).one()
    print(item.filename)
    print(item)
    print (idd)
    return render_template('showwork.html',filename = item.filename)
#    return render_template('work.html', filename=item.filename)

    #return send_from_directory(UPLOAD_FOLDER, item.filename, as_attachment=True)

@application.route('/deletework/<int:idd>', methods=["GET", "POST"])
def deletework(idd):
    itemToDelete = db.session.query(Project).filter_by(id=idd).one()
    if request.method == 'POST':
        db.session.delete(itemToDelete)
        db.session.commit()
        return render_template('deletework.html', name=itemToDelete.name)
    else:
        return render_template('deletework.html', name=itemToDelete.name)

@socketio.on('message')
def handleMessage(msg):
    print("message: " + msg)
    send(msg, broadcast=True)

@socketio.on('myevent')
def handleMyEvent(input):
    print('received my event: ' + str(input))
    room = input['room']
    user = input['username']
    send(input, room=room)

@socketio.on('join')
def handleJoin(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', room=room)

@socketio.on('myBotEvent')
def handleMyBot(data):
    print('received my event: ' + str(data))
    output1 = {"username":data["username"], "message":data["message"]}
    send(output1, broadcast=True)
    response = nlp.respond(data["message"])
    entry1 = UserChat(user=data["username"], message=data["message"])
    entry2 = UserChat(user='bot', message=response)
    db.session.add(entry1)
    db.session.add(entry2)
    db.session.commit()
    db.session.close()
    output2 = {"username": "BOT", "message": response}
    send(output2, broadcast=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    application.debug = True
    socketio.run(application)
    #app.run()
