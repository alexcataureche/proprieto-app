import React, { useState } from 'react';
import Navbar from './components/Navbar';
import GestiuneImobile from './views/GestiuneImobile';
import GestiuneContracte from './views/GestiuneContracte';
import DashboardFiscal from './views/DashboardFiscal';

function App() {
  const [activeView, setActiveView] = useState('imobile');

  const renderView = () => {
    switch (activeView) {
      case 'imobile':
        return <GestiuneImobile />;
      case 'contracte':
        return <GestiuneContracte />;
      case 'dashboard':
        return <DashboardFiscal />;
      default:
        return <GestiuneImobile />;
    }
  };

  return (
    <div className="min-h-screen bg-app-bg">
      <Navbar activeView={activeView} onNavigate={setActiveView} />
      <main>{renderView()}</main>
    </div>
  );
}

export default App;
