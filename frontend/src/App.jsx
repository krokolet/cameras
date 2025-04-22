// App.js
import React, { useEffect, useState } from 'react';
import Camera from './components/Camera';
import CameraForm from './components/CamerForm';
import { getCameras, addCamera } from './services/api';

function App() {
  const [cameras, setCameras] = useState([]);

  useEffect(() => {
    fetchCameras();
  }, []);

  const fetchCameras = async () => {
    const response = await getCameras();
    const data = await response.json();
    setCameras(Object.keys(data));
  };

  const handleAddCamera = async (cameraData) => {
    await addCamera(cameraData);
    alert('Add camera')
    fetchCameras(); // Обновляем список камер после добавления
  };

  return (
    <div className="app">
      <h1>Система видеонаблюдения</h1>
      <div className="camera-grid">
      <CameraForm onSubmit={handleAddCamera} />
        {cameras.map(id => (
          <Camera key={id} cameraId={id} />
        ))}
      </div>
    </div>
  );
}

export default App;