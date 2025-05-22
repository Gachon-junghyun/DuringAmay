import { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus } from 'lucide-react';

// 카드 컴포넌트
function Card({ children, className }) {
  return (
    <div className={`p-4 bg-white rounded-2xl shadow-md transform transition-all duration-300 hover:scale-105 hover:rotate-[1deg] hover:shadow-2xl hover:animate-wiggle ${className}`}>
      {children}
    </div>
  );
}

function CardContent({ children, className }) {
  return <div className={className}>{children}</div>;
}

function Button({ children, ...props }) {
  return (
    <button
      {...props}
      className="bg-orange-400 hover:bg-orange-500 hover:scale-105 hover:shadow-xl transition-all duration-200 text-white px-6 py-4 rounded-full shadow-lg flex items-center gap-2"
    >
      {children}
    </button>
  );
}

export default function HumanCultureExplore() {
  const [activities, setActivities] = useState([
    // 🧡 예시 카드 하나 추가
    {
      id: 0,
      title: '🗺️ 전통시장 탐방',
      description: '도시의 오래된 전통시장을 방문하고, 지역 상인과의 대화를 통해 문화를 체험합니다.'
    }
  ]);

  useEffect(() => {
    axios.get('/api/activities')
      .then(res => {
        const data = Array.isArray(res.data) ? res.data : [];
        setActivities(prev => [...prev, ...data]); // 예시 카드 유지 + API 추가
      })
      .catch(err => console.error('활동 불러오기 실패:', err));
  }, []);

  const addActivity = async () => {
    const newActivity = {
      title: `새 활동 ${activities.length + 1}`,
      description: '활동 내용을 작성하세요.'
    };
    try {
      const res = await axios.post('/api/activities', newActivity);
      setActivities(prev => [...prev, res.data]);
    } catch (err) {
      console.error('활동 추가 실패:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-100 to-yellow-50 py-10 px-4">
      <h1 className="text-5xl font-extrabold text-center text-orange-800 mb-10 tracking-tight">
        ✨ 인간문화탐방말출계획 ✨
      </h1>

      {activities.length === 0 && (
        <p className="text-center text-orange-600 text-lg mb-6 animate-pulse">
          아직 활동이 없습니다. 아래 버튼으로 새 활동을 추가해보세요!
        </p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {Array.isArray(activities) && activities.map((activity) => (
          <Card key={activity.id} className="bg-yellow-100 border-dashed border-2 border-orange-300">
            <CardContent className="p-4">
              <h2 className="text-xl font-bold text-orange-900 mb-2">{activity.title}</h2>
              <p className="text-orange-700">{activity.description}</p>
            </CardContent>
          </Card>
        ))}

        <div className="flex items-center justify-center">
          <Button onClick={addActivity}>
            <Plus /> 활동 추가
          </Button>
        </div>
      </div>
    </div>
  );
}
