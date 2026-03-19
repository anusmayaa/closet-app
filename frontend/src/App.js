import React, { useState } from 'react';
import Navbar from './components/Navbar';
import UploadForm from './components/UploadForm';
import ClosetGrid from './components/ClosetGrid';
import OutfitGenerator from './components/OutfitGenerator';
import Lookbook from './components/Lookbook';
import './App.css';

function App() {
  const [activePage, setActivePage] = useState('wardrobe');
  const [refreshGrid, setRefreshGrid] = useState(false);

  const handleUploadSuccess = () => {
    setRefreshGrid(prev => !prev);
  };

  return (
    <div className="app">
      <Navbar activePage={activePage} setActivePage={setActivePage} />

      <main className="main">
        {activePage === 'wardrobe' && (
          <div className="wardrobe-layout">
            <UploadForm onUploadSuccess={handleUploadSuccess} />
            <ClosetGrid refresh={refreshGrid} />
          </div>
        )}

        {activePage === 'generator' && (
          <OutfitGenerator />
        )}

        {activePage === 'lookbook' && (
          <Lookbook />
        )}
      </main>
    </div>
  );
}

export default App;