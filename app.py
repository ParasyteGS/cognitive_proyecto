from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/ProyectCog"
mongo = PyMongo(app)

@app.route('/')
def index():
    if 'username' in session:
        return 'Estas logueado como ' + session['username']
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['correo']})
    
    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['correo'] = request.form['correo']
            return redirect(url_for('index'))
    return 'Correo/password incorrectos!'
                                               
                                               
                                               
                                               
@app.route('/register', methods=['POST', 'GET'])
def register():
    return render_template('register.html')

    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['correo']})
        
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass, 'email' : request.form['correo']})
            session['correo'] = request.form['correo']
            return redirect(url_for('index'))
    return 'Usuario ya existe!'


if __name__ == '__main__':
    app.secret_key = 'sdasdsa'
    app.run(debug=True)