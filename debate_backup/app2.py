from flask import Flask, request, jsonify
from flask_cors import CORS
from config import db
from db import User, Debate, Message
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 409
    
    user = User(username=data['username'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        return jsonify({'message': 'Login success'})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/debates', methods=['POST'])
def create_debate():
    data = request.json
    debate = Debate(topic=data['topic'])
    db.session.add(debate)
    db.session.commit()
    return jsonify({'message': 'Debate created', 'debate_id': debate.id})

@app.route('/debates/<debate_id>/messages', methods=['POST'])
def add_message(debate_id):
    data = request.json
    message = Message(
        sender_name=data['sender_name'],
        content=data['content'],
        debate_id=debate_id
    )
    db.session.add(message)
    db.session.commit()
    return jsonify({'message': 'Message added'})

@app.route('/debates', methods=['GET'])
def list_debates():
    debates = Debate.query.all()
    return jsonify([
        {'id': d.id, 'topic': d.topic, 'created_at': d.created_at.isoformat()}
        for d in debates
    ])

@app.route('/debates/<debate_id>/messages', methods=['GET'])
def get_messages(debate_id):
    messages = Message.query.filter_by(debate_id=debate_id).all()
    return jsonify([
        {'sender_name': m.sender_name, 'content': m.content, 'timestamp': m.timestamp.isoformat()}
        for m in messages
    ])

if __name__ == '__main__':
    app.run(debug=True)
