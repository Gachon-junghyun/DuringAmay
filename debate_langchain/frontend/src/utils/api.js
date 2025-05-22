import axios from 'axios';

export const getAIResponse = async ({ topic, messages, currentSpeaker, model, mind }) => {
  try {
    const response = await axios.post('http://localhost:5000/api/debate/next', {
      topic,
      messages,
      currentSpeaker,
      model,
      mind
    });
    return response.data;  // { response: '...', mind: '...' }
  } catch (error) {
    console.error('❌ Flask 통신 실패:', error);
    return { response: '서버 오류: AI 응답을 생성하지 못했습니다.' };
  }
};


export const testAIResponse = async () => {
  const topic = '인공지능은 인간의 창의성을 넘어설 수 있는가?';
  const messages = [
    { senderName: '중재자', content: '오늘의 주제는 ~' },
    { senderName: '참가자 1', content: '찬성 ~' },
    { senderName: '참가자 2', content: '반대 ~' }
  ];
  const currentSpeaker = 'moderator';
  const model = 'claude';
  const mind = '질문을 유도하고 분위기를 조율하려 함';  // 예시

  const res = await getAIResponse({ topic, messages, currentSpeaker, model, mind });
  console.log(res.response);
  console.log(res.mind);  // 🧠 업데이트된 mind도 확인 가능
};
