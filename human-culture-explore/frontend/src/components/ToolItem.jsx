
// src/components/ToolItem.jsx
import { useDrag } from "react-dnd";

const CARD_TYPE = "CARD";

export function ToolItem({ type }) {
  const [{ isDragging }, dragRef] = useDrag({
    type: CARD_TYPE,
    item: { type },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  });

  return (
    <div
      ref={dragRef}
      className="border rounded p-2 mb-2 text-center bg-gray-100 cursor-move"
      style={{ opacity: isDragging ? 0.5 : 1 }}
    >
      {type}
    </div>
  );
}

