// App.jsx

import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import HumanCultureExplore from "./components/HumanCultureExplore";

function App() {
  return (
    <DndProvider backend={HTML5Backend}>
      <HumanCultureExplore />
    </DndProvider>
  );
}

export default App;