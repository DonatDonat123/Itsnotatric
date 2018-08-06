import os
import datetime
import mysql
import simplejson as json
from flask import Flask, redirect, render_template, request, url_for
from flask import  send_from_directory, session
from flask_socketio import join_room, leave_room
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean
from werkzeug.utils import secure_filename
from config import DB_URI, UP_FOLDER
#from nlp import NLP

#from db_setup import Dealers, Recipe, Project

UPLOAD_FOLDER = UP_FOLDER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

application = Flask(__name__, static_folder = 'fotos')

SQLALCHEMY_DATABASE_URI = DB_URI

application.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
#application.config["SQLALCHEMY_POOL_RECYCLE"] = 3000
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

socketio = SocketIO(application)
db = SQLAlchemy(application)

class Dealers(db.Model):
    __tablename__ = "dealers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(String(128))
    pcode = db.Column(String(128))

class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(String(128))
    description = db.Column(String(1028))
    filename = db.Column(String(128))

class Project(db.Model):
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(String(128))
    description = db.Column(String(1028))
    filename = db.Column(String(128))

class Chat(db.Model):
    __tablename__ = "chat"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(String(128)) #bot or user
    message = db.Column(String(1028))
    city1 = db.Column(String(24))
    city2 = db.Column(String(24))
    origin = db.Column(String(24))
    blindshot = db.Column(Boolean)
    docity1 = db.Column(Boolean)
    docity12 = db.Column(Boolean)
    askorigin = db.Column(Boolean)
    bydistance = db.Column(Boolean)
    askdist = db.Column(Boolean)

class UserChat(db.Model):
    __tablename__ = "userchat"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(String(128)) #bot or user
    message = db.Column(String(1028))
   
#    last_updated = db.Column(DateTime, onupdate=datetime.datetime.now)
# RUN OUTSIDE OF THE SCRIPT:
#from db_setup import db
#db.create_all()

@application.route("/")

def index():
    return render_template('index.html')

@application.route("/userchat", methods=["GET", "POST"])
def userchat():
    print ("Hallo Userchat")
    return render_template("userchat.html")

@socketio.on('message')
def handleMessage(msg):
    print("message: " + msg)
    room = "room0"
    send(msg, room=room)

@socketio.on('myevent')
def handleMyEvent(input):
    print('received my event: ' + str(input))
    room = input['room']
    print ("room: " + room)
    print (request.sid)
    socketio.send(input, room=room)

@socketio.on('join')
def handleJoin(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', room=room)

@application.route("/chatbotInit", methods=["GET"])
def chatbotInit():
    entry1 = Chat(user = 'init', message = 'hello', city1=None, city2=None, origin=None, blindshot=False, docity1=False, docity12=False\
        ,askorigin=False, bydistance=False, askdist=False)
    db.session.add(entry1)
    db.session.commit()
    db.session.close()
    return redirect(url_for('chatbot'))

@application.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    if request.method == "POST":
        print ('THEY POSTED !!!')
        user = 'user' # change with login later
        message = str(request.form["message"])
        cfg = Chat.query.order_by(Chat.id.desc()).limit(1).one()
        nlp = NLP(cfg.city1, cfg.city2, cfg.origin, cfg.blindshot, cfg.docity1, cfg.docity12, cfg.askorigin, cfg.bydistance, cfg.askdist)
        response, city1, city2, origin, blindshot, docity1, docity12, askorigin, bydistance, askdist = nlp.respond(message)
        entry1 = Chat(user = user, message = message, city1=city1, city2=city2, origin=origin, blindshot=blindshot, docity1=docity1, docity12=docity12\
        ,askorigin=askorigin, bydistance=bydistance, askdist=askdist)
        entry2 = Chat(user = 'bot', message = response, city1=city1, city2=city2, origin=origin, blindshot=blindshot, docity1=docity1, docity12=docity12\
                 ,askorigin=askorigin, bydistance=bydistance, askdist=askdist)
        db.session.add(entry1)
        db.session.add(entry2)
        db.session.commit()
        db.session.close()
        #return render_template("carnovo.html", results=Dealers.query.all())
        return redirect(url_for('chatbot'))
    else:
        return render_template("chatbot.html", results=Chat.query.all())


@application.route("/cardealers", methods=["GET", "POST"])
def cardealers():
    if request.method == "POST":
        print ('THEY POSTED !!!')
        name = str(request.form["name"])
        pcode = str(request.form["pcode"])
        cardealer = Dealers(name=name, pcode=pcode)
        db.session.add(cardealer)
        db.session.commit()
        db.session.close()
        #return render_template("carnovo.html", results=Dealers.query.all())
        return redirect(url_for('cardealers'))
    else:
        return render_template("carnovo.html", results=Dealers.query.all())


@application.route('/recipes', methods=["GET", "POST"])
def recipes():
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
            #filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('uploaded_file',filename=filename))
            name = str(request.form["name"])
            descr = str(request.form["descr"])
            recipe = Recipe(name=name, description=descr, filename = url_for('static',filename = filename))
            db.session.add(recipe)
            db.session.commit()
            db.session.close()
        # return send_from_directory(directory, filename, as_attachment=True)
        return redirect(url_for('recipes'))
    else:
        #recipes = db.session.query(Recipe).all()
        return render_template('recipes2.html', results = Recipe.query.all())

@application.route('/deleterecipe/<int:idd>', methods=["GET", "POST"])
def deleterecipe(idd):
    itemToDelete = db.session.query(Recipe).filter_by(id=idd).one()
    if request.method == 'POST':
        db.session.delete(itemToDelete)
        db.session.commit()
        return render_template('deleterecipe.html', name=itemToDelete.name)
    else:
        return render_template('deleterecipe.html', name=itemToDelete.name)


@application.route('/work', methods=["GET", "POST"])
def work():
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
            #filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('uploaded_file',filename=filename))
            name = str(request.form["name"])
            descr = str(request.form["descr"])
            project = Project(name=name, description=descr, filename = filename)
            db.session.add(project)
            db.session.commit()
            db.session.close()
        # return send_from_directory(directory, filename, as_attachment=True)
        return redirect(url_for('work'))
    else:
        #recipes = db.session.query(Recipe).all()
        return render_template('work.html', results = Project.query.all())

@application.route('/showwork/<int:idd>', methods=["GET"])
def showwork(idd):
    item = db.session.query(Project).filter_by(id=idd).one()
    return send_from_directory(UPLOAD_FOLDER, item.filename, as_attachment=True)

@application.route('/deletework/<int:idd>', methods=["GET", "POST"])
def deletework(idd):
    itemToDelete = db.session.query(Project).filter_by(id=idd).one()
    if request.method == 'POST':
        db.session.delete(itemToDelete)
        db.session.commit()
        return render_template('deleterecipe.html', name=itemToDelete.name)
    else:
        return render_template('deleterecipe.html', name=itemToDelete.name)

@application.route('/interactive', methods=["GET", "POST"])
def interactive():
    return render_template('interactive.html')

if __name__ == '__main__':
    application.debug = True
    socketio.run(application)
    #app.run()
