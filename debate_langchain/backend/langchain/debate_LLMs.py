
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
import os

# 🔐 OpenAI API 키 설정
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


# 💡 주제와 라운드 설정
TOPIC = "인공지능은 인간의 창의성을 넘어설 수 있는가?"
NUM_ROUNDS = 2
NUM_DEBATERS = 3

# 🎙️ 토론자 프롬프트
debater_prompt = PromptTemplate(
    input_variables=["topic", "chat_history"],
    template="""
당신은 열정적인 토론자입니다.
주제: "{topic}"
지금까지의 대화:
{chat_history}

당신의 입장을 말해주세요.
"""
)

# ⚖️ 중재자 프롬프트
moderator_prompt = PromptTemplate(
    input_variables=["topic", "chat_history"],
    template="""
당신은 중립적인 중재자입니다.
주제: "{topic}"
지금까지의 토론:
{chat_history}

간략하게 요약하고 다음 발언자를 지목해주세요.
"""
)

# 🤖 GPT-4 토론자 구성
temperatures = [0.6, 0.65, 0.7]
debater_chains = []
for i in range(NUM_DEBATERS):
    llm = ChatOpenAI(model_name="gpt-4", temperature=temperatures[i], openai_api_key=openai_api_key)
    memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
    chain = LLMChain(llm=llm, prompt=debater_prompt, memory=memory, verbose=False)
    debater_chains.append(chain)

# 🧑‍⚖️ 중재자 구성
moderator_llm = ChatOpenAI(model_name="gpt-4", temperature=0.3, openai_api_key=openai_api_key)
moderator_memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
moderator_chain = LLMChain(
    llm=moderator_llm, prompt=moderator_prompt, memory=moderator_memory, verbose=False
)

# 🏁 토론 실행
print(f"💬 주제: {TOPIC}\n")

for round_num in range(NUM_ROUNDS):
    print(f"🔁 Round {round_num + 1}")
    for i, chain in enumerate(debater_chains):
        response = chain.run(topic=TOPIC)
        print(f"[토론자 {i+1}] {response}\n")
        moderator_memory.chat_memory.add_user_message(f"[토론자 {i+1}] {response}")

    mod_response = moderator_chain.run(topic=TOPIC)
    print(f"[중재자] {mod_response}\n")
