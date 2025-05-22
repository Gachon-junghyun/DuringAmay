from flask import Flask, request, jsonify
from flask_cors import CORS

from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.openai_functions import create_structured_output_chain
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# ✅ 환경 변수 로드
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

# 💡 주제 설정
TOPIC = "인공지능은 인간의 창의성을 넘어설 수 있는가?"

# ✅ Pydantic BaseModel 정의
class DebateResponse(BaseModel):
    respond: str
    mind: str

# 🎙️ 토론자 프롬프트 (JSON 출력 유도)
debater_prompt = PromptTemplate(
    input_variables=["topic", "chat_history", "mind"],
    template="""
당신은 열정적인 토론자입니다.

주제: "{topic}"
접근 관점 (mind): "{mind}"

지금까지의 대화:
{chat_history}

위의 관점(mind)을 바탕으로, 이 주제에 대해 논리적으로 반응(respond)하십시오.
아래 형식으로 JSON으로 출력하십시오:

{{
  "respond": "...당신의 주장...",
  "mind": "...이 주장에 담긴 전략/사고 방식 요약..."
}}
"""
)

# ⚖️ 중재자 프롬프트
moderator_prompt = PromptTemplate(
    input_variables=["topic", "chat_history"],
    template="""
당신은 중립적인 중재자입니다.
주제: "{topic}"

{chat_history}

간략하게 요약하고 다음 발언자를 지목해주세요.
"""
)

# 🤖 토론자 설정
NUM_DEBATERS = 2
temperatures = [0.7] * NUM_DEBATERS
structured_debater_chains = []
debater_memories = []

for i in range(NUM_DEBATERS):
    llm = ChatOpenAI(model_name="gpt-4", temperature=temperatures[i], openai_api_key=openai_api_key)
    memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
    chain = create_structured_output_chain(
        output_schema=DebateResponse,
        llm=llm,
        prompt=debater_prompt,
    )
    structured_debater_chains.append(chain)
    debater_memories.append(memory)

# 🧑‍⚖️ 중재자 설정
moderator_llm = ChatOpenAI(model_name="gpt-4", temperature=0.3, openai_api_key=openai_api_key)
moderator_memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
moderator_chain = create_structured_output_chain(
    output_schema=DebateResponse,  # 중재자도 동일한 구조 사용할 수 있음
    llm=moderator_llm,
    prompt=moderator_prompt
)

# 🧠 상태 관리용 전역 라운드
current_round = 1
max_rounds = 5

@app.route('/api/debate/next', methods=['POST'])
def debate_next():
    data = request.get_json()
    topic = data.get('topic', TOPIC)
    messages = data.get('messages', [])
    current_speaker = data.get('currentSpeaker')
    model = data.get('model')
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
    app.run(debug=True)
