// src/components/HumanCultureExplore.jsx
import { ToolItem } from "./ToolItem"; // 상단에 추가

import { FaMapPin } from "react-icons/fa";

import { useState, useRef } from "react";
import { useDrag, useDrop } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { Resizable } from "re-resizable";
import { Plus } from "lucide-react";

const CARD_TYPE = "CARD";
const PIN_IMAGE = "https://cdn-icons-png.flaticon.com/512/32/32213.png";
const CARD_IMAGE = "http://localhost:5173/card-image.jpg";



function DraggableCard({ id, x, y, title, description, onMove, onRotate, rotation = 0, zIndex, onBringToFront, image, isPin, boardOffset }) {

  const [flipped, setFlipped] = useState(false);

  const [{ isDragging }, dragRef] = useDrag({
    type: CARD_TYPE,
    item: (monitor) => {
      const initialClientOffset = monitor.getInitialClientOffset();
      const initialSourceClientOffset = monitor.getInitialSourceClientOffset();
      const offsetX = initialClientOffset.x - initialSourceClientOffset.x;
      const offsetY = initialClientOffset.y - initialSourceClientOffset.y;
  
      onBringToFront(id);
      return { id, x, y, offsetX, offsetY }; // 👈 오프셋 추가!
    },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  });
  
  

  
  const [, dropRef] = useDrop({
    accept: CARD_TYPE,
    drop: (item, monitor) => {
      const clientOffset = monitor.getClientOffset();
      const boardRect = boardRef.current?.getBoundingClientRect();
      if (!clientOffset || !boardRect) return;
    
      const offsetX = item.offsetX ?? 0;
      const offsetY = item.offsetY ?? 0;
    
      const newX = clientOffset.x - boardRect.left - offsetX - boardOffset.x;
      const newY = clientOffset.y - boardRect.top - offsetY - boardOffset.y;
    
      if (item.id) {
        moveCard(item.id, newX, newY);
      } else {
        const newId = cards.length + 1;
        const newCard = {
          id: newId,
          title: item.type,
          description: `${item.type} 설명`,
          x: newX,
          y: newY,
          rotation: 0,
          zIndex: highestZIndex + 1,
        };
    
        if (item.type === "pin") {
          newCard.description = "";
          newCard.image = PIN_IMAGE;
          newCard.isPin = true;
        }
    
        bringToFront(newId);
        setCards((prev) => [...prev, newCard]);
      }
    },
  });
  

  return (
          <Resizable
        enable={isPin ? false : undefined} // ✅ 핀은 리사이즈 불가
        defaultSize={{ width: 240, height: 140 }}
        minWidth={120}
        minHeight={80}
        style={{
          position: "absolute",
          left: x + boardOffset.x,
          top: y + boardOffset.y,          
          transform: `rotate(${rotation}deg)`,
          opacity: isDragging ? 0.5 : 1,
          cursor: "grab",
          zIndex: zIndex || 1,
        }}
      >
        <div
          ref={(node) => dragRef(node)} 
          style={{ width: "100%", height: "100%" }}
          onClick={() => onBringToFront(id)}
          onWheel={(e) => {
            if (!isPin) {
              e.preventDefault();
              onRotate(id, rotation + (e.deltaY > 0 ? 10 : -10));
            }
          }}
          onMouseEnter={!isPin ? () => setFlipped(true) : undefined}
          onMouseLeave={!isPin ? () => setFlipped(false) : undefined}
        >
          {isPin ? (
            // ✅ 핀 전용 렌더링
            <FaMapPin color="#e74c3c" size={24} />
          
          ) : (
            // 기존 카드 렌더링
            <div style={{ perspective: "1000px", width: "100%", height: "100%" }}>
              <div
                style={{
                  position: "relative",
                  width: "100%",
                  height: "100%",
                  transform: flipped ? "rotateY(180deg)" : "rotateY(0deg)",
                  transformStyle: "preserve-3d",
                  transition: "transform 0.5s",
                }}
              >
                {/* Front */}
                <div
                  style={{
                    position: "absolute",
                    width: "100%",
                    height: "100%",
                    backfaceVisibility: "hidden",
                    backgroundColor: "white",
                    border: "1px solid #e5e7eb",
                    borderRadius: "0.375rem",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                  }}
                >
                  <img
                    src={image}
                    alt="card front"
                    style={{
                      width: "100%",
                      height: "100%",
                      objectFit: "cover",
                      borderRadius: "0.375rem",
                    }}
                  />
                </div>

                {/* Back */}
                <div
                  style={{
                    position: "absolute",
                    width: "100%",
                    height: "100%",
                    backfaceVisibility: "hidden",
                    backgroundColor: "white",
                    border: "1px solid #fdba74",
                    borderRadius: "0.375rem",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                    padding: "1rem",
                    transform: "rotateY(180deg)",
                  }}
                >
                  <h2 style={{ fontWeight: "bold", color: "#7c2d12" }}>{title}</h2>
                  <p style={{ color: "#9a3412", fontSize: "0.875rem" }}>{description}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </Resizable>

  );
}

export default function HumanCultureExplore() {

  // 배경 이동 변수

  const [boardOffset, setBoardOffset] = useState({ x: 0, y: 0 });
  const isDraggingBoard = useRef(false);
  const lastMousePosition = useRef(null);

  const handleMouseDown = (e) => {
    // 카드 위가 아닌 빈 배경 클릭일 때만
    if (e.target === boardRef.current) {
      isDraggingBoard.current = true;
      lastMousePosition.current = { x: e.clientX, y: e.clientY };
    }
  };
  
  const handleMouseMove = (e) => {
    if (!isDraggingBoard.current) return;
    const dx = e.clientX - lastMousePosition.current.x;
    const dy = e.clientY - lastMousePosition.current.y;
  
    setBoardOffset((prev) => ({
      x: prev.x + dx,
      y: prev.y + dy,
    }));
  
    lastMousePosition.current = { x: e.clientX, y: e.clientY };
  };
  
  const handleMouseUp = () => {
    isDraggingBoard.current = false;
    lastMousePosition.current = null;
  };
  


  const boardRef = useRef(null);
  // useState 초기 카드 정의 수정
  const [cards, setCards] = useState([
    {
      id: 1,
      title: "전통시장 탐방",
      description: "지역 시장에서 사람들과 교류하며 문화 체험",
      x: 100,
      y: 100,
      rotation: 0,
      zIndex: 1, // ✅ 추가
    },
  ]);

  const [highestZIndex, setHighestZIndex] = useState(1); // ⭐️ 추가


  const moveCard = (id, x, y) => {
    setCards((prev) => prev.map((card) => (card.id === id ? { ...card, x, y } : card)));
  };

  const rotateCard = (id, rotation) => {
    setCards((prev) => prev.map((card) => (card.id === id ? { ...card, rotation } : card)));
  };

  const bringToFront = (id) => {
    setHighestZIndex((prev) => prev + 1);
    setCards((prev) =>
      prev.map((card) =>
        card.id === id ? { ...card, zIndex: highestZIndex + 1 } : card
      )
    );
  }; // ⭐️ 여기에 붙이기
  

  const [, dropRef] = useDrop({
    accept: [CARD_TYPE],
    drop: (item, monitor) => {
      const clientOffset = monitor.getClientOffset();
      const boardRect = boardRef.current?.getBoundingClientRect();
      if (!clientOffset || !boardRect) return;
    
      const offsetX = item.offsetX ?? 0;
      const offsetY = item.offsetY ?? 0;
    
      const newX = clientOffset.x - boardRect.left - offsetX;
      const newY = clientOffset.y - boardRect.top - offsetY;
    
      if (item.id) {
        moveCard(item.id, newX, newY);
      } else {
        const newId = cards.length + 1;
        const newCard = {
          id: newId,
          title: item.type,
          description: `${item.type} 설명`,
          x: newX,
          y: newY,
          rotation: 0,
          zIndex: highestZIndex + 1,
        };
    
        if (item.type === "pin") {
          newCard.description = "";
          newCard.image = PIN_IMAGE;
          newCard.isPin = true;
        }
    
        bringToFront(newId);
        setCards((prev) => [...prev, newCard]);
      }
    },
  });
  

  return (
      <div className="flex">
        {/* 왼쪽 도구 패널 */}
        <div className="w-32 bg-white p-4 shadow-md h-screen">
          <h2 className="text-sm font-bold text-gray-700 mb-2">도구</h2>
          {["pin", "magnet", "clip"].map((tool) => (
            <ToolItem key={tool} type={tool} />
          ))}
        </div>

        {/* 메인 보드 */}
        <div
          ref={(node) => {
            boardRef.current = node;
            dropRef(node);
          }}
          className="flex-1 min-h-screen p-6 bg-amber-50 relative overflow-hidden"
          onMouseDown={handleMouseDown}     // ⬅️ 여기 추가
          onMouseMove={handleMouseMove}     // ⬅️ 여기 추가
          onMouseUp={handleMouseUp}         // ⬅️ 여기 추가
        >
          <h1 className="text-4xl font-bold text-orange-800 text-center mb-6">
            ✨ 엽서 보드 탐방 ✨
          </h1>

          {cards.map((card) => (
            <DraggableCard
              key={card.id}
              {...card}
              onMove={moveCard}
              onRotate={rotateCard}
              onBringToFront={bringToFront} // 앞으로 보내기 기능
              boardOffset={boardOffset} // 배경 오프셋 보내기
            />
          ))}

          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
            <button
              onClick={() => {
                const newId = cards.length + 1;
                setCards([
                  ...cards,
                  {
                    id: newId,
                    title: `새 활동 ${newId}`,
                    description: "활동 내용을 작성하세요.",
                    x: 100 + newId * 20,
                    y: 100 + newId * 20,
                    rotation: 0,
                    image: CARD_IMAGE,
                  },
                ]);
              }}
              className="bg-orange-400 hover:bg-orange-500 text-white px-6 py-3 rounded-full shadow-lg flex items-center gap-2"
            >
              <Plus /> 활동 추가
            </button>
          </div>
        </div>
      </div>
  );
}
