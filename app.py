from flask import Flask, render_template, url_for, request, session, redirect, Response, jsonify
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from bson import ObjectId
import os
from dotenv import load_dotenv
from bson.json_util import dumps
from bson.objectid import ObjectId

load_dotenv()

app = Flask(__name__)
app.secret_key = 'mysecret'

client = MongoClient('mongodb+srv://alexanderastorga:parasyte2134@iot-cognitive.dvor5qx.mongodb.net/')
db = client['ProyectoCognitive']
users_collection = db['users']
sensor_collection = db['sensors']
bcrypt = Bcrypt(app)
@app.route('/')
def index():
    if 'user_id' in session:
        user_id = ObjectId(session['user_id'])
        user = users_collection.find_one({'_id': user_id})
        sensors = list(db.sensors.find({}))
        
        led_sensors = [sensor for sensor in sensors if sensor['type'] == 'LED']
        dht_sensors = [sensor for sensor in sensors if sensor['type'] == 'DHT']
        mq2_sensors = [sensor for sensor in sensors if sensor['type'] == 'MQ2']
        
        # Diccionario para rastrear sensores por localización
        sensors_by_location = {}
        
        for sensor in sensors:
            location = sensor['location']
            if location in sensors_by_location:
                sensors_by_location[location].append(sensor)
            else:
                sensors_by_location[location] = [sensor]
        
        # Filtrar las localizaciones con más de un sensor
        multiple_location_sensors = {location: sensors for location, sensors in sensors_by_location.items() if len(sensors) > 1}
        
        print(multiple_location_sensors)
        
        return render_template('index.html', led_sensors=led_sensors, dht_sensors=dht_sensors, mq2_sensors=mq2_sensors, sensors_by_location=multiple_location_sensors)    
    return redirect(url_for('login'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']
        correo = request.form['correo']

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user_data = {
            'username': username,
            'password': hashed_password,
            'correo': correo
        }

        users_collection.insert_one(user_data)

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['pass']

        user = users_collection.find_one({'correo': correo})

        if user:
            if bcrypt.check_password_hash(user['password'], password):
                session['user_id'] = str(user['_id'])
                return redirect(url_for('index'))
            else:
                print("Contraseña incorrecta")
        else:
            print("Correo no encontrado")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))




@app.get("/api/sensors")
def get_sensors():
    sensor_id = request.args.get('sensor_id')
    filter = {} if sensor_id is None else {"sensor_id": sensor_id}
    sensors = list(db.sensors.find(filter))
    
    response = Response(
        response=dumps(sensors), status=200, mimetype='application/json') 
    return response

@app.post("/api/sensors")
def add_sensor():
    _json = request.json
    db.sensors.insert_one(_json)
    
    resp = jsonify({"message": "Sensor añadido satisfactoriamente"})
    resp.status_code = 200
    return resp

@app.delete("/api/sensors/<id>")
def delete_sensor(id):
    db.sensors.delete_one({"_id": ObjectId(id)})
    
    resp = jsonify({"message": "Sensor eliminado satisfactoriamente"})
    resp.status_code = 200
    return resp

@app.put("/api/sensors/<id>")
def update_sensor(id):
    _json = request.json
    db.sensors.update_one({"_id": ObjectId(id)}, {"$set": _json})
    
    resp = jsonify({"message": "Sensor actualizado satisfactoriamente"})
    resp.status_code = 200
    return resp

@app.errorhandler(400)
def handle_400_error(error):
    return make_response(jsonify({"errorCode": error.code, 
                                  "errorDescription": "Bad request!",
                                  "errorDetailedDescription": error.description,
                                  "errorName": error.name}), 400)

@app.errorhandler(404)
def handle_404_error(error):
        return make_response(jsonify({"errorCode": error.code, 
                                  "errorDescription": "Resource not found!",
                                  "errorDetailedDescription": error.description,
                                  "errorName": error.name}), 404)

@app.errorhandler(500)
def handle_500_error(error):
        return make_response(jsonify({"errorCode": error.code, 
                                  "errorDescription": "Internal Server Error",
                                  "errorDetailedDescription": error.description,
                                  "errorName": error.name}), 500)

if __name__ == '__main__':
    app.run(debug=1, host='0.0.0.0', port=5000)
