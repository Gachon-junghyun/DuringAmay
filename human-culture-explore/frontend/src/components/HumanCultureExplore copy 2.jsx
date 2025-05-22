import { useState } from "react";
import { DndProvider, useDrag, useDrop } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { Plus } from "lucide-react";

import { ResizableBox } from "react-resizable";
import "react-resizable/css/styles.css"; // 크기 조절 스타일

const CARD_TYPE = "CARD";

function DraggableCard({ id, index, moveCard, title, description }) {
     const [flipped, setFlipped] = useState(false);
   
     const [, ref] = useDrag({
       type: CARD_TYPE,
       item: { id, index },
     });
   
     const [, drop] = useDrop({
       accept: CARD_TYPE,
       hover(item) {
         if (item.index !== index) {
           moveCard(item.index, index);
           item.index = index;
         }
       },
     });
   
     return (
       <ResizableBox
         width={240}
         height={140}
         minConstraints={[160, 100]}
         maxConstraints={[400, 300]}
         resizeHandles={["se"]}
       >
         <div
           ref={(node) => ref(drop(node))}
           onMouseEnter={() => setFlipped(true)}
           onMouseLeave={() => setFlipped(false)}
           className="w-full h-full perspective-1000"
         >
           <div
             className={`relative w-full h-full transition-transform duration-500 transform ${
               flipped ? "rotate-y-180" : ""
             }`}
             style={{ transformStyle: "preserve-3d" }}
           >
             {/* 앞면 (이미지) */}
            <div className="absolute w-full h-full backface-hidden shadow-lg rounded-md overflow-hidden border border-gray-200">
              <div className="absolute top-1 left-1 w-3 h-3 bg-red-400 rounded-full shadow-md z-10" />
              <img
                src="/card-image.jpg"
                alt="card front"
                className="absolute inset-0 w-full h-full object-cover"
              />
            </div>

   
             {/* 뒷면 (글 내용) */}
             <div className="absolute w-full h-full backface-hidden bg-white border border-orange-300 shadow-lg rounded-md p-4 rotate-y-180">
               <h2 className="font-bold text-orange-900">{title}</h2>
               <p className="text-orange-700 text-sm">{description}</p>
             </div>
           </div>
         </div>
       </ResizableBox>
     );
   }
   
   
export default function PostcardBoard() {

  const [backgroundImage, setBackgroundImage] = useState('/board-background.jpg');

  const [cards, setCards] = useState([
    {
      id: 1,
      title: "전통시장 탐방",
      description: "지역 시장에서 사람들과 교류하며 문화 체험",
    },
  ]);

  const moveCard = (from, to) => {
    const updated = [...cards];
    const [moved] = updated.splice(from, 1);
    updated.splice(to, 0, moved);
    setCards(updated);
  };

  const addCard = () => {
    const newId = cards.length + 1;
    setCards([
      ...cards,
      { id: newId, title: `새 활동 ${newId}`, description: "활동 내용을 작성하세요." },
    ]);
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div
          style={{
          backgroundImage: `url(${backgroundImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          }}
          className="min-h-screen py-10 px-6"
          >
          <div
          className="w-full max-w-[90vw] h-[80vh] mx-auto bg-amber-50/90 p-8 rounded-xl shadow-2xl border border-orange-200 overflow-auto"
          >
          <h1 className="text-4xl font-bold text-orange-800 text-center mb-6">
            ✨ 엽서 보드 탐방 ✨
          </h1>

          <div className="flex flex-wrap gap-6 justify-center">
            {cards.map((card, i) => (
              <DraggableCard
                key={card.id}
                id={card.id}
                index={i}
                moveCard={moveCard}
                title={card.title}
                description={card.description}
              />
            ))}
          </div>

          <div className="flex justify-center mt-8">
            <button
              onClick={addCard}
              className="bg-orange-400 hover:bg-orange-500 text-white px-6 py-3 rounded-full shadow-lg flex items-center gap-2"
            >
              <Plus /> 활동 추가
            </button>
          </div>
        </div>
      </div>
    </DndProvider>
  );
}
