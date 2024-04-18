from flask import Flask
app = Flask(__name__)
if __name__ == "__main__":
    app.run(debug=True)
import psycopg2
from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/railway_db'
db = SQLAlchemy(app)
from datetime import datetime
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
class Train(db.Model):
    __tablename__ = 'trains'
    id = db.Column(db.Integer, primary_key=True)
    source_station = db.Column(db.String(100), nullable=False)
    destination_station = db.Column(db.String(100), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey('trains.id'), nullable=False)
    booking_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
app = Flask(__name__)
# Database configuration and model definitions here...
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = 'Regular'
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 400
    password_hash = generate_password_hash(password)
    new_user = User(username=username, password_hash=password_hash, role=role)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201
@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid username or password'}), 401
    token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'])
    return jsonify({'token': token.decode('UTF-8')}), 200
if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
app = Flask(__name__)
@app.route('/trains/add', methods=['POST'])
def add_train():
    if g.user.role != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    source_station = data.get('source_station')
    destination_station = data.get('destination_station')
    total_seats = data.get('total_seats')
    if not source_station or not destination_station or not total_seats:
        return jsonify({'error': 'Missing parameters'}), 400
    new_train = Train(source_station=source_station, destination_station=destination_station, total_seats=total_seats)
    db.session.add(new_train)
    db.session.commit()
    return jsonify({'message': 'Train added successfully'}), 201
@app.route('/trains/availability', methods=['GET'])
def get_seat_availability():
    source_station = request.args.get('source_station')
    destination_station = request.args.get('destination_station')
    if not source_station or not destination_station:
        return jsonify({'error': 'Missing parameters'}), 400
    trains = Train.query.filter_by(source_station=source_station, destination_station=destination_station).all()
    if not trains:
        return jsonify({'message': 'No trains found for the given route'}), 404
    availability = [{'train_id': train.id, 'total_seats': train.total_seats} for train in trains]
    return jsonify({'availability': availability}), 200
@app.route('/bookings/book', methods=['POST'])
def book_seat():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is missing'}), 401
    try:
        user_id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    data = request.json
    train_id = data.get('train_id')
    if not train_id:
        return jsonify({'error': 'Missing parameter: train_id'}), 400
    train = Train.query.get(train_id)
    if not train:
        return jsonify({'error': 'Train not found'}), 404
    if train.total_seats <= 0:
        return jsonify({'error': 'No seats available on this train'}), 400
    booking = Booking(user_id=user_id, train_id=train_id)
    db.session.add(booking)
    train.total_seats -= 1
    db.session.commit()
    return jsonify({'message': 'Seat booked successfully'}), 200
@app.route('/bookings/details/<int:booking_id>', methods=['GET'])
def get_booking_details(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    return jsonify({'booking_id': booking.id, 'user_id': booking.user_id, 'train_id': booking.train_id, 'booking_timestamp': booking.booking_timestamp}), 200
if __name__ == "__main__":
    app.run(debug=True)
from flask import g
@app.before_request
def decode_token():
    token = request.headers.get('Authorization')
    if token:
        try:
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded_token.get('user_id')
            user = User.query.get(user_id)
            g.user = user
        except jwt.ExpiredSignatureError:
            g.user = None
        except jwt.InvalidTokenError:
            g.user = None
    else:
        g.user = None
@app.route('/trains/add', methods=['POST'])
def add_train():
    if not g.user or g.user.role != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 401
from flask_migrate import Migrate
# After defining your Flask app and database
migrate = Migrate(app, db)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
