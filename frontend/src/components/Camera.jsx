// Camera.jsx
import React, { useState } from 'react';
import { getVideoFeed } from '../services/api';

const Camera = ({ cameraId }) => {
  const [error, setError] = useState(false);

  const handleError = () => {
    setError(true);
    setTimeout(() => setError(false), 1000);
  };

  return (
    <div className="camera-card">
      <h3>Камера {cameraId}</h3>
      {error && <div className="error-banner">Нет соединения</div>}
      <img 
        src={getVideoFeed(cameraId)}
        alt={`Поток ${cameraId}`}
        onError={handleError}
      />
    </div>
  );
};

export default Camera;