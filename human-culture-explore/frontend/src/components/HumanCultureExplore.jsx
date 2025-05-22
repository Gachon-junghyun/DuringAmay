// src/components/HumanCultureExplore.jsx
import { ToolItem } from "./ToolItem";
import { FaMapPin } from "react-icons/fa";
import { useState, useRef, useEffect } from "react";
import { useDrag, useDrop } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { Resizable } from "re-resizable";
import { Plus } from "lucide-react";

const CARD_TYPE = "CARD";
const PIN_IMAGE = "https://cdn-icons-png.flaticon.com/512/32/32213.png";
const CARD_IMAGE = "http://localhost:5173/card-image.jpg";

export function SelectedCardModal({ image, onClose, onSave }) {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const img = new Image();
    img.src = image;
    img.onload = () => {
      const maxWidth = window.innerWidth * 0.8;
      const maxHeight = window.innerHeight * 0.8;
      const scale = Math.min(maxWidth / img.width, maxHeight / img.height);
      const displayWidth = img.width * scale;
      const displayHeight = img.height * scale;

      canvas.width = displayWidth;
      canvas.height = displayHeight;
      ctx.drawImage(img, 0, 0, displayWidth, displayHeight);
    };
  }, [image]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") {
        handleSaveAndClose(); // ✅ ESC 키에 저장+닫기
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleSaveAndClose = () => {
    const canvas = canvasRef.current;
    const dataUrl = canvas.toDataURL("image/png");

    if (onSave) onSave(dataUrl); // ✅ 보드로 이미지 보내기
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
      <div className="relative max-w-[90vw] max-h-[90vh] overflow-auto">
        <canvas
          ref={canvasRef}
          onMouseDown={() => setIsDrawing(true)}
          onMouseUp={() => setIsDrawing(false)}
          onMouseMove={(e) => {
            if (!isDrawing) return;
            const canvas = canvasRef.current;
            const ctx = canvas.getContext("2d");
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            ctx.fillStyle = "white";
            ctx.beginPath();
            ctx.arc(x, y, 3, 0, 2 * Math.PI);
            ctx.fill();
          }}
          className="border-4 border-white shadow-lg cursor-crosshair"
          style={{ maxWidth: "100%", maxHeight: "100%" }}
        />

        {/* 닫기 버튼도 저장 후 닫기 */}
        <button
          onClick={handleSaveAndClose}
          className="absolute top-2 right-2 text-white bg-red-500 px-3 py-1 rounded"
        >
          닫기
        </button>
      </div>
    </div>
  );
}

export function DraggableCard({
  id,
  x,
  y,
  title,
  description,
  onMove,
  onRotate,
  rotation = 0,
  zIndex,
  onBringToFront,
  image,
  isPin,
  boardOffset,
  onSelectImage, // ✅ prop 받기
}) {
  const [flipped, setFlipped] = useState(false);

  const [{ isDragging }, dragRef] = useDrag({
    type: CARD_TYPE,
    item: (monitor) => {
      const initialClientOffset = monitor.getInitialClientOffset();
      const initialSourceClientOffset = monitor.getInitialSourceClientOffset();
      const offsetX = initialClientOffset.x - initialSourceClientOffset.x;
      const offsetY = initialClientOffset.y - initialSourceClientOffset.y;

      onBringToFront(id);
      return { id, x, y, offsetX, offsetY };
    },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  });

  return (
    <Resizable
      enable={isPin ? false : undefined}
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
        ref={dragRef}
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
          <FaMapPin color="#e74c3c" size={24} />
        ) : (
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
                onClick={() => {
                  if (!isPin && image && onSelectImage) {
                    onSelectImage(image); // ✅ 부모로 전달해서 ID까지 기억하게 함
                  }
                }}// ✅ 여기 추가!
              />

              </div>

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
  // 이미지 업로드 함수
  const fileInputRef = useRef(null);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const imageURL = URL.createObjectURL(file);

    const newId = cards.length + 1;
    const newCard = {
      id: newId,
      title: `내 엽서 ${newId}`,
      description: "내가 직접 올린 이미지!",
      x: 100 + newId * 20,
      y: 100 + newId * 20,
      rotation: 0,
      image: imageURL,
      zIndex: highestZIndex + 1,
    };

    bringToFront(newId);
    setCards([...cards, newCard]);
  };

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
  const [selectedImage, setSelectedImage] = useState(null); // 이미지 셀렉트 모달
  const [selectedCardId, setSelectedCardId] = useState(null); // 어떤 카드인지 기억


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
            onSelectImage={(img) => {
              setSelectedImage(img);
              setSelectedCardId(card.id); // ✅ 이미지 클릭한 카드의 ID 저장
            }}
            
          />
        ))}
          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-4">
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

            {/* 🔽 이미지 업로드 버튼 추가 */}
            <input
              type="file"
              accept="image/*"
              ref={fileInputRef}
              onChange={handleImageUpload}
              className="hidden"
            />

            <button
              onClick={() => fileInputRef.current.click()}
              className="bg-orange-300 hover:bg-orange-400 text-white px-6 py-3 rounded-full shadow-lg flex items-center gap-2"
            >
              <Plus /> 이미지 엽서 추가
            </button>
          </div>
      </div>
        {/* 오른쪽 카드 인덱스 리스트 */}
        <div className="w-48 bg-white p-4 shadow-md h-screen overflow-y-auto">
          <h2 className="text-sm font-bold text-gray-700 mb-2">카드 목록</h2>
          {cards.map((card) => (
            <div
              key={card.id}
              className="mb-2 cursor-pointer hover:underline text-orange-700"
              onClick={() => {
                bringToFront(card.id); // ✅ card에서 직접 접근
                if (!card.isPin && card.image) {
                  setSelectedImage(card.image); // ✅ card.image 사용
                }
              }}
            >
              {card.title}
            </div>
          ))}
        </div>



        {selectedImage && (
              <SelectedCardModal
                image={selectedImage}
                onClose={() => {
                  setSelectedImage(null);
                  setSelectedCardId(null);
                }}
                onSave={(editedImage) => {
                  setCards((prev) =>
                    prev.map((card) =>
                      card.id === selectedCardId ? { ...card, image: editedImage } : card
                    )
                  );
                }}
              />
            )}

    </div>
  );
}
