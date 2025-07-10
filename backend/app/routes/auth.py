from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password or not email:
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    new_user = User(
        user_id=str(uuid.uuid4()),
        username=username,
        password=generate_password_hash(password),
        email=email
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user': {
            'user_id': new_user.user_id,
            'username': new_user.username,
            'email': new_user.email
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email
        }
    }), 200