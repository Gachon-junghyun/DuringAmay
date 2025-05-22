# 📁 app.py
from flask import Flask, request, jsonify
from config import init_extensions, db
from db import User
from auth import auth_bp
from chains import create_debate_chains, create_moderator_chain, TOPIC

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///debate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_extensions(app)
app.register_blueprint(auth_bp)

structured_debater_chains, debater_memories = create_debate_chains()
moderator_chain, moderator_memory = create_moderator_chain()

current_round = 1
max_rounds = 12

@app.route('/api/debate/next', methods=['POST'])
def debate_next():
    data = request.get_json()
    topic = data.get('topic', TOPIC)
    messages = data.get('messages', [])
    current_speaker = data.get('currentSpeaker')
    mind = data.get('mind', '')

    chat_history = "\n".join([f"[{m['senderName']}] {m['content']}" for m in messages])

    if current_speaker == "moderator":
        response_obj = moderator_chain.run(topic=topic, chat_history=chat_history)
        return jsonify({"response": response_obj.respond, "mind": response_obj.mind})
    else:
        debater_id = int(current_speaker) - 1
        chain = structured_debater_chains[debater_id]
        response_obj = chain.run(topic=topic, chat_history=chat_history, mind=mind)
        return jsonify({"response": response_obj.respond, "mind": response_obj.mind})

@app.route('/api/debate/advance_round', methods=['POST'])
def advance_round():
    global current_round
    if current_round < max_rounds:
        current_round += 1
    return jsonify({"round": current_round})

@app.route('/api/debate/reset', methods=['POST'])
def reset_debate():
    global current_round
    current_round = 1
    moderator_memory.clear()
    for mem in debater_memories:
        mem.clear()
    return jsonify({"status": "reset complete"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
