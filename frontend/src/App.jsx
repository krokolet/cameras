// App.js
import React, { useEffect, useState } from 'react';
import Camera from './components/Camera';
import { getCameras } from './services/api';

function App() {
  const [cameras, setCameras] = useState([]);

  useEffect(() => {
    const fetchCameras = async () => {
      const response = await getCameras();
      const data = await response.json();
      setCameras(Object.keys(data));
    };
    
    fetchCameras();
    const interval = setInterval(fetchCameras, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app">
      <h1>Система видеонаблюдения</h1>
      <div className="camera-grid">
        {cameras.map(id => (
          <Camera key={id} cameraId={id} />
        ))}
      </div>
    </div>
  );
}

export default App;