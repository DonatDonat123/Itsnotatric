import os
import datetime
import mysql
from flask import Flask, redirect, render_template, request, url_for, send_from_directory
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, Float, Column, ForeignKey, String
from werkzeug.utils import secure_filename
#from db_setup import Dealers, Recipe, Project

UPLOAD_FOLDER = '/home/DennisDemenis/WebPage/fotos'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

from nlp import NLP
nlp = NLP()
print ('NLP Object Created \n <br>')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__, static_folder = 'fotos')

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="DennisDemenis",
    password="advanced",
    hostname="DennisDemenis.mysql.pythonanywhere-services.com",
    databasename="DennisDemenis$cardealers",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 300
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'mysecret'

socketio = SocketIO(app)

db = SQLAlchemy(app)

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
#    last_updated = db.Column(DateTime, onupdate=datetime.datetime.now)
# RUN OUTSIDE OF THE SCRIPT:
#from db_setup import db
#db.create_all()

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    if request.method == "POST":
        print ('THEY POSTED !!!')
        user = 'user' # change with login later
        message = str(request.form["message"])
        entry1 = Chat(user=user, message=message)
        response = nlp.respond(message)
        entry2 = Chat(user = 'bot', message = response)
        db.session.add(entry1)
        db.session.add(entry2)
        db.session.commit()
        db.session.close()
        print ('T')
        #return render_template("carnovo.html", results=Dealers.query.all())
        return redirect(url_for('chatbot'))
    else:
        return render_template("chatbot.html", results=Chat.query.all())


@app.route("/cardealers", methods=["GET", "POST"])
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


@app.route('/recipes', methods=["GET", "POST"])
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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
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

@app.route('/deleterecipe/<int:idd>', methods=["GET", "POST"])
def deleterecipe(idd):
    itemToDelete = db.session.query(Recipe).filter_by(id=idd).one()
    if request.method == 'POST':
        db.session.delete(itemToDelete)
        db.session.commit()
        return render_template('deleterecipe.html', name=itemToDelete.name)
    else:
        return render_template('deleterecipe.html', name=itemToDelete.name)


@app.route('/work', methods=["GET", "POST"])
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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
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

@app.route('/showwork/<int:idd>', methods=["GET"])
def showwork(idd):
    item = db.session.query(Project).filter_by(id=idd).one()
    return send_from_directory(UPLOAD_FOLDER, item.filename, as_attachment=True)

@app.route('/deletework/<int:idd>', methods=["GET", "POST"])
def deletework(idd):
    itemToDelete = db.session.query(Project).filter_by(id=idd).one()
    if request.method == 'POST':
        db.session.delete(itemToDelete)
        db.session.commit()
        return render_template('deleterecipe.html', name=itemToDelete.name)
    else:
        return render_template('deleterecipe.html', name=itemToDelete.name)

@app.route('/interactive', methods=["GET", "POST"])
def interactive():
    return render_template('interactive.html')

if __name__ == '__main__':
    app.debug = True
    socketio.run(app)
    #app.run()
