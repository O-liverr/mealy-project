from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from marshmallow import Schema, fields, ValidationError, validates, validate
from datetime import datetime
import jwt
import os
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mealy_user:@mealy@localhost/mealy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '@2025'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Caterer(db.Model):
    __tablename__ = 'Caterers'
    caterer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class MealOption(db.Model):
    __tablename__ = 'MealOptions'
    meal_option_id = db.Column(db.Integer, primary_key=True)
    caterer_id = db.Column(db.Integer, db.ForeignKey('Caterers.caterer_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MealOptionSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    category = fields.Str(validate=validate.Length(max=50))

    @validates('price')
    def validate_price(self, value):
        if value < 0:
            raise ValidationError('Price must be non-negative.')

meal_option_schema = MealOptionSchema()
meal_options_schema = MealOptionSchema(many=True)

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            token = token.replace('Bearer ', '')
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(user_id=data['user_id']).first()
            if not current_user or current_user.role != 'admin':
                return jsonify({'error': 'Unauthorized access'}), 403
        except:
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorator

@app.route('/', endpoint='root')
def root():
    return jsonify({'message': 'Mealy API'})

@app.route('/api/meals', methods=['POST'], endpoint='create_meal')
@token_required
def create_meal(current_user):
    try:
        data = meal_option_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    caterer = Caterer.query.filter_by(user_id=current_user.user_id).first()
    if not caterer:
        return jsonify({'error': 'Caterer profile not found'}), 403
    meal = MealOption(
        caterer_id=caterer.caterer_id,
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        category=data.get('category')
    )
    db.session.add(meal)
    db.session.commit()
    return jsonify(meal_option_schema.dump(meal)), 201

@app.route('/api/meals', methods=['GET'], endpoint='get_meals')
def get_meals():
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    query = MealOption.query
    if category:
        query = query.filter_by(category=category)
    if min_price is not None:
        query = query.filter(MealOption.price >= min_price)
    if max_price is not None:
        query = query.filter(MealOption.price <= max_price)
    meals = query.all()
    return jsonify(meal_options_schema.dump(meals)), 200

@app.route('/api/meals/<int:id>', methods=['GET'], endpoint='get_meal')
def get_meal(id):
    meal = MealOption.query.get_or_404(id)
    return jsonify(meal_option_schema.dump(meal)), 200

@app.route('/api/meals/<int:id>', methods=['PUT'], endpoint='update_meal')
@token_required
def update_meal(current_user, id):
    meal = MealOption.query.get_or_404(id)
    caterer = Caterer.query.filter_by(user_id=current_user.user_id).first()
    if not caterer or meal.caterer_id != caterer.caterer_id:
        return jsonify({'error': 'Unauthorized to modify this meal'}), 403
    try:
        data = meal_option_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    meal.name = data.get('name', meal.name)
    meal.description = data.get('description', meal.description)
    meal.price = data.get('price', meal.price)
    meal.category = data.get('category', meal.category)
    db.session.commit()
    return jsonify(meal_option_schema.dump(meal)), 200

@app.route('/api/meals/<int:id>', methods=['DELETE'], endpoint='delete_meal')
@token_required
def delete_meal(current_user, id):
    meal = MealOption.query.get_or_404(id)
    caterer = Caterer.query.filter_by(user_id=current_user.user_id).first()
    if not caterer or meal.caterer_id != caterer.caterer_id:
        return jsonify({'error': 'Unauthorized to delete this meal'}), 403
    db.session.delete(meal)
    db.session.commit()
    return jsonify({'message': 'Meal deleted'}), 204

@app.route('/api/users', methods=['POST'], endpoint='create_user')
def create_user():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password,
        role='customer'
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201

@app.route('/api/login', methods=['POST'], endpoint='login')
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        token = jwt.encode({'user_id': user.user_id}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(debug=True)
