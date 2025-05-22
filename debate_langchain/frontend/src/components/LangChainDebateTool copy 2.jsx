import { useState, useEffect } from 'react';
import { Trash2, Send, Plus, Settings, MessageCircle } from 'lucide-react';
import { getAIResponse } from '../utils/api'; // utils 경로 확인 필요

// AI 모델 기본 옵션
const AI_MODELS = [
  { id: 'gemini', name: 'Gemini' },
  { id: 'claude', name: 'Claude' },
  { id: 'gpt4', name: 'GPT-4' },
  { id: 'llama3', name: 'Llama 3' },
  { id: 'mistral', name: 'Mistral' }
];

// 색상 테마
const COLORS = {
  moderator: '#6366f1', // 인디고
  debater1: '#ec4899', // 핑크
  debater2: '#14b8a6', // 틸
  debater3: '#f59e0b', // 앰버
  debater4: '#8b5cf6', // 보라
};

export default function LangChainDebateTool() {
  // 상태 관리
  const [topic, setTopic] = useState('인공지능은 인간의 창의성을 넘어설 수 있는가?');
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [debaters, setDebaters] = useState([
    { id: 1, name: '참가자 1', model: 'claude', stance: '찬성', color: COLORS.debater1 },
    { id: 2, name: '참가자 2', model: 'gpt4', stance: '반대', color: COLORS.debater2 }
  ]);
  const [moderator, setModerator] = useState({ model: 'gemini', name: '중재자', color: COLORS.moderator });
  const [currentSpeaker, setCurrentSpeaker] = useState('moderator');

  // 토론 시작 시 중재자가 첫 메시지를 보냄
  useEffect(() => {
    if (messages.length === 0) {
      const initialMessage = {
        id: Date.now(),
        content: `안녕하세요, 오늘의 토론 주제는 "${topic}"입니다. 각 참가자는 자신의 입장을 3분 이내로 소개해 주시기 바랍니다. 먼저 찬성 측부터 시작하겠습니다.`,
        sender: 'moderator',
        senderName: moderator.name,
        timestamp: new Date().toLocaleTimeString(),
        color: moderator.color
      };
      setMessages([initialMessage]);
    }
  }, []);

  const sendMessage = async () => {
     if (newMessage.trim() === '') return;
   
     let sender, senderName, color;
     
     if (currentSpeaker === 'moderator') {
       sender = 'moderator';
       senderName = moderator.name;
       color = moderator.color;
     } else {
       const currentDebater = debaters.find(d => d.id === parseInt(currentSpeaker));
       sender = `debater${currentDebater.id}`;
       senderName = currentDebater.name;
       color = currentDebater.color;
     }
   
     const userMsg = {
       id: Date.now(),
       content: newMessage,
       sender,
       senderName,
       timestamp: new Date().toLocaleTimeString(),
       color
     };
   
     // 1. 사용자 메시지 추가
     const updatedMessages = [...messages, userMsg];
     setMessages(updatedMessages);
     setNewMessage('');
   
     // 2. Flask API 호출
     const model =
       currentSpeaker === 'moderator'
         ? moderator.model
         : debaters.find(d => d.id === parseInt(currentSpeaker))?.model || 'gpt4';
   
     const res = await getAIResponse({
       topic,
       messages: updatedMessages,
       currentSpeaker,
       model
     });
   
     // 3. AI 응답 메시지 추가
     const aiMsg = {
       id: Date.now() + 1,
       content: res.response,
       sender,
       senderName,
       timestamp: new Date().toLocaleTimeString(),
       color
     };
   
     setMessages(prev => [...prev, aiMsg]);
   };
   

  // 발언자 변경 함수
  const changeSpeaker = (speakerId) => {
    setCurrentSpeaker(speakerId);
  };

  // 참가자 추가 함수
  const addDebater = () => {
    if (debaters.length >= 4) return; // 최대 4명까지
    
    const newId = Math.max(...debaters.map(d => d.id), 0) + 1;
    const newDebater = {
      id: newId,
      name: `참가자 ${newId}`,
      model: 'claude',
      stance: '관점 입력',
      color: COLORS[`debater${newId}`]
    };
    
    setDebaters([...debaters, newDebater]);
  };

  // 참가자 제거 함수
  const removeDebater = (id) => {
    if (debaters.length <= 2) return; // 최소 2명은 유지
    setDebaters(debaters.filter(d => d.id !== id));
    if (currentSpeaker === id.toString()) {
      setCurrentSpeaker('moderator');
    }
  };

  // 참가자 설정 변경 함수
  const updateDebater = (id, field, value) => {
    setDebaters(debaters.map(d => 
      d.id === id ? { ...d, [field]: value } : d
    ));
  };

  // 중재자 설정 변경 함수
  const updateModerator = (field, value) => {
    setModerator({ ...moderator, [field]: value });
  };

  return (
    <div className="flex flex-col h-screen max-h-screen bg-gray-100">
      {/* 헤더 */}
      <header className="bg-white shadow p-4">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-800">LangChain 토론 도구</h1>
          <button 
            onClick={() => setIsSettingsOpen(!isSettingsOpen)}
            className="p-2 rounded-full hover:bg-gray-200"
          >
            <Settings size={20} />
          </button>
        </div>
        <div className="mt-2">
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
            placeholder="토론 주제 입력..."
          />
        </div>
      </header>

      {/* 메인 컨텐츠 영역 */}
      <div className="flex flex-1 overflow-hidden">
        {/* 설정 패널 (열릴 때만 표시) */}
        {isSettingsOpen && (
          <div className="w-64 bg-white shadow-md p-4 overflow-y-auto">
            <h2 className="font-bold mb-4">토론 설정</h2>
            
            {/* 중재자 설정 */}
            <div className="mb-6 p-3 bg-gray-50 rounded">
              <h3 className="font-semibold mb-2 flex items-center">
                <MessageCircle size={16} className="mr-1" />
                중재자 설정
              </h3>
              <div className="mb-2">
                <label className="block text-sm mb-1">이름</label>
                <input
                  type="text"
                  value={moderator.name}
                  onChange={(e) => updateModerator('name', e.target.value)}
                  className="w-full p-1 text-sm border rounded"
                />
              </div>
              <div>
                <label className="block text-sm mb-1">모델</label>
                <select
                  value={moderator.model}
                  onChange={(e) => updateModerator('model', e.target.value)}
                  className="w-full p-1 text-sm border rounded"
                >
                  {AI_MODELS.map(model => (
                    <option key={model.id} value={model.id}>{model.name}</option>
                  ))}
                </select>
              </div>
            </div>
            
            {/* 참가자 설정 */}
            <h3 className="font-semibold mb-2">참가자 설정</h3>
            {debaters.map(debater => (
              <div key={debater.id} className="mb-4 p-3 bg-gray-50 rounded">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium text-sm">{debater.name}</span>
                  <button 
                    onClick={() => removeDebater(debater.id)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
                <div className="mb-2">
                  <label className="block text-sm mb-1">이름</label>
                  <input
                    type="text"
                    value={debater.name}
                    onChange={(e) => updateDebater(debater.id, 'name', e.target.value)}
                    className="w-full p-1 text-sm border rounded"
                  />
                </div>
                <div className="mb-2">
                  <label className="block text-sm mb-1">모델</label>
                  <select
                    value={debater.model}
                    onChange={(e) => updateDebater(debater.id, 'model', e.target.value)}
                    className="w-full p-1 text-sm border rounded"
                  >
                    {AI_MODELS.map(model => (
                      <option key={model.id} value={model.id}>{model.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm mb-1">입장/관점</label>
                  <input
                    type="text"
                    value={debater.stance}
                    onChange={(e) => updateDebater(debater.id, 'stance', e.target.value)}
                    className="w-full p-1 text-sm border rounded"
                  />
                </div>
              </div>
            ))}
            
            {/* 참가자 추가 버튼 */}
            {debaters.length < 4 && (
              <button 
                onClick={addDebater}
                className="w-full py-2 flex items-center justify-center text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                <Plus size={16} className="mr-1" /> 참가자 추가
              </button>
            )}
          </div>
        )}

        {/* 메시지 영역 */}
        <div className="flex-1 flex flex-col">
          {/* 메시지 목록 */}
          <div className="flex-1 p-4 overflow-y-auto">
            {messages.map(message => (
              <div 
                key={message.id} 
                className={`mb-4 ${message.sender === 'moderator' ? 'pl-4 border-l-4' : 'pl-4 border-l-4'}`}
                style={{ borderColor: message.color }}
              >
                <div className="flex items-center">
                  <span className="font-bold" style={{ color: message.color }}>
                    {message.senderName}
                  </span>
                  <span className="ml-2 text-xs text-gray-500">{message.timestamp}</span>
                </div>
                <div className="mt-1 text-gray-800">{message.content}</div>
              </div>
            ))}
          </div>

          {/* 발언자 선택 */}
          <div className="bg-gray-100 p-2 flex flex-wrap">
            <button
              onClick={() => changeSpeaker('moderator')}
              className={`mr-2 mb-2 px-3 py-1 rounded text-sm ${
                currentSpeaker === 'moderator' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-white border hover:bg-gray-50'
              }`}
            >
              {moderator.name}
            </button>
            
            {debaters.map(debater => (
              <button
                key={debater.id}
                onClick={() => changeSpeaker(debater.id.toString())}
                className={`mr-2 mb-2 px-3 py-1 rounded text-sm ${
                  currentSpeaker === debater.id.toString() 
                    ? 'text-white' 
                    : 'bg-white border hover:bg-gray-50'
                }`}
                style={{ 
                  backgroundColor: currentSpeaker === debater.id.toString() 
                    ? debater.color 
                    : undefined 
                }}
              >
                {debater.name}
              </button>
            ))}
          </div>

          {/* 메시지 입력 */}
          <div className="bg-white p-4 border-t">
            <div className="flex">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                className="flex-1 p-2 border border-gray-300 rounded-l"
                placeholder={`${currentSpeaker === 'moderator' ? moderator.name : debaters.find(d => d.id === parseInt(currentSpeaker))?.name}로 메시지 입력...`}
              />
              <button
                onClick={sendMessage}
                className="bg-blue-500 text-white px-4 rounded-r hover:bg-blue-600"
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}